from datetime import timedelta
from typing import Annotated, Any
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from mtmai import crud
from mtmai.api.deps import SessionDep, get_current_active_superuser
from mtmai.core import coreutils, security
from mtmai.core.config import settings
from mtmai.core.security import get_password_hash
from mtmai.models.models import Message, NewPassword, Token
from mtmai.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
    verify_password_reset_token,
)

router = APIRouter()


@router.post("/login/access-token")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )

    # 创建 JSON 响应对象
    response = JSONResponse(content=access_token.model_dump())

    # 将 token 设置到 HttpOnly 和 Secure Cookie 中
    response.set_cookie(
        key="access_token",
        value=f"{access_token.access_token}",
        httponly=True,
        secure=True,
        samesite="lax",  # 根据需要调整 samesite 策略,lax是常见的选择
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        * 60,  # 以秒为单位设置 Cookie 的过期时间
    )

    return response


@router.post("/password-recovery/{email}")
def recover_password(email: str, session: SessionDep) -> Message:
    """
    Password Recovery
    """
    user = crud.get_user_by_email(session=session, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    send_email(
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Password recovery email sent")


@router.post("/reset-password/")
def reset_password(session: SessionDep, body: NewPassword) -> Message:
    """
    Reset password
    """
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = crud.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    hashed_password = get_password_hash(password=body.new_password)
    user.hashed_password = hashed_password
    session.add(user)
    session.commit()
    return Message(message="Password updated successfully")


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
)
def recover_password_html_content(email: str, session: SessionDep) -> Any:
    """
    HTML Content for Password Recovery
    """
    user = crud.get_user_by_email(session=session, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )

    return HTMLResponse(
        content=email_data.html_content, headers={"subject:": email_data.subject}
    )


@router.get("/auth/github/callback")
async def github_oauth_callback(req: Request):
    # 从请求中获取 GitHub OAuth 传回的 code 和 state 参数
    code = req.query_params.get("code")
    state = req.query_params.get("state", "")

    if not code:
        raise HTTPException(status_code=400, detail="Code not provided")

    client_id = settings.GITHUB_CLIENT_ID
    client_secret = settings.GITHUB_CLIENT_SECRET

    # 交换 code 获取 access token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            json={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
            },
        )
        token_data = token_response.json()

    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Failed to obtain access token")

    # 使用 access token 获取用户信息
    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_data = user_response.json()
    full_redirect_url = coreutils.abs_url(req, state)
    return RedirectResponse(url=full_redirect_url)


@router.get("/auth/github/authorize")
async def github_oauth_authorize(req: Request):
    client_id = settings.GITHUB_CLIENT_ID
    if not client_id:
        raise HTTPException(
            status_code=500, detail="Missing environment variable: GITHUB_CLIENT_ID"
        )

    next_url = req.query_params.get("next", "/")

    callback_path = "/api/v1/auth/github/callback"
    redirect_uri = coreutils.abs_url(req, callback_path)

    github_auth_url = "https://github.com/login/oauth/authorize?" + urlencode(
        {"client_id": client_id, "redirect_uri": redirect_uri, "state": next_url}
    )

    return RedirectResponse(github_auth_url)
