from fastapi import APIRouter
from pydantic import BaseModel
from sqlmodel import SQLModel

from mtmai.api.deps import SessionDep

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
def pull(
    db: SessionDep,
    # current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
):
    return AgentsPublic(id=111)


@router.post("", response_model=AgentsPublic)
def ack(
    db: SessionDep,
    # current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
):
    return AgentsPublic(id=111)
