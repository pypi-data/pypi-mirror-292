from langgraph.prebuilt import ToolNode

from mtmai.teams.weather_node import get_weather
from mtmai.tools.search_tools import SearchTools


def tools_node():
    tools = [get_weather, SearchTools.search_internet]
    tool_node = ToolNode(tools)
    return tool_node
