import logging

from fastapi import APIRouter
from pydantic import BaseModel

from mtmai.core.config import settings

logger = logging.getLogger()

router = APIRouter()


class SubApp(BaseModel):
    name: str
    openapi: str


class SubWeb(BaseModel):
    name: str
    urlbase: str


class ConfigResponse(BaseModel):
    name: str
    subapps: list[SubApp]
    subwebs: list[SubWeb]


@router.get("", response_model=ConfigResponse)
async def get_config():
    return ConfigResponse(
        name=settings.app_name,
        subapps=[
            SubApp(name="main", openapi="/api/v1/openapi.json"),
            SubApp(name="trans", openapi="/api/v1/trans/openapi.json"),
        ],
        subwebs=[
            SubWeb(name="searxng", urlbase="https://www.baidu.com"),
        ],
    )
