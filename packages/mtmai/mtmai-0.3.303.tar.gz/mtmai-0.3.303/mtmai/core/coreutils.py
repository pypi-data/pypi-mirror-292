import os
import platform


def is_in_huggingface():
    return os.getenv("SPACE_HOST")


def is_in_vercel() -> bool:
    a = os.getenv("VERCEL") == "1"
    return a


def is_in_temboio():
    return os.getenv("VISUALLY_MEASURED_DOWITCHER_TMPBOAI_PORT")


def is_in_windows() -> bool:
    return platform.system() == "Windows"


def backend_url_base():
    from mtmai.core.config import settings

    return f"http://localhost:{settings.PORT}"


def is_in_gitpod() -> bool:
    return os.getenv("GITPOD_WORKSPACE_URL")


def is_in_testing():
    return os.getenv("PYTEST_CURRENT_TEST")
