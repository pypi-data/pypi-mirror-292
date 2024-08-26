import logging
from collections.abc import Iterable

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam

from mtmai.mtlibs.aiutils import lcllm_openai_chat

logger = logging.getLogger()


# @tool
# def get_flows(url: str):
#     """Get list of langgraph flows"""
#     return ["list1", "list2"]


async def chatbot_agent(
    messages: Iterable[ChatCompletionMessageParam], chat_id: str = None
):
    # tools = [get_flows]
    tools = []
    llm = lcllm_openai_chat("")
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant"),
            MessagesPlaceholder("chat_history", optional=True),
            # ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    agent = create_openai_tools_agent(
        llm.with_config({"tags": ["agent_llm"]}), tools, prompt
    )
    agent_executor = AgentExecutor(agent=agent, tools=tools).with_config(
        {"run_name": "Agent"}
    )

    return agent_executor
