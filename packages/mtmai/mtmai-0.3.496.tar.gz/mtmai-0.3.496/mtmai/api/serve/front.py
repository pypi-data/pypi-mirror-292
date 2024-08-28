import logging
import threading

from fastapi import APIRouter, Depends
from mtmlib import mtutils

from mtmai.api.deps import get_current_active_superuser
from mtmai.core import coreutils
from mtmai.core.config import settings

router = APIRouter()
logger = logging.getLogger()


def start_front_app():
    # front_dir = Path("/app/apps/mtmaiweb")
    # # logger.info("准备启动前端, 端口 %s, 路径: %s", settings.FRONT_PORT, front_dir)
    mtmai_url = coreutils.backend_url_base()
    # if front_dir.joinpath("apps/mtmaiweb/server.js").exists():
    #     bash(
    #         f"cd {front_dir} && PORT={settings.FRONT_PORT} HOSTNAME=0.0.0.0 MTMAI_API_BASE={mtmai_url} node apps/mtmaiweb/server.js"
    #     )
    #     return
    # mtmaiweb_package_dir = Path("node_ modules/mtmaiweb/")
    # if mtmaiweb_package_dir.exists():
    #     bash(
    #         "cd mtmaiweb_package_dir && PORT={settings.FRONT_PORT} HOSTNAME=0.0.0.0 MTMAI_API_BASE={mtmai_url} bun run start"
    #     )
    #     return
    # logger.warning("因路径问题, 前端 (mtmaiweb) nextjs 不能正确启动")
    if not mtutils.command_exists("mtmaiweb"):
        logger.warning("⚠️ mtmaiweb 命令未安装,跳过前端的启动")
        return
    mtutils.bash(
        f"PORT={settings.FRONT_PORT} MTMAI_API_BASE={mtmai_url} mtmaiweb serve"
    )


@router.get(
    "/front_start",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
    include_in_schema=False
)
def front_start():
    threading.Thread(target=start_front_app).start()
    return {"ok": True}
