from fastapi import APIRouter
from pydantic import BaseModel
from sqlmodel import SQLModel

from mtmai.api.deps import OptionalUserDep, SessionDep

router = APIRouter()


class AgentPublic(BaseModel):
    id: str
    label: str | None = None
    description: str | None = None
    agent_type: str | None = None


class AgentsPublic(SQLModel):
    data: list[AgentPublic]
    count: int


@router.get("", response_model=AgentsPublic)
def query(
    db: SessionDep,
    user: OptionalUserDep,
    skip: int = 0,
    limit: int = 100,
):
    # all_agents = [AgentMeta()]
    items = [
        AgentPublic(id="joke", label="冷笑话", description="笑话生成器"),
        AgentPublic(
            id="blogwriter",
            label="博客文章生成器",
            description="根据配置，自动爬取对应主题文章，并整理到博客文章中",
        ),
    ]
    return AgentsPublic(data=items, count=len(items))
