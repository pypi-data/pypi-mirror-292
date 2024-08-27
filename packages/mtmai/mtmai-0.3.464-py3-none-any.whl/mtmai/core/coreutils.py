import os
import platform
from urllib.parse import urlparse

from fastapi import Request


def is_in_huggingface():
    return os.getenv("SPACE_HOST")


def is_in_vercel() -> bool:
    a = os.getenv("VERCEL") == "1"
    return a


def is_in_temboio():
    return os.getenv("VISUALLY_MEASURED_DOWITCHER_TMPBOAI_PORT")


def is_in_windows() -> bool:
    return platform.system() == "Windows"


def backend_url_base(relative_path: str | None = None):
    from mtmai.core.config import settings

    if settings.Serve_ADDR:
        return f"http://{settings.Serve_ADDR}"

    gitpod_workspace_url = os.environ.get("GITPOD_WORKSPACE_URL")

    if gitpod_workspace_url:
        uri1 = urlparse(gitpod_workspace_url)
        return f"https://{settings.PORT}-{uri1.hostname}"
    return f"http://localhost:{settings.PORT}"


def abs_url(req: Request, path_name: str = ""):
    x_forwardd_host = req.headers.get("x-forwarded-host")
    x_forwardd_port = req.headers.get("x-forwarded-port")
    x_forwardd_proto = req.headers.get("x-forwarded-proto")
    if x_forwardd_host:
        base_url2 = f"{x_forwardd_proto}://{x_forwardd_host}"
        if path_name:
            return f"{base_url2}{path_name}"
        return base_url2
    else:
        return backend_url_base(path_name)


def is_in_gitpod() -> bool:
    return os.getenv("GITPOD_WORKSPACE_URL")


def is_in_testing():
    return os.getenv("PYTEST_CURRENT_TEST")
