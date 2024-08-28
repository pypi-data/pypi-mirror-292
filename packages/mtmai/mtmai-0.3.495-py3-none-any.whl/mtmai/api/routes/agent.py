from fastapi import APIRouter
from sqlmodel import SQLModel

from mtmai.api.deps import OptionalUserDep, SessionDep
from mtmai.core.config import settings
from mtmai.models.agent import AgentMeta

router = APIRouter()


# class AgentPublic(BaseModel):
#     id: str
#     label: str | None = None
#     description: str | None = None
#     agent_type: str | None = None


class AgentsPublic(SQLModel):
    data: list[AgentMeta]
    count: int


@router.get("", response_model=AgentsPublic)
def items(
    db: SessionDep,
    user: OptionalUserDep,
    skip: int = 0,
    limit: int = 100,
):
    all_agents = [
        AgentMeta(
            name="joke",
            label="冷笑话",
            description="笑话生成器",
            chat_url=settings.API_V1_STR + "/joke/chat",
            can_chat=False,
            agent_type="graphq",
            graph_image=settings.API_V1_STR + "/joke/image",
        ),
        AgentMeta(
            name="blogwriter",
            label="博客写手",
            description="博客写手",
            chat_url=settings.API_V1_STR + "/blogwriter/chat",
            can_chat=False,
            agent_type="graphq",
            graph_image=settings.API_V1_STR + "/blogwriter/image",
        ),
    ]
    # items = [
    #     AgentPublic(id="joke", label="冷笑话", description="笑话生成器"),
    #     AgentPublic(
    #         id="blogwriter",
    #         label="博客文章生成器",
    #         description="根据配置，自动爬取对应主题文章，并整理到博客文章中",
    #     ),
    # ]
    return AgentsPublic(data=all_agents, count=len(all_agents))
