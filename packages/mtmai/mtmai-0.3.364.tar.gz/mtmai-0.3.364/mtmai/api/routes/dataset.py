from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class DashNavItem(BaseModel):
    label: str
    url: str


@router.get("/dataset/download/{dataset_name}")
def dataset_download(dataset_name: str):
    """数据集文件下载"""
    Path("./mtmai")
    return ""
