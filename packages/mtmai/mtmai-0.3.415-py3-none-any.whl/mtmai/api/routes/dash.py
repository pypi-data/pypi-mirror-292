from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class DashNavItem(BaseModel):
    label: str
    url: str


@router.get("/dash_menus")
def get_dash_memus():
    return [
        DashNavItem(label="首页", url="/dash"),
        DashNavItem(label="openapi 文档", url="/dash/docs"),
    ]
