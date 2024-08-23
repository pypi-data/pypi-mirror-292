import asyncio
import logging
from pathlib import Path

from mtmai.core import coreutils
from mtmai.core.config import settings
from mtmai.mtlibs import mtutils
from mtmai.mtlibs.github import git_commit_push
from mtmai.mtlibs.mtutils import command_exists, get_pyproject_version, is_in_gitpod
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
    if is_in_gitpod():
        logger.info("删除 ~/.rustup")
        bash("rm -rdf ~/.rustup")
        logger.info("删除 ~/.rvm")
        dotrvm = Path.home().joinpath(".rvm")
        if dotrvm.exists():
            bash("rm -rdf ~/.rvm")


def run_release():
    logger.info("🚀 testing")
    bash("poetry run poe test")
    logger.info("✅ testing ok!")
    bash("rm -rdf dist")
    logger.info("🚀 build node packages")

    bash("bun run turbo build")
    asyncio.run(run_tmpbo_instance1())
    logger.info("✅ tembo io pushed")

    hf_trans1_commit()
    logger.info("✅ hf_trans1_commit")
    git_commit_push()

    mtutils.pyproject_patch_version()
    logger.info("✅ version patch new version!")
    logger.info("新版本号 %s", get_pyproject_version())

    bash("poetry build")
    release_pip_package()
    logger.info("✅ pip published")


def run_release_mtmlib():
    bash("cd ./mtmlib && poetry build && poetry publish")
