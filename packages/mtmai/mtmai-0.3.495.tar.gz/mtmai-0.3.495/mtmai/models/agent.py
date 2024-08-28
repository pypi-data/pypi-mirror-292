from pydantic import BaseModel


class AgentMeta(BaseModel):
    name: str
    chat_url: str | None = None
    can_chat: bool = (False,)
    agent_type: str | None = None
    graph_image: str | None = None
    label: str | None = None
    description: str | None = None
