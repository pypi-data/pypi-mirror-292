import fastapi
from fastapi import APIRouter
from sqlmodel import Session, select

from mtmai.core.db import getdb
from mtmai.models.models import Knownledge

router = APIRouter()


def register_api_router(app: fastapi.FastAPI):
    app.include_router(router)


@router.post("")
def create(knowledge: Knownledge):
    with Session(getdb()) as session:
        session.add(Knownledge)
        session.commit()
        session.refresh(Knownledge)
        return knowledge


@router.get("/knows/", response_model=list[Knownledge])
def items():
    with Session(getdb()) as session:
        heroes = session.exec(select(Knownledge)).all()
        return heroes


@router.get("/knows/{id}")
def get_one(id: int):
    with Session(getdb()) as session:
        heroes = session.exec(select(Knownledge)).all()
        return heroes
