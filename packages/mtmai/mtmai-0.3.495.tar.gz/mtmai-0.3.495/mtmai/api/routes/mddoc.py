from fastapi import APIRouter

router = APIRouter()


@router.get("/dash_menus")
def md_doc():
    return ""
