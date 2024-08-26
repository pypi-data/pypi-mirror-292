# from mtmai.retrieval import retrieval
# from mtmai.retrieval.retrieval import Document
import logging
from typing import TYPE_CHECKING

from fastapi import APIRouter
from pgvector.sqlalchemy import Vector
from pydantic import BaseModel
from sqlmodel import JSON, Column, Field, Session, SQLModel, select

from mtmai.api.deps import SessionDep
from mtmai.llm.embedding import embedding_hf
from mtmai.mtlibs import mtutils

if TYPE_CHECKING:
    from langchain_core.documents import Document


router = APIRouter()

logger = logging.getLogger(__name__)


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

    class Config:  # noqa: D106
        arbitrary_types_allowed = True


class RagAddContentReq(BaseModel):
    collection: str | None
    content: str


# Properties to return via API, id is always required
class DocumentPublic(DocumentBase):
    id: str
    collection: str
    document: str


class DocumentResonse(BaseModel):
    data: list[DocumentPublic]
    count: int


async def doc_add(db: Session, content: str):
    result = await embedding_hf(inputs=[content])
    doc = Document(document=content, embedding=result[0])
    db.add(doc)
    db.commit()


async def doc_retrieval(db: Session, query: str):
    result = await embedding_hf(inputs=[query])
    docs = db.exec(
        select(Document).order_by(Document.embedding.l2_distance(result[0])).limit(5)
    ).all()
    return docs


class RagAddContentRes(BaseModel):
    success: bool = True


@router.post("/", response_model=RagAddContentRes)
async def add_content(db: SessionDep, req: RagAddContentReq):
    await doc_add(db=db, content=req.content)

    return RagAddContentRes()


class RagRetrievalReq(BaseModel):
    collection: str | None
    query: str


@router.post("/retrieval", response_model=DocumentResonse)
async def retrieval_docs(db: SessionDep, req: RagRetrievalReq):
    result = await embedding_hf(inputs=[req.query])
    docs = db.exec(
        select(Document).order_by(Document.embedding.l2_distance(result[0])).limit(5)
    ).all()
    return DocumentResonse(data=docs, count=len(docs))


# def hello_pg_vetor():
#     # loader = TextLoader("state_of_the_union.txt")
#     loader = WebBaseLoader("https://www.espn.com/")
#     documents = loader.load()
#     text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
#     docs = text_splitter.split_documents(documents)

#     embeddings = get_embeding_llm()
#     connection_string = settings.DATABASE_URL
#     collection_name = "state_of_the_union"

#     db = PGEmbedding.from_documents(
#         embedding=embeddings,
#         documents=docs,
#         collection_name=collection_name,
#         connection_string=connection_string,
#     )

#     query = "What did the president say about Ketanji Brown Jackson"
#     docs_with_score: list[tuple[Document, float]] = db.similarity_search_with_score(
#         query
#     )

#     for doc, score in docs_with_score:
#         print("-" * 80)
#         print("Score: ", score)
#         print(doc.page_content)
#         print("-" * 80)

#     return json.dumps(jsonable_encoder(docs_with_score))
