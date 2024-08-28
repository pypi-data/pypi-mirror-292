from fastapi import APIRouter
from sqlmodel import SQLModel

from mtmai.api.deps import OptionalUserDep, SessionDep
from mtmai.core.config import settings
from mtmai.models.agent import AgentMeta

router = APIRouter()


class AgentsPublic(SQLModel):
    data: list[AgentMeta]
    count: int


all_agents = [
    AgentMeta(
        id="joke",
        name="joke",
        label="冷笑话",
        description="笑话生成器",
        chat_url=settings.API_V1_STR + "/joke/chat",
        can_chat=False,
        agent_type="graphq",
        graph_image=settings.API_V1_STR + "/joke/image",
    ),
    AgentMeta(
        id="joke",
        name="blogwriter",
        label="博客写手",
        description="博客写手",
        chat_url=settings.API_V1_STR + "/blogwriter/chat",
        can_chat=False,
        agent_type="graphq",
        graph_image=settings.API_V1_STR + "/blogwriter/image",
    ),
    AgentMeta(
        id="mteditor",
        name="mteditor",
        label="智能文章编辑器",
        description="智能文章编辑器",
        chat_url=settings.API_V1_STR + "/mteditor/chat",
        can_chat=False,
        agent_type="common",
        graph_image=settings.API_V1_STR + "/mteditor/image",
    ),
]


@router.get("", response_model=AgentsPublic)
def items(
    db: SessionDep,
    user: OptionalUserDep,
    skip: int = 0,
    limit: int = 100,
):
    return AgentsPublic(data=all_agents, count=len(all_agents))


@router.get("/{agent_id}", response_model=AgentMeta | None)
def get_item(db: SessionDep, user: OptionalUserDep, agent_id: str):
    for agent in all_agents:
        if agent.id == agent_id:
            return agent
    return None
