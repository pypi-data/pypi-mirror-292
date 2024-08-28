from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session, select

from mtmai.core.config import settings
from mtmai.core.db import get_session
from mtmai.models.models import Post, PostContent

router = APIRouter(prefix=settings.API_V1_STR)


@router.get("/", response_model=list[Post])
async def blog_post_list(
    *,
    db: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    posts = db.exec(select(Post).offset(offset).limit(limit)).all()
    return posts


class BlogPostCreateReq(BaseModel):
    title: str
    content: str


class BlogPostCreateRes(BaseModel):
    id: str


@router.post("/", response_model=BlogPostCreateRes)
async def blog_post_create(
    *,
    db: Session = Depends(get_session),
    req: BlogPostCreateReq,
):
    new_blog_post = Post(**req.model_dump())

    # Update title
    new_blog_post.title = req.title
    if new_blog_post.content_id:
        blog_post_content = db.exec(
            select(PostContent).where(PostContent.id == new_blog_post.content_id)
        ).one_or_none()
    else:
        blog_post_content = None

    if not blog_post_content:
        blog_post_content = PostContent(content=req.content)
        db.add(blog_post_content)
        db.commit()
        db.refresh(blog_post_content)
        new_blog_post.content_id = blog_post_content.id

    db.add(new_blog_post)
    db.commit()
    db.refresh(new_blog_post)
    return new_blog_post


class BlogPostUpdateReq(BaseModel):
    title: str
    content: str


class BlogPostUpdateRes(BaseModel):
    id: str


@router.put("/{post_id}", response_model=BlogPostUpdateRes)
async def blog_post_update(
    *,
    post_id: str,
    db: Session = Depends(get_session),
    req: BlogPostUpdateReq,
):
    blog_post = db.exec(select(Post).where(Post.id == post_id)).one()
    if not blog_post:
        raise HTTPException(status_code=404)

    blog_post.title = req.title

    # 更新内容
    if blog_post.content_id:
        blog_post_content = db.exec(
            select(PostContent).where(PostContent.id == blog_post.content_id)
        ).one_or_none()
    else:
        blog_post_content = None

    if not blog_post_content:
        blog_post_content = PostContent(content=req.content)
        db.add(blog_post_content)
        db.commit()
        db.refresh(blog_post_content)
        blog_post.content_id = blog_post_content.id
    else:
        blog_post_content.content = req.content

    db.add(blog_post)
    db.add(blog_post_content)
    db.commit()
    return BlogPostUpdateRes(id=blog_post.id)


class BlogPostDetailRes(BaseModel):
    id: str
    title: str
    content: str


@router.get("/{post_id}", response_model=BlogPostDetailRes)
async def blog_post_get(
    *,
    post_id: str,
    db: Session = Depends(get_session),
):
    blog_post = db.exec(select(Post).where(Post.id == post_id)).one()
    if not blog_post:
        raise HTTPException(status_code=404)

    blog_post_content = db.exec(
        select(PostContent).where(PostContent.id == blog_post.content_id)
    ).one_or_none()

    return BlogPostDetailRes(
        id=blog_post.id, title=blog_post.title, content=blog_post_content.content
    )
