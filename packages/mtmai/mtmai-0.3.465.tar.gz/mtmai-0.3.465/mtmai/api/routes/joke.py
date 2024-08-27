import logging
import operator
from collections.abc import Sequence
from functools import lru_cache
from typing import Annotated

from fastapi import APIRouter, Response
from fastapi.responses import StreamingResponse
from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel

from mtmai.core.config import settings
from mtmai.models.models import AgentMeta, ChatMessage
from mtmai.mtlibs import mtutils
from mtmai.mtlibs.aiutils import flow_events, lcllm_openai_chat

logger = logging.getLogger()

router = APIRouter()

subjects_prompt = """Generate a comma separated list of between 2 and 5 examples related to: {topic}."""
joke_prompt = """Generate a joke about {subject}"""
best_joke_prompt = """Below are a bunch of jokes about {topic}. Select the best one! Return the ID of the best one.

{jokes}"""


class Subjects(BaseModel):
    subjects: list[str]


class Joke(BaseModel):
    joke: str


class BestJoke(BaseModel):
    id: int


class JokeAgentState(BaseModel):
    # id: str = Field(default_factory=mtutils.nano_gen, primary_key=True)
    # topic: str | None = None
    # subjects: list | None = []
    # subjects: list[str] | None = Field(sa_column=Column(JSON))
    subjects: list[str] | None = None
    # jokes: Annotated[Sequence[str], operator.add] = []
    jokes: Annotated[Sequence[str], operator.add] | None = (
        None  # = Field(sa_column=Column(JSON))
    )
    best_selected_joke: str | None = None
    # messages: Annotated[list, add_messages] = Field(sa_column=Column(JSON))
    messages: list[dict] | None = None  # = Field(sa_column=Column(JSON))
    ask_human: bool = False


# This will be the state of the node that we will "map" all
# subjects to in order to generate a joke
class JokeState(BaseModel):
    subject: str


# This is the function we will use to generate the subjects of the jokes
def generate_topics(state: JokeAgentState):
    llm = lcllm_openai_chat("")

    latest_message = state.messages[-1]
    prompt = subjects_prompt.format(topic=latest_message["content"])
    response = llm.with_structured_output(Subjects).invoke(prompt)
    state.subjects = response.subjects
    # return {"subjects": response.subjects}
    return state


# Here we generate a joke, given a subject
def generate_joke(state: JokeState):
    llm = lcllm_openai_chat("")
    prompt = joke_prompt.format(subject=state.subject)
    response = llm.with_structured_output(Joke).invoke(prompt)
    # state.jokes = [response.joke]
    return {"jokes": [response.joke]}
    # return state


# Here we define the logic to map out over the generated subjects
# We will use this an edge in the graph
def continue_to_jokes(state: JokeAgentState):
    # We will return a list of `Send` objects
    # Each `Send` object consists of the name of a node in the graph
    # as well as the state to send to that node
    send_list = []
    for s in state.subjects:
        joke_state = JokeState(
            subject=s,
        )
        send_list.append(Send("generate_joke", joke_state))
    # return [Send("generate_joke", ) for JokeAgentState(subjects=s) in state.subjects]
    return send_list


# Here we will judge the best joke
def best_joke(state: JokeAgentState):
    llm = lcllm_openai_chat("")

    jokes = "\n\n".join(state.jokes)
    latest_message = state.messages[-1]

    prompt = best_joke_prompt.format(topic=latest_message["content"], jokes=jokes)
    response = llm.with_structured_output(BestJoke).invoke(prompt)

    idx = response.id

    # Ensure idx is within the bounds of the jokes list
    if idx >= len(state.jokes):
        idx = len(state.jokes) - 1

    return {"best_selected_joke": state.jokes[idx]}


@lru_cache
def get_workflow() -> CompiledStateGraph:
    graph = StateGraph(JokeAgentState)
    graph.add_node("generate_topics", generate_topics)
    graph.add_node("generate_joke", generate_joke)
    graph.add_node("best_joke", best_joke)
    graph.add_edge(START, "generate_topics")
    graph.add_conditional_edges("generate_topics", continue_to_jokes, ["generate_joke"])
    graph.add_edge("generate_joke", "best_joke")
    graph.add_edge("best_joke", END)
    app = graph.compile()
    return app


@router.get("", tags=["joke"], response_model=AgentMeta)
async def info():
    return AgentMeta(
        name="joke",
        chat_url=settings.API_V1_STR + "/joke/chat",
        can_chat=False,
        agent_type="graphq",
        graph_image=settings.API_V1_STR + "/joke//image",
    )


# async def flow_events(wf: CompiledStateGraph, state: JokeAgentState, thread_id: str):
#     config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
#     async for event in wf.astream_events(
#         input=state,
#         version="v2",
#         config=config,
#     ):
#         kind = event["event"]
#         name = event["name"]
#         data = event["data"]
#         if kind == "on_chat_model_stream":
#             data_chunk: AIMessageChunk = event["data"]["chunk"]
#             content = data_chunk.content
#             yield f"0: {json.dumps(content)} \n\n"
#         print(f"astream_event: kind: {kind}, name={name},{data}")

#         if kind == "on_chain_end" and name == "LangGraph":
#             # 完全结束可以拿到最终数据
#             yield f"2: {json.dumps(jsonable_encoder(data))}\n"

#     print(f"flow 结束, {thread_id}")


@router.post("/chat", tags=["joke"], response_model=JokeAgentState | None)
async def chat(messages: list[ChatMessage]):
    logger.info("JokeAgent handle Message %s", messages)

    latest_message = messages[-1]
    wf = get_workflow()

    state = JokeAgentState(
        messages=[{"role": "user", "content": latest_message.content}]
    )

    thread_id = mtutils.gen_orm_id_key()

    response = response = StreamingResponse(
        flow_events(wf=wf, state=state, thread_id=thread_id)
    )
    response.headers["x-vercel-ai-data-stream"] = "v1"
    return response


@router.get("/state", tags=["joke"], response_model=JokeAgentState | None)
async def state():
    wf = get_workflow()
    return {"message": "TODO: show graphql state"}


@router.get("/image", tags=["joke"])
async def image():
    wf = get_workflow()
    image_data = wf.get_graph(xray=1).draw_mermaid_png()
    return Response(content=image_data, media_type="image/png")
