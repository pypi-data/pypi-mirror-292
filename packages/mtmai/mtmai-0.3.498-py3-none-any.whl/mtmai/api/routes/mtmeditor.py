import json
import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from langchain.agents import (
    AgentExecutor,
    create_openai_tools_agent,
)
from langchain.pydantic_v1 import BaseModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from opentelemetry import trace
from pydantic import BaseModel

from mtmai.llm.llm import get_fast_llm

tracer = trace.get_tracer_provider().get_tracer(__name__)
logger = logging.getLogger()


router = APIRouter()


class MtmEditorReq(BaseModel):
    option: str
    prompt: str


def example_stream():
    yield '0: "hello"\n\n'
    # yield "0: word\n\n"
    # yield "[DONE]\n\n"
    yield ""


async def exec_agent():
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant"),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )
    llm = get_fast_llm()
    tools = []
    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    async for event in agent_executor.astream_events(
        {"input": "where is the cat hiding? what items are in that location?"},
        version="v1",
    ):
        kind = event["event"]
        if kind == "on_chain_start":
            if (
                event["name"] == "Agent"
            ):  # Was assigned when creating the agent with `.with_config({"run_name": "Agent"})`
                print(
                    f"Starting agent: {event['name']} with input: {event['data'].get('input')}"
                )
        elif kind == "on_chain_end":  # noqa: SIM102
            if (
                event["name"] == "Agent"
            ):  # Was assigned when creating the agent with `.with_config({"run_name": "Agent"})`
                print()
                print("--")
                print(
                    f"Done agent: {event['name']} with output: {event['data'].get('output')['output']}"
                )
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                # Empty content in the context of OpenAI means
                # that the model is asking for a tool to be invoked.
                # So we only print non-empty content
                print(content, end="|")
                yield f"0: {json.dumps(content)}\n\n"
        elif kind == "on_tool_start":
            print("--")
            print(
                f"Starting tool: {event['name']} with inputs: {event['data'].get('input')}"
            )
        elif kind == "on_tool_end":
            print(f"Done tool: {event['name']}")
            print(f"Tool output was: {event['data'].get('output')}")
            print("--")


@router.post("")
async def input(req: MtmEditorReq):
    return StreamingResponse(
        exec_agent(),
        media_type="text/event-stream",
    )
