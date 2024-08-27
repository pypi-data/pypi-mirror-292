import logging

from fastapi import APIRouter
from sqlmodel import select

from mtmai.api.deps import CurrentUser, SessionDep
from mtmai.models import DocColl, DocCollPublic

router = APIRouter()

logger = logging.getLogger()


################################################################################################################
# 知识库集
@router.get("/doccolls", response_model=DocCollPublic)
async def doccolls(
    db: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
):
    docs = db.exec(
        select(DocColl)
        # .order_by(Document.embedding.l2_distance(result[0]))
        .skip(skip)
        .limit(limit)
    ).all()
    return DocCollPublic(data=docs, count=len(docs))
