import logging
from functools import lru_cache

import fastapi
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from langgraph.graph.state import CompiledStateGraph
from sqlmodel import Session, select

from mtmai.agents.joke_agent import JokeAgent
from mtmai.api.routes.chat_input import ChatInputReq
from mtmai.core.config import settings
from mtmai.core.db import get_session
from mtmai.models.models import Agent, ChatInput, ChatMessage
from mtmai.mtlibs import mtutils

router = APIRouter()

logger = logging.getLogger()


def register_api_router(app: fastapi.FastAPI):
    app.include_router(router)


graphs: dict[str, CompiledStateGraph] = {}


# @router.get(settings.api_prefix + "/agent/{agent_id}/graph.png")
# async def get_graph_image(
#     *,
#     db: Session = Depends(get_session),
#     agent_id: str,
# ):
#     agent = get_agent_by_id(db, agent_id)
#     if not agent:
#         raise HTTPException(status_code=404, detail="Agent not found")
#     agent_graph = get_agent_graph(agent.id)
#     if not agent_graph:
#         raise HTTPException(status_code=404, detail="agent graph not found")
#     image_data = agent_graph.get_graph(xray=1).draw_mermaid_png()
#     return Response(content=image_data, media_type="image/png")


# def get_graph(agent: Agent):
#     return get_agent_graph(agent.id)


@router.get(settings.API_V1_STR + "/agent/{agent_id}")
async def get_agent(
    *,
    db: Session = Depends(get_session),
    agent_id: str,
):
    # 新版
    agent_instance = get_agent_instance(agent_id)
    if agent_instance:
        return agent_instance.info
    # 旧版
    agent = db.exec(select(Agent).where(Agent.id == agent_id)).one()
    return agent


async def get_agent_from_headers(chat_agent: str = Header(None)):
    return chat_agent


def ensure_thread_id(input: ChatInput):
    if not input.config:
        input.config = {}

    if not input.config.get("configurable"):
        input.config["configurable"] = {}
    if not input.config["configurable"].get("thread_id"):
        input.config["configurable"]["thread_id"] = mtutils.gen_orm_id_key()
    if not input.config["configurable"].get("chat_id"):
        input.config["configurable"]["chat_id"] = input.id
    return input


def get_agent_by_id(db: Session, agent_id: str):
    return db.exec(select(Agent).where(Agent.id == agent_id)).one()


@router.post(settings.API_V1_STR + "/agent/chat")
async def agent_chat(
    *,
    db: Session = Depends(get_session),
    agent_id: str = Depends(get_agent_from_headers),
    chat_input_req: ChatInputReq,
):
    latest_message = chat_input_req.messages[-1]
    agent_instance = get_agent_instance(agent_id)
    if agent_instance:
        agent_instance.handle_chat_messages(chat_input_req.messages)
    else:
        agent = get_agent_by_id(db, agent_id)
        chat_id = chat_input_req.chat_id

        if not agent:
            msg = f"missing agent {agent_id}"
            raise Exception(msg)  # noqa: TRY002
        if not chat_id:
            # 新的对话
            try:
                logger.info("new conversation %s", chat_input_req)
                chat_input = ChatInput(agent_id=agent_id)
                ensure_thread_id(chat_input)
                db.add(chat_input)
                db.commit()
                db.refresh(chat_input)
            except Exception as e:
                logger.exception("get_response_openai Error: %s", e)
                raise HTTPException(503)
        else:
            # 现有的对话
            chat_input = db.exec(select(ChatInput).where(ChatInput.id == chat_id)).one()
            if not chat_input:
                msg = "missing conversation id: %s"
                raise Exception(msg, chat_id)  # noqa: TRY002

        new_message = ChatMessage(
            content=latest_message.content,
            chat_id=chat_input.id,
            role=latest_message.role,
        )
        db.add(new_message)
        db.commit()
        ## 调用模型获取输出
        # response = response = StreamingResponse(
        #     agent_chat_inner(db=db, chat_id=chat_input.id)
        # )
        # response.headers["x-vercel-ai-data-stream"] = "v1"
        # return response
        return "todo?"


# async def agent_chat_inner(*, db: Session, chat_id: str):
#     """调用模型获取输出"""
#     # yield '0:"app starting..." \n'

#     chat_input = db.exec(select(ChatInput).where(ChatInput.id == chat_id)).one()
#     if not chat_input:
#         msg = "missing conversation id: %s"
#         raise Exception(msg, chat_id)

#     agent = get_agent_by_id(db, chat_input.agent_id)
#     app = get_graph(agent)
#     config: RunnableConfig = chat_input.config
#     latest_message = chat_input.messages[-1]
#     async for event in app.astream_events(
#         {"messages": [latest_message.content]},
#         version="v2",
#         config=config,
#     ):
#         kind = event["event"]
#         if kind == "on_chat_model_stream":
#             data_chunk: AIMessageChunk = event["data"]["chunk"]
#             content = data_chunk.content
#             yield f"0:{json.dumps(content)}\n"


# @router.get(API_PREFIX + "/flow/{team_id}/state/{thread_id}")
# async def get_flow_state(team_id: str, thread_id: str):
#     graph_flow = await get_agent(team_id)

#     runable_config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
#     state_history = graph_flow.aget_state_history(runable_config)

#     results = []
#     async for state in state_history:
#         print(state)
#         print("--")
#         results.append(state)

#     return results


# def get_agent_graph(agent_id: str):
#     global graphs
#     cache_item = graphs.get(agent_id)
#     if cache_item is not None:
#         return cache_item

#     if agent_id == "demo":
#         graphs[agent_id] = get_my_demo_team()
#         return graphs[agent_id]
#     if agent_id == "joke":
#         # graphs[agent_id] = flow_demo_mapredure()
#         # return graphs[agent_id]
#         joke_agent = JokeAgent()
#     if agent_id == "demo_subgraph":
#         graphs[agent_id] = flow_demo_subgraph()
#         return graphs[agent_id]


@lru_cache
def get_agent_instance(agent_id: str):
    if agent_id == "joke":
        agent_instance = JokeAgent()
        return agent_instance
    return None


@router.get(settings.API_V1_STR + "/agent", response_model=list[Agent])
def get_agents(
    *,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    session: Session = Depends(get_session),
):
    statement = select(Agent).offset(offset).limit(limit)
    results = session.exec(statement).all()
    return results
