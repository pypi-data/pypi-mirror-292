import logging
import operator
from typing import Annotated, TypedDict

from langchain_core.pydantic_v1 import BaseModel
from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from mtmai.models.models import ChatMessage
from mtmai.mtlibs.aiutils import lcllm_openai_chat

logger = logging.getLogger()

# Model and prompts
# Define model and prompts we will use
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


class OverallState(TypedDict):
    topic: str
    subjects: list
    jokes: Annotated[list, operator.add]
    best_selected_joke: str


# This will be the state of the node that we will "map" all
# subjects to in order to generate a joke
class JokeState(TypedDict):
    subject: str


# This is the function we will use to generate the subjects of the jokes
def generate_topics(state: OverallState):
    llm = lcllm_openai_chat("")

    prompt = subjects_prompt.format(topic=state["topic"])
    response = llm.with_structured_output(Subjects).invoke(prompt)
    return {"subjects": response.subjects}


# Here we generate a joke, given a subject
def generate_joke(state: JokeState):
    llm = lcllm_openai_chat("")
    prompt = joke_prompt.format(subject=state["subject"])
    response = llm.with_structured_output(Joke).invoke(prompt)
    return {"jokes": [response.joke]}


# Here we define the logic to map out over the generated subjects
# We will use this an edge in the graph
def continue_to_jokes(state: OverallState):
    # We will return a list of `Send` objects
    # Each `Send` object consists of the name of a node in the graph
    # as well as the state to send to that node
    return [Send("generate_joke", {"subject": s}) for s in state["subjects"]]


# Here we will judge the best joke
def best_joke(state: OverallState):
    llm = lcllm_openai_chat("")

    jokes = "\n\n".join(state["jokes"])
    prompt = best_joke_prompt.format(topic=state["topic"], jokes=jokes)
    response = llm.with_structured_output(BestJoke).invoke(prompt)

    idx = response.id

    # Ensure idx is within the bounds of the jokes list
    if idx >= len(state["jokes"]):
        idx = len(state["jokes"]) - 1

    # 返回 idx 值，必须在 state["jokes"]列表长度内，防止出错
    return {"best_selected_joke": state["jokes"][idx]}


class JokeAgent:
    @property
    def name():
        return "joke"

    @property
    def info(self):
        return {"name": "joke-agent"}

    def get_workflow(self) -> CompiledStateGraph:
        graph = StateGraph(OverallState)
        graph.add_node("generate_topics", generate_topics)
        graph.add_node("generate_joke", generate_joke)
        graph.add_node("best_joke", best_joke)
        graph.add_edge(START, "generate_topics")
        graph.add_conditional_edges(
            "generate_topics", continue_to_jokes, ["generate_joke"]
        )
        graph.add_edge("generate_joke", "best_joke")
        graph.add_edge("best_joke", END)
        app = graph.compile()
        return app

    def handle_chat_messages(self, messages: list[ChatMessage]):
        try:
            logger.info("JokeAgent handle Message %s", messages)

            latest_message = messages[-1]
            wf = self.get_workflow()
            result = wf.invoke(input={"topic": latest_message.content})
            logger.info("joke 运行结束 %s", result)
        except Exception as e:
            logger.error("调用智能体 joke 出错 %s", e)
