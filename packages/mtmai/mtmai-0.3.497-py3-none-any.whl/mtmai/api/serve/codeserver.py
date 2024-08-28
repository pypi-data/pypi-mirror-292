import logging
import threading
import time
from pathlib import Path

from fastapi import APIRouter
from mtmlib.mtutils import bash
from opentelemetry import trace

tracer = trace.get_tracer_provider().get_tracer(__name__)
logger = logging.getLogger()


router = APIRouter()


# 官网： https://coder.com/docs/install
def start_code_server():
    config_file = Path.home().joinpath(".config/code-server/config.yaml")
    if not config_file.exists():
        logger.warning("code-server 配置文件不存在, 跳过启动: %s", config_file)
        return
    # 配置要点：
    # 1: 明确指定 SHELL 路径，否则在一些受限环境，可能没有默认的shell 变量，导致：“The terminal process "/usr/sbin/nologin" terminated with exit code: 1.”
    bash(
        "PORT=8622 PASSWORD=feihuo321 SHELL=/bin/bash code-server --bind-addr=0.0.0.0 &"
    )
    time.sleep(2)
    config_content = config_file.read_text()
    logger.info("codeserver 配置: %s", config_content)


@router.get("/start", include_in_schema=False)
async def start():
    threading.Thread(target=start_code_server).start()
