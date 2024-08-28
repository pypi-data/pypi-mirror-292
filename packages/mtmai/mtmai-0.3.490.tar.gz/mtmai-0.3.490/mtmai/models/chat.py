from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel

from mtmai.models.models import ChatInput
from mtmai.mtlibs import mtutils


class ChatMessage(SQLModel, table=True):
    id: str = Field(default_factory=mtutils.gen_orm_id_key, primary_key=True)
    content: str | None = None
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    chat_id: str | None = Field(default=None, foreign_key="chatinput.id")
    chat: ChatInput | None = Relationship(back_populates="messages")
    role: str | None = Field(default="user")
