import logging

from fastapi import APIRouter, Depends, FastAPI, Query
from pydantic import BaseModel
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select

from mtmai.api.deps import CurrentUser
from mtmai.core.config import settings
from mtmai.core.db import get_session, getdb
from mtmai.models.models import ChatInput, ChatMessage

router = APIRouter()

logger = logging.getLogger()


def register_api_router(app: FastAPI):
    app.include_router(router)


class ConfigModel(BaseModel):
    option1: str
    option2: int


async def get_chatinput_byid(chat_id: str):
    with Session(getdb()) as session:
        statement = (
            select(ChatInput)
            .where(ChatInput.id == chat_id)
            .options(joinedload(ChatInput.messages))
        )
        result = session.exec(statement).first()
        return result


# @router.get(API_PREFIX + "/chat_input", response_model=list[ChatInput])
# async def list_chat_input(request: Request):
#     items: Sequence[ChatInput] = []
#     with Session(getdb()) as session:
#         items = session.exec(select(ChatInput)).all()
#     return items


@router.get(
    settings.API_V1_STR + "/chat/{chat_id}/messages", response_model=list[ChatMessage]
)
async def chat_messages(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    # current_user: Annotated[User, Depends(get_current_active_user)],
    current_user: CurrentUser,
):
    if not current_user:
        return None
    chat_messages = session.exec(select(ChatMessage).offset(offset).limit(limit)).all()
    return chat_messages


# @router.get(API_PREFIX + "/chat_input/{id}", response_model=ChatInput)
# async def chat_input_get(id: str):
#     return await get_chatinput_byid(id)


class ChatInputReq(BaseModel):
    chat_id: str | None = None
    messages: list[ChatMessage]
    # text: str
    # agent_id: str | None
    # role: str | None = None


# @router.post(API_PREFIX + "/chat")
# def cht_input(
#     *,
#     req: ChatInputReq,
#     session: Session = Depends(get_session),
# ):
#     # ensure_thread_id(input)
#     # input.status = "new"

#     agent = get_agent(session, req.agent_id)
#     if not agent:
#         msg = f"missing agent {req.agent_id}"
#         raise Exception(msg)
#     if not req.chat_id:
#         # 新的对话
#         try:
#             logger.info("new conversation %s", req)
#             chat_input = ChatInput(agent_id=req.agent_id)
#             session.add(chat_input)
#             session.commit()
#         except Exception as e:
#             logger.exception("get_response_openai Error: %s", e)
#             raise HTTPException(503)
#     else:
#         # 现有的对话
#         chat_input = session.exec(
#             select(ChatInput).where(ChatInput.id == req.chat_id)
#         ).one()
#         if not chat_input:
#             raise Exception("missing conversation id: %s", req.chat_id)

#     new_message = ChatMessage(
#         content=req.text,
#         chat_id=req.chat_id,
#         role=req.role or "user",
#     )
#     with Session(getdb()) as session:
#         session.add(new_message)
#         session.commit()
#         session.refresh(new_message)

#     return {"ok": True}


@router.put(settings.API_V1_STR + "/chat_input")
async def chat_input_put(input: ChatInput):
    with Session(getdb()) as session:
        session.merge(input)
        session.commit()
    return input


@router.patch(settings.API_V1_STR + "/chat_input/{id}")
async def chat_input_patch(id: str, item: ChatInput):
    item = get_chatinput_byid(id)
    if not item:
        return "Item not found", 404
    stored_item_model = ChatInput(**item)
    update_data = item.dict(exclude_unset=True)
    updated_item = stored_item_model.copy(update=update_data)
    # items[item_id] = jsonable_encoder(updated_item)
    with Session(getdb()) as session:
        session.merge(updated_item)
        session.commit()

    return updated_item


@router.delete(settings.API_V1_STR + "/chat_input/{id}")
async def chat_input_delete(id: str):
    with Session(getdb()) as session:
        statement = select(ChatInput).where(ChatInput.id == id)
        results = session.exec(statement)
        item = results.one()
        session.delete(item)
        session.commit()
        return item
