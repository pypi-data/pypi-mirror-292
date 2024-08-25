import logging
from typing import Literal

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from mtmai.mtlibs.langgraph import get_langgraph_checkpointer
from mtmai.teams.graph_state import ReturnNodeValue, State
from mtmai.teams.tools_node import tools_node
from mtmai.teams.weather_node import weather_node

logger = logging.getLogger()


# Define the function that determines whether to continue or not
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
    # tools = []

    workflow = StateGraph(State)
    # graph_builder.add_node("agent", call_model)
    # graph_builder.add_node("action", tool_node)

    # # Set the entrypoint as `agent`
    # # This means that this node is the first one called
    # graph_builder.add_edge(START, "agent")
    # graph_builder.add_node("chatbot", chatbot_node)
    # graph_builder.add_node("tools", ToolNode(tools=tools))
    # graph_builder.add_node("human", human_node)

    # graph_builder.add_conditional_edges(
    #     "chatbot",
    #     select_next_node,
    #     {"human": "human", "tools": "tools", "__end__": "__end__"},
    # )
    # graph_builder.add_edge("tools", "chatbot")
    # graph_builder.add_edge("human", "chatbot")
    # graph_builder.add_edge(START, "chatbot")

    # # We now add a conditional edge
    # graph_builder.add_conditional_edges(
    #     # First, we define the start node. We use `agent`.
    #     # This means these are the edges taken after the `agent` node is called.
    #     "chatbot",
    #     # Next, we pass in the function that will determine which node is called next.
    #     should_continue,
    #     # Finally we pass in a mapping.
    #     # The keys are strings, and the values are other nodes.
    #     # END is a special node marking that the graph should finish.
    #     # What will happen is we will call `should_continue`, and then the output of that
    #     # will be matched against the keys in this mapping.
    #     # Based on which one it matches, that node will then be called.
    #     {
    #         # If `tools`, then we call the tool node.
    #         "continue": "action",
    #         # Otherwise we finish.
    #         "end": END,
    #     },
    # )
    # # We now add a normal edge from `tools` to `agent`.
    # # This means that after `tools` is called, `agent` node is called next.
    # graph_builder.add_edge("action", "chatbot")
    # workflow = StateGraph(State)
    # workflow = StateGraph(MessagesState)
    # workflow.add_node("agent", call_model)
    # workflow.add_node("tools", tool_node)

    # # Set the entrypoint as `agent`
    # # This means that this node is the first one called
    # workflow.add_edge(START, "agent")

    # # We now add a conditional edge
    # workflow.add_conditional_edges(
    #     # First, we define the start node. We use `agent`.
    #     # This means these are the edges taken after the `agent` node is called.
    #     "agent",
    #     # Next, we pass in the function that will determine which node is called next.
    #     should_continue,
    #     # Finally we pass in a mapping.
    #     # The keys are strings, and the values are other nodes.
    #     # END is a special node marking that the graph should finish.
    #     # What will happen is we will call `should_continue`, and then the output of that
    #     # will be matched against the keys in this mapping.
    #     # Based on which one it matches, that node will then be called.
    #     # {
    #     #     # If `tools`, then we call the tool node.
    #     #     "continue": "action",
    #     #     # Otherwise we finish.
    #     #     "end": END,
    #     # },
    # )

    # # We now add a normal edge from `tools` to `agent`.
    # # This means that after `tools` is called, `agent` node is called next.
    # workflow.add_edge("tools", "agent")

    # workflow.add_node("human", human_node)
    workflow.add_node("agent", weather_node)
    workflow.add_node("tools", tools_node())

    workflow.add_edge(START, "agent")
    # workflow.add_edge("human", "agent")
    # We now add a conditional edge
    workflow.add_conditional_edges(
        # First, we define the start node. We use `agent`.
        # This means these are the edges taken after the `agent` node is called.
        "agent",
        # Next, we pass in the function that will determine which node is called next.
        should_continue,
        # Finally we pass in a mapping.
        # The keys are strings, and the values are other nodes.
        # END is a special node marking that the graph should finish.
        # What will happen is we will call `should_continue`, and then the output of that
        # will be matched against the keys in this mapping.
        # Based on which one it matches, that node will then be called.
        {
            # If `tools`, then we call the tool node.
            "continue": "tools",
            # Otherwise we finish.
            "end": END,
        },
    )
    # workflow.add_edge("agent", "tools")
    workflow.add_edge("tools", "agent")
    # workflow.add_edge("tools", "agent")
    graph = workflow.compile(
        checkpointer=get_langgraph_checkpointer(),
        # interrupt_before=["tool"],
    )
    return graph


def flow_demo_parallel() -> CompiledStateGraph:
    builder = StateGraph(State)
    builder.add_node("a", ReturnNodeValue("I'm A"))
    builder.add_edge(START, "a")
    builder.add_node("b", ReturnNodeValue("I'm B"))
    builder.add_node("c", ReturnNodeValue("I'm C"))
    builder.add_node("d", ReturnNodeValue("I'm D"))
    builder.add_edge("a", "b")
    builder.add_edge("a", "c")
    builder.add_edge("b", "d")
    builder.add_edge("c", "d")
    builder.add_edge("d", END)
    graph = builder.compile()
    return graph
