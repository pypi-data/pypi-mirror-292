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


class QMessagePublic(SQLModel):
    id: str


@router.get("", response_model=QMessagePublic)
def pull(
    db: SessionDep,
    skip: int = 0,
    limit: int = 100,
):
    return QMessagePublic(id="id111")


@router.post("", response_model=QMessagePublic)
def ack(
    db: SessionDep,
    skip: int = 0,
    limit: int = 100,
):
    return QMessagePublic(id="id222")
