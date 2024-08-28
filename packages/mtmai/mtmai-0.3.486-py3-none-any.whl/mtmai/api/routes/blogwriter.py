import json
import logging
from typing import TYPE_CHECKING

from fastapi import APIRouter, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from langgraph.graph.state import CompiledStateGraph

from mtmai.core.config import settings
from mtmai.models.models import AgentMeta, ChatMessage
from mtmai.mtlibs import mtutils

if TYPE_CHECKING:
    from langchain_core.messages import AIMessageChunk
    from langchain_core.runnables.config import RunnableConfig

from mtmai.teams import blog_writer_node

logger = logging.getLogger()

router = APIRouter()


@router.get("", tags=["blogwriter"], response_model=AgentMeta)
async def meta():
    return AgentMeta(
        name="joke",
        chat_url=settings.API_V1_STR + "/blogwriter/chat",
        can_chat=False,
        agent_type="graphq",
        graph_image=settings.API_V1_STR + "/blogwriter/image",
    )


async def flow_events(
    wf: CompiledStateGraph, state: blog_writer_node.BlogWriterAgentState, thread_id: str
):
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


@router.post(
    "/chat", tags=["joke"], response_model=blog_writer_node.BlogWriterAgentState | None
)
async def joke_agent_chat(messages: list[ChatMessage]):
    try:
        logger.info("JokeAgent handle Message %s", messages)

        latest_message = messages[-1]
        wf = blog_writer_node.get_workflow()

        state = blog_writer_node.BlogWriterAgentState(
            messages=[{"role": "user", "content": latest_message.content}]
        )

        thread_id = mtutils.gen_orm_id_key()

        response = response = StreamingResponse(
            flow_events(wf=wf, state=state, thread_id=thread_id)
        )
        response.headers["x-vercel-ai-data-stream"] = "v1"
        return response
    except Exception as e:
        logger.exception("调用智能体 joke 出错 %s", e)
    return None


@router.get(
    "/state", tags=["joke"], response_model=blog_writer_node.BlogWriterAgentState | None
)
async def get_joke_agent_state():
    wf = blog_writer_node.get_workflow()
    return {"message": "TODO: show graphql state"}


@router.get("/image", tags=["joke"])
async def joke_agent_image():
    wf = blog_writer_node.get_workflow()
    image_data = wf.get_graph(xray=1).draw_mermaid_png()
    return Response(content=image_data, media_type="image/png")
