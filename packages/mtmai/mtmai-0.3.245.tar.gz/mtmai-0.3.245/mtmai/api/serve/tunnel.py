import logging
import threading
from pathlib import Path

from fastapi import APIRouter

from mtmai.core import coreutils
from mtmai.core.config import settings
from mtmai.mtlibs.httpUtils import download_file
from mtmai.mtlibs.process_helper import bash, command_exists

router = APIRouter()
logger = logging.getLogger(__name__)


def start_cloudflared():
    if not settings.CF_TUNNEL_TOKEN:
        logger.warning("missing env CF_TUNNEL_TOKEN")
        return

    bash("sudo pkill cloudflared || true")
    logger.info("----start up cloudflared tunnel----")
    bash(
        f"""cloudflared tunnel --no-autoupdate --http2-origin run --token {settings.CF_TUNNEL_TOKEN} & """
    )


if (
    not settings.is_in_vercel
    and not settings.is_in_gitpod
    and settings.CF_TUNNEL_TOKEN
    and not coreutils.is_in_huggingface()
    and not coreutils.is_in_windows()
):
    start_cloudflared()


@router.get("/start")
def start():
    threading.Thread(target=start_cloudflared).start()


@router.get("/install")
def install():
    if not command_exists("cloudflared"):
        logger.info("cloudflared 命令不存在现在安装")
        download_file(
            "https://github.com/cloudflare/cloudflared/releases/download/2024.1.5/cloudflared-linux-amd64",
            Path.home() / ".local/bin/cloudflared",
        )
    return "installed"
