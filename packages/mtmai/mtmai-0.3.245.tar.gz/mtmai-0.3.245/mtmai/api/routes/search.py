import threading

from fastapi import APIRouter

from mtmai.core.config import settings
from mtmai.core.coreutils import is_in_vercel
from mtmai.mtlibs.process_helper import bash

router = APIRouter()


searxng_install_dir = "/app/searxng"
searxng_setting_file = searxng_install_dir + "/settings.yml"  # Fix the missing slash


def install_searxng():
    script = f"""git clone https://github.com/searxng/searxng {searxng_install_dir} \
    && cd /app/searxng \
    && python -m venv .venv \
    && source .venv/bin/activate \
    && pip install -U --no-cache-dir pip setuptools wheel pyyaml && pip install --no-cache-dir -e ."""
    bash(script)


def run_searxng_server():
    bash(
        f'cd {searxng_install_dir}  && export SEARXNG_SETTINGS_PATH="{searxng_setting_file}" && . .venv/bin/activate && python searx/webapp.py &'
    )


if not is_in_vercel() and not settings.is_in_gitpod:
    threading.Thread(target=run_searxng_server).start()


@router.get("/serve")
def start_searxng():
    threading.Thread(target=run_searxng_server).start()
    return {"ok": True}
