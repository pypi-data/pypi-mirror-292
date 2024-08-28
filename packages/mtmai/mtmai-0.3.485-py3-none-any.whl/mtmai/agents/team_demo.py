import logging
from typing import Literal

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from mtmai.mtlibs.langgraph import get_langgraph_checkpointer
from mtmai.teams.graph_state import State
from mtmai.teams.tools_node import tools_node
from mtmai.teams.weather_node import weather_node

logger = logging.getLogger()


def should_continue(state: State) -> Literal["__end__", "tools", "continue"]:
    messages = state["messages"]
    last_message = messages[-1]

    # if state.get("ask_human"):
    #     return "human"

    # if last_message.tool_calls:
    #     return "tools"
    if not last_message.tool_calls:
        return "end"
    # Otherwise if there is, we continue
    else:
        return "continue"


def get_my_demo_team() -> CompiledStateGraph:
    workflow = StateGraph(State)
    workflow.add_node("agent", weather_node)
    workflow.add_node("tools", tools_node())

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            # If `tools`, then we call the tool node.
            "continue": "tools",
            # Otherwise we finish.
            "end": END,
        },
    )
    workflow.add_edge("tools", "agent")
    graph = workflow.compile(
        checkpointer=get_langgraph_checkpointer(),
        # interrupt_before=["tool"],
    )
    return graph
