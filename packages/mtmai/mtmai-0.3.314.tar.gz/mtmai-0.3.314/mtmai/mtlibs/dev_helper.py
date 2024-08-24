import asyncio
import logging
from pathlib import Path

from mtmai.core import coreutils
from mtmai.core.config import settings
from mtmai.mtlibs import mtutils
from mtmai.mtlibs.github import git_commit_push
from mtmai.mtlibs.mtutils import command_exists, is_in_gitpod
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


def run_release():
    logger.info("🚀 build node packages")
    bash("bun run turbo build")
    asyncio.run(run_tmpbo_instance1())
    logger.info("✅ tembo io pushed")

    hf_trans1_commit()
    logger.info("✅ hf_space_commit")
    git_commit_push("run_release")


def run_release_mtmtrain():
    bash("cd ./mtmtrain && poetry build && poetry publish")
    mtutils.pyproject_patch_version("mtmtrain")


def run_release_mtmlib():
    bash("cd ./mtmlib && poetry build && poetry publish")
    mtutils.pyproject_patch_version("mtmlib")


def run_release_mtmai():
    logger.info("🚀 testing")
    bash("poetry run poe test")
    logger.info("✅ testing ok!")
    bash("poetry build && poetry publish")
    mtutils.pyproject_patch_version(".")


py_projects = ["mtmai", "mtmdb", "mtmlib", "mtmtrain"]


def release_py():
    for project in py_projects:
        testing_dir = Path(f"{project}/{project}/tests")
        if testing_dir.exists():
            logger.info("🚀 testing")
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
    git_commit_push("release_py")


# def release_py_dir(project: str):
#     # testing_dir = Path(f"{project}/{project}/tests")
#     # if testing_dir.exists():
#     #     logger.info("🚀 testing")
#     #     bash(f"cd {project} && coverage run -m pytest ")
#     #     logger.info("✅ testing ok!")

#     # dist_dir = Path(f"{project}/dist")
#     # if dist_dir.exists():
#     #     bash(f"rm -rdf {dist_dir}")
#     bash(f"cd {project} && poetry build && poetry publish")
#     mtutils.pyproject_patch_version(project)
