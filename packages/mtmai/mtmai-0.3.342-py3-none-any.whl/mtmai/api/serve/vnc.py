import logging
import threading
from pathlib import Path

from fastapi import APIRouter, Depends
from opentelemetry import trace

from mtmai.api.deps import get_current_active_superuser
from mtmai.core import coreutils
from mtmai.core.config import settings
from mtmai.core.coreutils import is_in_vercel
from mtmai.mtlibs.process_helper import bash

tracer = trace.get_tracer_provider().get_tracer(__name__)
logger = logging.getLogger(__name__)


router = APIRouter()


def start_vnc_server():
    logger.info("start_vnc_server")
    home = Path.home()
    DEFAULT_PASSWORD = settings.DEFAULT_PASSWORD
    user = "user"
    bash(f"mkdir -p {home}/.certs/")
    bash(f"mkdir -p {home}/.vnc/")
    bash(
        f"openssl req -subj '/CN=example.com/O=My Company Name LTD./C=US' -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout {home}/.certs/ssl-cert-snakeoil.key -out {home}/.certs/ssl-cert-snakeoil.pem"
    )
    # 将会输出到文件 ~/.vnc/passwd
    bash(f'echo "{DEFAULT_PASSWORD}\n{DEFAULT_PASSWORD}\n" | vncpasswd -u {user} -r -w')
    bash(
        f'echo "{DEFAULT_PASSWORD}\n{DEFAULT_PASSWORD}\n" | vncpasswd -u {user} -r -w ~/.kasmpasswd'
    )

    setting_content = f"""
logging:
    log_writer_name: all
    log_dest: logfile
    level: 100
network:
    protocol: http
    interface: 0.0.0.0
    websocket_port: auto
    use_ipv4: true
    use_ipv6: true
    ssl:
        require_ssl: false
        pem_certificate: {home}/.certs/ssl-cert-snakeoil.pem
        pem_key: {home}/.certs/ssl-cert-snakeoil.key
"""
    Path(f"{home}/.vnc/kasmvnc.yaml").write_text(setting_content)
    Path(f"{home}/.vnc/xstartup").write_text("""#!/bin/sh
set -x
xfce4-terminal &
exec xfce4-session
""")
    bash(f"chmod 755 {home}/.vnc/xstartup")
    bash("touch ~/.vnc/.de-was-selected")
    bash("vncserver -kill :1 || true")
    bash(
        'export SHELL=/bin/bash && echo "1\n1\n1\n" | vncserver :1 -autokill -disableBasicAuth'
    )

    # 端口：8444


if not is_in_vercel() and not settings.is_in_gitpod and not coreutils.is_in_windows():
    threading.Thread(target=start_vnc_server).start()


@router.get(
    "/start", dependencies=[Depends(get_current_active_superuser)], status_code=201
)
async def start_vnc():
    threading.Thread(target=start_vnc_server).start()
    return {
        "ok": True,
    }


# logging:
#   log_writer_name: all
#   log_dest: logfile
#   level: 100
# network:
#   ssl:
#     pem_certificate: /home/user/.certs/ssl-cert-snakeoil.pem
#     pem_key: /home/user/.certs/ssl-cert-snakeoil.key


# mkdir /home/user/.certs/private/ -p
# openssl req -subj '/CN=example.com/O=My Company Name LTD./C=US' -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout /home/user/.certs/private/ssl-cert-snakeoil.key -out /home/user/.certs/ssl-cert-snakeoil.pem
