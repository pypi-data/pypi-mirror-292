import asyncio
import logging
from pathlib import Path

from mtmlib.version_tag import patch_git_tag_version, read_tag

from mtmai.core import coreutils
from mtmai.core.config import settings
from mtmai.mtlibs import mtutils
from mtmai.mtlibs.mtutils import command_exists, is_in_gitpod, npm_patch_version
from mtmai.mtlibs.process_helper import bash
from mtmai.mtlibs.temboio import run_tmpbo_instance1

from . import huggingface

logger = logging.getLogger()


def init_project():
    if not coreutils.is_in_gitpod():
        return

    if not mtutils.command_exists("bun"):
        bash("curl -fsSL https://bun.sh/install | bash")
    if not Path("./node_modules").exists():
        bash("bun i")

    if not Path(".env").exists():
        bash("cp env/dev.env .env")

    docker_config = Path.home().joinpath(".docker/config.json")
    if settings.DOCKERHUB_PASSWORD and not docker_config.exists():
        bash(
            f"(command -v docker && echo {settings.DOCKERHUB_PASSWORD} | docker login --username {settings.DOCKERHUB_USER} --password-stdin) || true"
        )

    if settings.NPM_TOKEN:
        npmrc = Path.home().joinpath(".npmrc")
        npmrc.write_text(f"//registry.npmjs.org/:_authToken={settings.NPM_TOKEN}\n")

    huggingface.hf_trans1_clone()


def hf_trans1_commit():
    target_dir = (
        Path(settings.storage_dir)
        .joinpath(settings.gitsrc_dir)
        .joinpath(settings.HUGGINGFACEHUB_DEFAULT_WORKSPACE)
    )
    rnd_str = mtutils.gen_orm_id_key()
    Path(target_dir).joinpath("Dockerfile").write_text(f"""
# {rnd_str}
FROM docker.io/gitgit188/tmpboai
ENV DATABASE_URL={settings.DATABASE_URL}
ENV LOKI_USER={settings.LOKI_USER}
ENV GRAFANA_TOKEN={settings.GRAFANA_TOKEN}
ENV LOKI_ENDPOINT={settings.LOKI_ENDPOINT}


RUN sudo apt update

""")
    Path(target_dir).joinpath("README.md").write_text(f"""---
title: Trans1
emoji: 🏢
colorFrom: red
colorTo: gray
sdk: docker
pinned: false
license: other
app_port:  {settings.FRONT_PORT}
---""")
    bash(f"cd {target_dir} && git commit -am abccommit && git push")
    return {"ok": True}


def release_pip_package():
    bash("poetry config repositories.pypi https://pypi.org/legacy/")
    bash(f"poetry config pypi-token.pypi {settings.POETRY_PYPI_TOKEN_PYPI}")
    bash("poetry publish")


def run_clean():
    bun_cache_dir = Path.home().joinpath(".bun/install/cache")
    bash(f"rm -rdf {bun_cache_dir}")

    if command_exists("pip"):
        logging.info("正在清理 pip 缓存")
        bash("pip cache dir && pip cache purge")
    if command_exists("docker"):
        logging.info("正在清理 docker 缓存")
        bash("docker system prune -f")

    if command_exists("pyenv"):
        bash("pyenv rehash")  # 可能不正确
    if is_in_gitpod():
        logger.info("删除 ~/.rustup")
        bash("rm -rdf ~/.rustup")
        logger.info("删除 ~/.rvm")
        dotrvm = Path.home().joinpath(".rvm")
        if dotrvm.exists():
            bash("rm -rdf ~/.rvm")


def docker_build_base():
    logger.info("🚀 build docker image_base")
    image_tag = f"{settings.DOCKERHUB_USER}/base"
    bash(
        f"docker build --progress=plain -t {image_tag} -f Dockerfile.base . && docker push {image_tag}"
    )
    logger.info("✅ build docker image_base")


def run_deploy():
    asyncio.run(run_tmpbo_instance1())
    logger.info("✅ tembo io pushed")

    hf_trans1_commit()
    logger.info("✅ hf_space_commit")


py_projects = ["mtmai", "mtmdb", "mtmlib", "mtmtrain", "mtmai-client"]


def release_py():
    gen()
    version_tag = read_tag()
    logger.info("version tag: %s", version_tag)
    for project in py_projects:
        testing_dir = Path(f"{project}/{project}/tests")
        if testing_dir.exists():
            bash(f"cd {project} && coverage run -m pytest ")
            logger.info("✅ testing ok!")

        dist_dir = Path(f"{project}/dist")
        if dist_dir.exists():
            bash(f"rm -rdf {dist_dir}")
        bash(f"cd {project} && poetry build")

    for project in py_projects:
        bash(f"cd {project} && poetry publish")

    for project in py_projects:
        mtutils.pyproject_patch_version(project)

    release_npm()
    next_version = patch_git_tag_version()
    logger.info("✅ patch_git_tag_version ok!,next version tag: %s", next_version)


def release_npm():
    npm_packages = ["apps/mtmaiweb"]

    bash("bun run turbo build")

    for package in npm_packages:
        npm_patch_version(package)
    bash("bun run changeset publish --no-git-tag")
    logger.info("✅ release_npm ok!")


def dp_cfpage():
    from mtmlib import vercel

    vercel.deploy_vercel(
        project_dir="apps/mtmaiweb",
        is_cfpage=True,
        project_name="mtmaiweb",
        vercel_token=settings.vercel_token,
    )


def gen():
    """生产相关客户端代码"""
    # python 客户端库
    if not mtutils.command_exists("openapi-python-client"):
        bash(
            "pip install openapi-python-client && openapi-python-client --install-completion"
        )
    bash("openapi-python-client generate --path mtmai/mtmai/openapi.json --overwrite")

    # typescript 客户端库
    bash("cd packages/mtmaiapi && bun run gen")
