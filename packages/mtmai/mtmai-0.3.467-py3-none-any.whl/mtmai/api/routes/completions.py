import json
import logging
from typing import TYPE_CHECKING

import fastapi
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from langsmith import traceable
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from openai.types.chat.completion_create_params import (
    CompletionCreateParamsBase,
    CompletionCreateParamsStreaming,
)
from opentelemetry import trace
from sqlmodel import Session

from mtmai.agents.chatbot_agent import chatbot_agent
from mtmai.agents.langgraph_crew import graph
from mtmai.api.routes.chat_input import get_chatinput_byid
from mtmai.core.config import settings
from mtmai.core.db import getdb
from mtmai.models.models import ChatInput, ChatMessage
from mtmai.mtlibs import mtutils

if TYPE_CHECKING:
    from langchain_core.messages import AIMessage


router = APIRouter()
logger = logging.getLogger()
tracer = trace.get_tracer_provider().get_tracer(__name__)


def register_api_router(app: fastapi.FastAPI):
    app.include_router(router)


async def chat_crewdemo(query: str):
    yield '0:"app starting..." \n'
    app = graph.WorkFlow().app
    app.invoke({"emails": ["email1"]})
    yield '0:"app finished." \n'


async def chat_simplepost(input: str):
    from mtmai.teams.simple_post import simple_post

    yield '0:"simplepost starting..." \n'
    crew = simple_post.SimplePostCrew({"topic": input})
    result = await crew.run()
    yield f'0:"{result}" \n'


# async def chat_landing_page(input: str):
#     from mtmai.teams.landing_page import landing_page

#     yield '0:"landing_page starting..." \n\n'
#     crew = landing_page.LandingPageCrew(input)
#     crew.run()
#     yield '0:"landing_page finished." \n\n'


async def agent_chat_stream(
    chat_messages: list[ChatCompletionMessageParam],
    agent_name: str = "demo",
    chat_id: str | None = None,
):
    lastest_message = chat_messages[-1]
    lastest_conent = lastest_message.get("content")
    if lastest_message.get("role") == "user" and lastest_conent.startswith("/"):
        command = lastest_message.get("content")[1:]
        logger.debug("是命令请求 %s", command)
        if command == "help":
            yield '9:{{"toolCallId":"{id}","toolName":"{name}","args":{args}}}\n'.format(
                id="toolcall_" + mtutils.gen_orm_id_key(),
                name="show_help",
                args=json.dumps({}),
            )
        # elif command == "state":
        #     yield '9:{{"toolCallId":"{id}","toolName":"{name}","args":{args}}}\n'.format(
        #         id="toolcall_" + mtutils.nano_gen(),
        #         name="state",
        #         args=json.dumps({}),
        #     )
        return
    chat_input_item = await get_chatinput_byid(chat_id)
    if not chat_input_item:
        chat_input_item = ChatInput()
        # ensure_thread_id(chat_input_item)
        chat_input_item.status = "new"
        chat_input_item.agent_id = agent_name

        new_message = ChatMessage(
            content=lastest_message.get("content"),
            chat=chat_input_item,
            role=lastest_message.get("role"),
        )
        chat_input_item.messages.append(new_message)

        with Session(getdb()) as session:
            session.add(chat_input_item)
            session.commit()
            session.refresh(chat_input_item)

        logger.info("创建新的对话记录 %s", chat_input_item.id)

        yield '9:{{"toolCallId":"{id}","toolName":"{name}","args":{args}}}\n'.format(
            id="toolcall_" + mtutils.gen_orm_id_key(),
            name="setState",
            args=json.dumps({"chatId": chat_input_item.id}),
        )
    # add chat message
    new_message = ChatMessage(
        content=lastest_message.get("content"),
        chat_id=chat_id,
        role=lastest_message.get("role"),
    )
    with Session(getdb()) as session:
        session.add(new_message)
        session.commit()
        session.refresh(new_message)

    # if chat_input_item.agent_id == "researcher":
    #     async for a in chat_researcher(lastest_conent):
    #         yield a
    if chat_input_item.agent_id == "crew_demo":
        async for a in chat_crewdemo(lastest_conent):
            yield a
    if chat_input_item.agent_id == "langdingpage":
        async for a in chat_landing_page(lastest_conent):
            yield a
    if chat_input_item.agent_id == "simplepost":
        async for a in chat_simplepost(lastest_conent):
            yield a

    if chat_input_item.agent_id == "chatbot_agent":
        agent_executor = await chatbot_agent(chat_messages, chat_id=chat_id)

        async for event in agent_executor.astream_events(
            {
                "chat_history": chat_messages,
                #         # "input": "what's items are located where the cat is hiding?",
            },
            version="v1",
        ):
            kind = event["event"]
            if kind == "on_chain_start":
                if (
                    event["name"] == "Agent"
                ):  # Was assigned when creating the agent with `.with_config({"run_name": "Agent"})`
                    print(
                        f"(chatbot_agent)Starting agent: {event['name']} with input: {event['data'].get('input')}"
                    )
            elif kind == "on_chain_end":  # noqa: SIM102
                if (
                    event["name"] == "Agent"
                ):  # Was assigned when creating the agent with `.with_config({"run_name": "Agent"})`
                    # add chat message
                    ai_content = event["data"].get("output")
                    messages: list[AIMessage] = ai_content.get("messages")
                    for msg in messages:
                        new_message = ChatMessage(
                            id=msg.id,
                            content=msg.content,
                            chat_id=chat_id,
                            role="assistant",
                        )
                        with Session(getdb()) as session:
                            session.add(new_message)
                            session.commit()
                            session.refresh(new_message)
                    print(
                        f"Done agent: {event['name']} with output: {event['data'].get('output')['output']}"
                    )
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    yield f"0:{json.dumps(content)} \n"
            elif kind == "on_tool_start":
                print(
                    f"Starting tool: {event['name']} with inputs: {event['data'].get('input')}"
                )
            elif kind == "on_tool_end":
                ai_content = event["data"].get("output")
                print(f"Tool output was: {ai_content}")
        # async for stream_item in chatbot_agent(chat_messages, chat_id=chat_id):
        #     yield stream_item
        return

    # if chat_input_item.agent_id == "demo":
    #     # 旧版基于 langgraph 的聊天方式
    #     team = await get_agent(chat_input_item.model)
    #     logger.info("chat input 状态 %s", chat_input_item.status)
    #     messages = list(chat_messages)
    #     chat_input_item.status = StatusEnum.RUNNING.value
    #     with Session(getdb()) as session:
    #         session.merge(chat_input_item)
    #         session.commit()

    #     flow_input = None
    #     if messages is not None:
    #         flow_input = {"messages": messages}

    #     events = team.astream_events(
    #         flow_input,
    #         version="v2",
    #         config=chat_input_item.config,
    #     )
    #     async for event in events:
    #         kind = event["event"]
    #         # logger.info("event %s", kind)
    #         # yield f"0:{json.dumps(kind)} \n"
    #         if kind == "on_chat_model_stream":
    #             data_chunk: AIMessageChunk = event["data"]["chunk"]
    #             # print("dataChunk:")
    #             # pprint.pprint(data_chunk)
    #             # print("=======================================================")
    #             content = data_chunk.content
    #             if content:
    #                 yield f"0:{json.dumps(content)} \n"
    #             # chat_chunk = ChatCompletionChunk(
    #             #     id=mtutils.nano_gen(),
    #             #     object="chat.completion.chunk",
    #             #     created=int(time.time()),
    #             #     model="agent",
    #             #     choices=[
    #             #         Choice(
    #             #             index=0,
    #             #             delta=ChoiceDelta(
    #             #                 content=content,
    #             #                 role="assistant",
    #             #                 text=content,
    #             #                 tool_calls=[tool_call_choice],
    #             #             ),
    #             #         )
    #             #     ],
    #             # )
    #             # yield f"data: {json.dumps(jsonable_encoder(chat_chunk))}\n\n"
    #             # if data_chunk.additional_kwargs:
    #             #     chunck2 =
    #         # elif kind == "on_chain_start":
    #         #     yield '9:{{"toolCallId":"{id}","toolName":"{name}","args":{args}}}\n'.format(
    #         #         id="toolcall_" + mtutils.nano_gen(),
    #         #         name="setChatId",
    #         #         args=json.dumps(
    #         #             {
    #         #                 "chatId": "fakeChatId",
    #         #             }
    #         #         ),
    #         #         # result=json.dumps(tool_result),
    #         #     )
    #         elif kind == "on_tool_start":
    #             # for chunk1 in gen_text_stream("**on_tool_start**\n\n"):
    #             #     yield chunk1
    #             print(
    #                 f"Starting tool: {event['name']} with inputs: {event['data'].get('input')}"
    #             )
    #         elif kind == "on_tool_end":
    #             # for chunk1 in gen_text_stream("**on_tool_end**\n\n"):
    #             #     yield chunk1
    #             print(
    #                 f"Done tool: {event['name']}, Tool output was: {event['data'].get('output')}"
    #             )
    #         # elif kind == "on_chat_model_start":
    #         #     for chunk1 in gen_text_stream("**on_chat_model_start**\n\n"):
    #         #         yield chunk1
    #         # else:
    #         #     for chunk1 in gen_text_stream(f"**{kind}**\n\n"):
    #         #         yield chunk1

    #     config: RunnableConfig = chat_input_item.config
    #     graph_flow = await get_agent(chat_input_item.model)
    #     state_snapshot = await graph_flow.aget_state(chat_input_item.config)

    #     thread_id = config["configurable"]["thread_id"]
    #     state_log = f".logs/teams/{chat_input_item.id}/{thread_id}.json"

    # await mtutils.write_file(
    #     state_log,
    #     json.dumps(
    #         jsonable_encoder(
    #             {
    #                 "state": state_snapshot,
    #                 # "events": results,
    #             }
    #         ),
    #         indent=2,
    #         ensure_ascii=False,
    #     ),
    # )

    # logger.info(
    #     'log: "%s"',
    #     state_log,
    # )

    # yield 'd:{{"finishReason":"{reason}","usage":{{"promptTokens":{prompt},"completionTokens":{completion}}}}}\n'.format(
    #     reason="tool-calls",
    #     prompt={},
    #     completion={},
    # )


@traceable
@router.post(settings.API_V1_STR + "/chat/completions")
async def chat_completions(request: Request):
    is_chat = request.headers.get("Is-Chat")
    agent_name = request.headers.get("Chat-Agent", "demo")
    chat_id = request.headers.get("Chat-Id", "new")

    if is_chat is None:
        # openai /vi/chat/completionss 官方兼容
        # 这里的功能未 完全实现, 以后慢慢修改
        try:
            req = await request.json()
            logger.info("api completions %s", req)
            chat_id = "75ced3bca3794f86"
            cc: CompletionCreateParamsBase = None
            # if req["stream"]:
            cc = CompletionCreateParamsStreaming(**req)
            return StreamingResponse(
                agent_chat_stream(cc["messages"], "demo", chat_id),
                media_type="text/event-stream",
            )
        except Exception as e:
            logger.exception("get_response_openai Error: %s", e)  # noqa: TRY401
            raise HTTPException(503)

    # chat_request = ChatRequest(**await request.json())
    # vercel ai sdk stream 协议
    # 协议: https://sdk.vercel.ai/docs/ai-sdk-ui/stream-protocol#data-stream-protocol
    # 参考: https://github.com/vercel/ai/blob/main/examples/next-fastapi/api/index.py
    # protocol = "data"  # data or text

    # if request.headers.get("Is-Testing") == "1":
    #     response = StreamingResponse(
    #         stream_text_testing(
    #             convert_to_openai_messages(chat_request.messages), protocol="data"
    #         )
    #     )
    # else:
    #     cc = CompletionCreateParamsStreaming(**await request.json())
    #     response = response = StreamingResponse(
    #         agent_chat_stream(cc["messages"], agent_name, chat_id=chat_id)
    #     )
    # response.headers["x-vercel-ai-data-stream"] = "v1"
    # return response
    return "todo "
