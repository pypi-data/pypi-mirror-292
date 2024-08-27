import logging

import fastapi
from sqlmodel import Session, select

from mtmai.core.config import settings
from mtmai.core.db import getdb
from mtmai.models.models import ChatMessage

router = fastapi.APIRouter()

logger = logging.getLogger()


def register_api_router(app: fastapi.FastAPI):
    app.include_router(router)


@router.put(settings.API_V1_STR + "/chat_messages")
async def chat_message_add(chat_message: ChatMessage):
    """追加一个聊天历史"""
    with Session(getdb()) as session:
        session.merge(chat_message)
        session.commit()
    return chat_message


@router.get(settings.API_V1_STR + "/chat_messages/{id}")
def chat_message_get(id: int):
    with Session(getdb()) as session:
        statement = select(ChatMessage).where(ChatMessage.id == id)
        results = session.exec(statement)
        item = results.one()
        session.delete(item)
        session.commit()
        return item
