import json
import logging
import pprint
import random
import time
from collections.abc import AsyncIterator, Generator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langchain_core.messages import AIMessageChunk
    from langchain_core.runnables.config import RunnableConfig

import openai
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from json_repair import repair_json
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.state import CompiledStateGraph
from langsmith.wrappers import wrap_openai
from openai import Stream
from openai.types.chat.chat_completion_chunk import (
    ChatCompletionChunk,
    Choice,
    ChoiceDelta,
)
from openai.types.chat.completion_create_params import CompletionCreateParams
from opentelemetry import trace
from pydantic import BaseModel

from mtmai.mtlibs import mtutils

logger = logging.getLogger()
tracer = trace.get_tracer_provider().get_tracer(__name__)


def repaire_json(json_like_input: str):
    """修复llm json 输出的json
    原因: 有些性能不太高的语言模型输出json字符串的时候, 会附带一些不规范的格式，导致字符串像json 但却不是严格意义的json字符串
    """
    good_json_string = repair_json(json_like_input, skip_json_loads=True)
    return good_json_string


def chat_complations_stream_text(response: Stream[ChatCompletionChunk]):
    """
    兼容 vercel ai sdk
    等同于 nextjs /api/chat/route.ts 中的:
        return await streamText({
            model: getAiModalDefault(),
            messages,
        }).toDataStreamResponse();
    """
    for chunk in response:
        if not chunk.choices[0].finish_reason:
            if chunk.choices[0].delta.content:
                yield f'{chunk.choices[0].index}: "{chunk.choices[0].delta.content}"\n'
                # yield f"data: {json.dumps(chunk2)}\n"
        else:
            # 结束
            final_chunk = {
                "id": chunk.id,
                "object": chunk.object,
                "created": chunk.created,
                "model": chunk.model,
                "finishReason": chunk.choices[0].finish_reason,
                "usage": jsonable_encoder(chunk.usage),
            }
            yield f"d: {json.dumps(final_chunk)}\n"
            # 明确的结束符
            yield "[DONE]\n"


# defaultModel = "groq/llama3-8b-8192"
# default_model = "groq/llama3-groq-70b-8192-tool-use-preview"
groq_tokens = [
    "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",
]

# TOGETHER_API_KEY="b135fd4bed9be2a988e0376d1bb0977fcb8b6a88ec9f35da8138fa49eb9a0d50"


def get_groq_api_token():
    return random.choice(groq_tokens)  # noqa: S311


def _get_api_base(model_name: str):
    # if provider == "groq":
    #     return "https://api.groq.com/openai/v1"
    # if provider == "together":
    #     return "https://api.together.xyz/v1"
    # if provider == "workerai":
    #     CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    #     return f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/v1"
    # raise Exception("未知的provider:" + provider)
    return "https://api.groq.com/openai/v1"


def get_target_model_name(model_name: str):
    # if model_name.startswith("groq/"):
    #     return model_name[5:]
    # return model_name
    # return get_default_model_name()

    # return "llama3-groq-70b-8192-tool-use-preview"
    return "llama3-groq-8b-8192-tool-use-preview"


def get_default_openai_client(model_name: str = ""):
    """获取默认的 跟 openai 兼容的 ai 客户端."""
    # provider_name = model.split("/")[0]
    # api_url = get_api_base(provider_name)
    openai_client = None
    # api_key = (
    #     "b135fd4bed9be2a988e0376d1bb0977fcb8b6a88ec9f35da8138fa49eb9a0d50"  # together
    # )
    api_key = _get_api_key(model_name)
    base_url = _get_api_base(model_name)
    # model = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
    openai_client = openai.Client(
        base_url=base_url,
        api_key=api_key,
    )
    return wrap_openai(openai_client)


def _get_api_key(model_name: str):  # noqa: ARG001
    # key = random.choice(groq_tokens)
    # print("api key %s", key)
    # together_api_key = (
    #     "10747773f9883cf150558aca1b0dda81af4237916b03d207b8ce645edb40a546"
    # )
    # return together_api_key

    groq_key = "gsk_XncA6chwBwxwteYwui6DWGdyb3FYVhssnvzYourlKaZWHkYnTWye"
    return groq_key


async def llm_call(request: CompletionCreateParams):
    client = get_default_openai_client(request.model)
    return client.chat.completions.create(
        model=get_target_model_name(request.model),
        messages=request.messages,
        temperature=request.temperature,
        max_tokens=getattr(request, "max_tokens", None),
        top_p=getattr(request, "top_p", None),
        stop=getattr(request, "stop", None),
        stream=request.stream,
        # presence_penalty=getattr(request, "presence_penalty", None),
        # frequency_penalty=getattr(request, "frequency_penalty", None),
        # logit_bias=getattr(request, "logit_bias", None),
        # user=getattr(request, "user", None),
    )


def lcllm_openai_chat(model_name: str = ""):
    """获取 langchain 兼容的 openai chat 对象."""
    # Enable HTTPX logging

    # console_handler = logging.StreamHandler()
    # console_handler.setLevel(logging.DEBUG)
    # httpx_logger.addHandler(console_handler)

    with tracer.start_as_current_span("lcllm-openai-span") as span:
        base_url = "http://localhost:8333/api/v1/default"
        span.set_attribute(
            "model_name",
            model_name,
        )
        span.set_attribute(
            "base_url",
            base_url,
        )
        api_key = _get_api_key(model_name)
        base_url = _get_api_base(model_name)
        model = get_target_model_name(model_name)
        return ChatOpenAI(
            base_url=base_url,
            api_key=api_key,
            model=model,
            temperature=0.1,
            max_tokens=8000,
        )
        # return ChatOpenAI(
        #     base_url=base_url,
        #     api_key="fakekey",
        #     model="default",
        #     temperature=0.1,
        #     # max_tokens=8000,
        # )


def stream_response(stream_chunck: Stream[ChatCompletionChunk]):
    def gen_stream():
        for chunk in stream_chunck:
            pprint.pp(chunk)
            yield f"data: {json.dumps(jsonable_encoder( chunk))}\n\n"
            if chunk.choices[0].finish_reason is not None:
                yield "data: [DONE]\n"

    return StreamingResponse(gen_stream(), media_type="text/event-stream")


async def stream_text(stream: AsyncIterator[BaseMessage]):
    async for ai_message_chunk in stream:
        if ai_message_chunk.content:
            yield f"0:{json.dumps(ai_message_chunk.content)} \n"


def gen_text_stream(words: Generator[str, None]):
    """以stream 的方式向chat 输出字符串 (旧代码)"""
    for w in words:
        chat_chunk = ChatCompletionChunk(
            id=mtutils.gen_orm_id_key(),
            object="chat.completion.chunk",
            created=int(time.time()),
            model="agent",
            choices=[
                Choice(
                    index=0,
                    delta=ChoiceDelta(content=w, role="assistant", text=w),
                )
            ],
        )
        yield f"data: {json.dumps(jsonable_encoder(chat_chunk))}\n\n"


class ClientAttachment(BaseModel):
    name: str
    contentType: str
    url: str


class ToolInvocation(BaseModel):
    toolCallId: str
    toolName: str
    args: dict
    result: dict


class ClientMessage(BaseModel):
    role: str
    content: str
    experimental_attachments: list[ClientAttachment] | None = None
    toolInvocations: list[ToolInvocation] | None = None


class ClientAttachment(BaseModel):
    name: str
    contentType: str
    url: str


class ToolInvocation(BaseModel):
    toolCallId: str
    toolName: str
    args: dict
    result: dict


# class ChatRequest(BaseModel):
#     messages: list[ClientMessage]


# def stream_text(messages: list[ClientMessage], protocol: str = "data"):
#     # 源码来:  https://github.com/vercel/ai/blob/main/examples/next-fastapi/api/index.py
#     # openAIClient = get_default_openai_client()

#     # TODO messages 应该从数据库获取
#     chat_id = "chat_id123"
#     agent_chat_stream(messages, "demo", chat_id)
#     # When protocol is set to "text", you will send a stream of plain text chunks
#     # https://sdk.vercel.ai/docs/ai-sdk-ui/stream-protocol#text-stream-protocol

#     if protocol == "text":
#         for chunk in stream:
#             for choice in chunk.choices:
#                 if choice.finish_reason == "stop":
#                     break
#                 else:
#                     yield f"{choice.delta.content}"

#     # When protocol is set to "data", you will send a stream data part chunks
#     # https://sdk.vercel.ai/docs/ai-sdk-ui/stream-protocol#data-stream-protocol

#     elif protocol == "data":
#         draft_tool_calls = []
#         draft_tool_calls_index = -1

#         for chunk in stream:
#             for choice in chunk.choices:
#                 if choice.finish_reason == "stop":
#                     continue

#                 elif choice.finish_reason == "tool_calls":
#                     for tool_call in draft_tool_calls:
#                         yield '9:{{"toolCallId":"{id}","toolName":"{name}","args":{args}}}\n'.format(
#                             id=tool_call["id"],
#                             name=tool_call["name"],
#                             args=tool_call["arguments"],
#                         )

#                     for tool_call in draft_tool_calls:
#                         tool_result = available_tools[tool_call["name"]](
#                             **json.loads(tool_call["arguments"])
#                         )

#                         yield 'a:{{"toolCallId":"{id}","toolName":"{name}","args":{args},"result":{result}}}\n'.format(
#                             id=tool_call["id"],
#                             name=tool_call["name"],
#                             args=tool_call["arguments"],
#                             result=json.dumps(tool_result),
#                         )

#                 elif choice.delta.tool_calls:
#                     for tool_call in choice.delta.tool_calls:
#                         id = tool_call.id
#                         name = tool_call.function.name
#                         arguments = tool_call.function.arguments

#                         if id is not None:
#                             draft_tool_calls_index += 1
#                             draft_tool_calls.append(
#                                 {"id": id, "name": name, "arguments": ""}
#                             )

#                         else:
#                             draft_tool_calls[draft_tool_calls_index]["arguments"] += (
#                                 arguments
#                             )

#                 else:
#                     yield f'0:"{choice.delta.content}"\n'

#             if chunk.choices == []:
#                 usage = chunk.usage
#                 prompt_tokens = usage.prompt_tokens
#                 completion_tokens = usage.completion_tokens

#                 yield 'd:{{"finishReason":"{reason}","usage":{{"promptTokens":{prompt},"completionTokens":{completion}}}}}\n'.format(
#                     reason="tool-calls" if len(draft_tool_calls) > 0 else "stop",
#                     prompt=prompt_tokens,
#                     completion=completion_tokens,
#                 )


def gen_text_stream_2(words: Generator[str, None]):
    """(可能是旧代码)以stream 的方式向chat 输出字符串"""
    for w in words:
        chat_chunk = ChatCompletionChunk(
            id=mtutils.gen_orm_id_key(),
            object="chat.completion.chunk",
            created=int(time.time()),
            model="agent",
            choices=[
                Choice(
                    index=0,
                    delta=ChoiceDelta(content=w, role="assistant", text=w),
                )
            ],
        )
        yield f"data: {json.dumps(jsonable_encoder(chat_chunk))}\n\n"

    # 发送结束标志
    end_chunk = ChatCompletionChunk(
        id=mtutils.gen_orm_id_key(),
        object="chat.completion.chunk",
        created=int(time.time()),
        model="agent",
        choices=[
            Choice(
                index=0,
                delta=ChoiceDelta(content="", role="assistant"),
                finish_reason="stop",
            )
        ],
    )
    yield f"data: {json.dumps(jsonable_encoder(end_chunk))}\n\n"


def stream_text_testing(messages: list[ClientMessage], protocol: str = "data"):
    demo_message = """ValueError Traceback (most recent call last)
Cell In[32], line 1
----> 1 agent = create_sql_agent(
2 llm=llm,
3 db=db,
4 prompt=full_prompt,
5 verbose=True
6 )
173 [
174 react_prompt.PREFIX,
(...)
178 ]
179 )
180 prompt = PromptTemplate.from_template(template)
181 agent = RunnableAgent(
--> 182 runnable=create_react_agent(llm, tools, prompt),
183 input_keys_arg=["input"],
184 return_keys_arg=["output"],
185 )
187 elif agent_type == AgentType.OPENAI_FUNCTIONS:
188 if prompt is None:

93 missing_vars = {"tools", "tool_names", "agent_scratchpad"}.difference(
94 prompt.input_variables
95 )
96 if missing_vars:
---> 97 raise ValueError(f"Prompt missing required variables: {missing_vars}")
99 prompt = prompt.partial(
100 tools=render_text_description(list(tools)),
101 tool_names=", ".join([t.name for t in tools]),
102 )

ValueError: Prompt missing required variables: {'tools', 'tool_names'}"""

    if protocol == "data":
        for word in demo_message.split(" "):
            yield f"0:{json.dumps(word)} \n"
            time.sleep(0.03)

        # 返回一个范例工具调用指令
        yield '9:{{"toolCallId":"{id}","toolName":"{name}","args":{args}}}\n'.format(
            id="toolcall_" + mtutils.gen_orm_id_key(),
            name="hello_tool",
            args=json.dumps({}),
            # result=json.dumps(tool_result),
        )

        yield 'd:{{"finishReason":"{reason}","usage":{{"promptTokens":{prompt},"completionTokens":{completion}}}}}\n'.format(
            reason="tool-calls",
            prompt={},
            completion={},
        )


def convert_to_openai_messages(messages: list[ClientMessage]):
    openai_messages = []

    for message in messages:
        parts = []

        parts.append({"type": "text", "text": message.content})

        if message.experimental_attachments:
            for attachment in message.experimental_attachments:
                if attachment.contentType.startswith("image"):
                    parts.append(
                        {"type": "image_url", "image_url": {"url": attachment.url}}
                    )

                elif attachment.contentType.startswith("text"):
                    parts.append({"type": "text", "text": attachment.url})

        if message.toolInvocations:
            tool_calls = [
                {
                    "id": tool_invocation.toolCallId,
                    "type": "function",
                    "function": {
                        "name": tool_invocation.toolName,
                        "arguments": json.dumps(tool_invocation.args),
                    },
                }
                for tool_invocation in message.toolInvocations
            ]

            openai_messages.append({"role": "assistant", "tool_calls": tool_calls})

            tool_results = [
                {
                    "role": "tool",
                    "content": json.dumps(tool_invocation.result),
                    "tool_call_id": tool_invocation.toolCallId,
                }
                for tool_invocation in message.toolInvocations
            ]

            openai_messages.extend(tool_results)

            continue

        openai_messages.append({"role": message.role, "content": parts})

    return openai_messages


async def flow_events(wf: CompiledStateGraph, state, thread_id: str):
    config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
    async for event in wf.astream_events(
        input=state,
        version="v2",
        config=config,
    ):
        kind = event["event"]
        name = event["name"]
        data = event["data"]
        if kind == "on_chat_model_stream":
            data_chunk: AIMessageChunk = event["data"]["chunk"]
            content = data_chunk.content
            yield f"0: {json.dumps(content)} \n\n"
        print(f"astream_event: kind: {kind}, name={name},{data}")

        if kind == "on_chain_end" and name == "LangGraph":
            # 完全结束可以拿到最终数据
            yield f"2: {json.dumps(jsonable_encoder(data))}\n"

    print(f"flow 结束, {thread_id}")
