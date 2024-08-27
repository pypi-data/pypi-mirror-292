from datetime import datetime
from enum import Enum

from langchain_core.runnables.config import RunnableConfig
from pgvector.sqlalchemy import Vector
from pydantic import BaseModel, EmailStr
from sqlmodel import JSON, Column, Field, Relationship, SQLModel

from mtmai.mtlibs import mtutils


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    username: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    # id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    id: str = Field(default_factory=mtutils.gen_orm_id_key, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    documents: list["Document"] = Relationship(
        back_populates="owner", cascade_delete=True
    )
    doccolls: list["DocColl"] = Relationship(
        back_populates="owner", cascade_delete=True
    )


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: str


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    # id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    id: str = Field(default_factory=mtutils.gen_orm_id_key, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: str = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: str
    owner_id: str


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


# ---------------------------------------------------------------------------------------------------------------------


class StatusEnum(str, Enum):
    """工作流状态"""

    NEW = "new"  # New state
    PENDING = "pending"  # Waiting for execution
    RUNNING = "running"
    WAITING_FOR_HUMAN = "waiting_for_human"  # Awaiting human intervention
    CONTINUE_AFTER_CONFIRMATION = (
        "continue_after_confirmation"  # Continue after confirmation
    )
    # START = "start"
    END = "end"
    PAUSE = "pause"


# class UserBase(SQLModel):
#     # id: int | None = Field(default=None, primary_key=True)
#     id: str = Field(default_factory=mtutils.gen_orm_id_key, primary_key=True)
#     username: str
#     email: str | None = None
#     full_name: str | None = None
#     disabled: bool | None = None


# class User(UserBase, table=True):
#     hashed_password: str

#     chats: list["ChatInput"] = Relationship(back_populates="user")


class ChatInput(SQLModel, table=True):
    """用户跟聊天机器人的对话信息"""

    id: str = Field(default_factory=mtutils.gen_orm_id_key, primary_key=True)
    agent_id: str
    user_id: str | None = Field(default=None, foreign_key="user.id")
    # user: User | None = Relationship(back_populates="chats")

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    output: str | None = Field(default="")
    config: RunnableConfig = Field(sa_column=Column(JSON))
    title: str | None = Field(default="")
    description: str | None = Field(default="")
    path: str | None = Field(default="")
    share_path: str | None = Field(default="")
    # status: str = Field(default=StatusEnum.NEW.value, nullable=False)
    # messages: ChatMessage = Field(sa_column=Column(JSON))

    messages: list["ChatMessage"] = Relationship(back_populates="chat")


class ChatMessage(SQLModel, table=True):
    id: str = Field(default_factory=mtutils.gen_orm_id_key, primary_key=True)
    content: str | None = None
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    chat_id: str | None = Field(default=None, foreign_key="chatinput.id")
    chat: ChatInput | None = Relationship(back_populates="messages")
    role: str | None = Field(default="user")


class AgentReport(SQLModel, table=True):
    id: str = Field(default_factory=mtutils.gen_orm_id_key, primary_key=True)
    agent_name: str = Field(index=True)
    content: str | None = None
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)

    # chat_id: str | None = Field(default=None, foreign_key="chatinput.id")
    # chat: ChatInput | None = Relationship(back_populates="messages")
    # role: str | None = Field(default="user")


class Knownledge(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    wid: str = Field(index=True)
    title: str = Field(index=True)
    content: str = Field(default=None, index=False)


class Agent(SQLModel, table=True):
    id: str = Field(primary_key=True)
    title: str = Field()
    type: str = Field(default="default")


class PostContent(SQLModel, table=True):
    id: str = Field(default_factory=mtutils.gen_orm_id_key, primary_key=True)
    content: str = Field()
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    # post_id: str | None = Field(default=None, foreign_key="blogpost.id")
    # post: "BlogPost" = Relationship(back_populates="content")


class Post(SQLModel, table=True):
    id: str = Field(default_factory=mtutils.gen_orm_id_key, primary_key=True)
    title: str = Field()
    content_id: str | None = Field(default=None, foreign_key="postcontent.id")
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    # content: BlogPostContent | None = Relationship(back_populates="post")
    # content: "BlogPostContent" = Relationship(
    #     back_populates="post",
    # )


class AgentMeta(BaseModel):
    name: str
    chat_url: str | None = None
    can_chat: bool = (False,)
    agent_type: str | None = None
    graph_image: str | None = None


# 知识库相关


# Shared properties
class DocumentBase(SQLModel):
    # title: str | None = Field(default=None, max_length=255)
    collection: str = Field(default="default", index=True)
    meta: dict | None = Field(default={}, sa_column=Column(JSON))
    document: str | None = Field(default=None, max_length=8196)


class Document(DocumentBase, table=True):
    """
    通用的基于 postgres + pgvector 的 rag 文档
    注意: 需要提前运行: CREATE EXTENSION IF NOT EXISTS vector
    参考: https://github.com/pgvector/pgvector-python/tree/master
    """

    id: str = Field(default_factory=mtutils.gen_orm_id_key, primary_key=True)
    embedding: list[float] = Field(sa_column=Column(Vector(1024)))
    owner_id: str = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    owner: User | None = Relationship(back_populates="documents")

    class Config:  # noqa: D106
        arbitrary_types_allowed = True


class DocCollBase(SQLModel):
    title: str = Field(default="default", index=True)


class DocColl(DocCollBase, table=True):
    """
    知识库集
    """

    id: str = Field(default_factory=mtutils.gen_orm_id_key, primary_key=True)
    owner_id: str = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    owner: User | None = Relationship(back_populates="doccolls")

    class Config:  # noqa: D106
        arbitrary_types_allowed = True


# Properties to receive on item creation
class DocCollCreate(DocCollBase):
    pass


class DocCollPublic(SQLModel):
    id: str
    owner_id: str
    title: str


class DocCollsPublic(SQLModel):
    data: list[DocCollPublic]
    count: int
