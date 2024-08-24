import logging
import threading
from pathlib import Path

from fastapi import APIRouter, Depends

from mtmai.api.deps import get_current_active_superuser
from mtmai.core import coreutils
from mtmai.core.config import settings
from mtmai.mtlibs.process_helper import bash

router = APIRouter()
logger = logging.getLogger()


def start_front_app():
    front_dir = Path("/app/apps/mtmaiweb")
    logger.info("准备启动前端, 端口 %s, 路径: %s", settings.FRONT_PORT, front_dir)

    mtmai_url = coreutils.backend_url_base()
    if front_dir.joinpath("apps/mtmaiweb/server.js").exists():
        bash(
            f"cd {front_dir} && PORT={settings.FRONT_PORT} HOSTNAME=0.0.0.0 MTMAI_API_BASE={mtmai_url} node apps/mtmaiweb/server.js"
        )
    logger.warning("因路径问题, 前端 (mtmaiweb) nextjs 不能正确启动")


if (
    not settings.is_in_vercel
    and not settings.is_in_gitpod
    and not coreutils.is_in_windows()
):
    threading.Thread(target=start_front_app).start()


@router.get(
    "/front_start",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
)
def front_start():
    threading.Thread(target=start_front_app).start()
    return {"ok": True}
