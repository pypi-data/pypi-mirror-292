import argparse
import asyncio
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from starlette.templating import Jinja2Templates

sys.path.insert(0, str(Path("./mtmlib").absolute()))
sys.path.insert(0, str(Path("./mtmtrain").absolute()))

from mtmai.api.main import api_router
from mtmai.api.routes import home
from mtmai.core.__version__ import version
from mtmai.core.config import settings
from mtmai.core.coreutils import is_in_vercel
from mtmai.core.logging import setup_logging
from mtmai.core.seed import init_database

# print(sys.path)
setup_logging()
load_dotenv()
logger = logging.getLogger(__name__)

logger.info(f"[mtmai]({settings.VERSION}) app starting...")  # noqa: G004


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    if not is_in_vercel():
        init_database()
    yield


def custom_generate_unique_id(route: APIRoute) -> str:
    if len(route.tags) > 0:
        return f"{route.tags[0]}-{route.name}"
    return f"{route.name}"


openapi_tags = [
    {
        "name": "admin",
        "description": "这部分API与管理员操作相关, 包括用户管理和权限控制等功能. ",
    },
]

app = FastAPI(
    # docs_url=None,
    # redoc_url=None,
    title=settings.PROJECT_NAME,
    description="mtmai description(group)",
    version=version,
    lifespan=lifespan,
    generate_unique_id_function=custom_generate_unique_id,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    swagger_ui_parameters={
        "syntaxHighlight": True,
        "syntaxHighlight.theme": "obsidian",
    },
    openapi_tags=openapi_tags,
)
templates = Jinja2Templates(directory="templates")


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):  # noqa: ARG001
    return JSONResponse(status_code=500, content={"detail": str(exc)})


logger.info("setup routes")
app.include_router(home.router)
app.include_router(api_router, prefix=settings.API_V1_STR)


if settings.OTEL_ENABLED:
    from mtmai.mtlibs import otel

    otel.setup_otel(app)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

if not is_in_vercel():
    from mtmai.api.serve import rproxy

    app.include_router(
        rproxy.router,
    )


async def serve():
    import uvicorn

    config = uvicorn.Config(app, host="0.0.0.0", port=8000)  # noqa: S104
    server = uvicorn.Server(config)
    await server.serve()


def main():
    parser = argparse.ArgumentParser(description="mtmai tool")
    parser.add_argument(
        "command",
        help="Specify the command to run, e.g., 'init' to run initialization.",
        nargs="?",  # 可选位置参数
        default="serve",  # 默认命令为 serve
    )

    args = parser.parse_args()
    if args.command == "init":
        from mtmai.mtlibs import dev_helper

        dev_helper.init_project()

    elif args.command == "release":
        from mtmai.mtlibs import dev_helper

        dev_helper.run_release()
    elif args.command == "clean":
        from mtmai.mtlibs import dev_helper

        dev_helper.run_clean()
    elif args.command == "worker":
        from mtmai.worker import worker

        worker.run_worker()

    # elif args.command == "publish_mthellolib":
    #     from mtmai.mtlibs import dev_helper

    #     dev_helper.run_release_mtmlib()

    # elif args.command == "222":
    #     from mtmtrain.text_classify import text_classify

    #     print(text_classify)
    # elif args.command == "333":
    #     print(sys.path)
    #     import mtmlib

    #     print(mtmlib)

    else:
        asyncio.run(serve())


if __name__ == "__main__":
    main()
