import logging
from pprint import pformat

from langchain_core.messages import ToolMessage

from .graph_state import State, create_response

logger = logging.getLogger()


def human_node(state: State):
    logger.info("进入 human_node %s", pformat(state))

    new_messages = []
    if not isinstance(state["messages"][-1], ToolMessage):
        # Typically, the user will have updated the state during the interrupt.
        # If they choose not to, we will include a placeholder ToolMessage to
        # let the LLM continue.
        new_messages.append(
            create_response("No response from human.", state["messages"][-1])
        )

    logger.info("完成 human_node %s", pformat(state, depth=1))
    return {
        # Append the new messages
        "messages": new_messages,
        # Unset the flag
        "ask_human": False,
    }
