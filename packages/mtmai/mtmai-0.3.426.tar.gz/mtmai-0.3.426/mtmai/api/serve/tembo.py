import asyncio
import json
import logging
from pathlib import Path

import httpx
from fastapi import APIRouter
from mtmlib.mtutils import bash

from mtmai.core.config import settings
from mtmai.mtlibs import mtutils

router = APIRouter()

logger = logging.getLogger()


# api 文档:  https://api.tembo.io/swagger-ui/#/instance/patch_instance


async def docker_build_mtmai():
    container_image_name = "docker.io/gitgit188/tmpboai"
    project_version = mtutils.get_pyproject_version("mtmai")
    await asyncio.to_thread(
        bash,
        f"""docker build --progress=plain -t {container_image_name} --target temboapi . \
        && docker push {container_image_name} \
        && docker tag {container_image_name} {container_image_name}:{project_version}\
        && docker push {container_image_name}:{project_version} """,
    )


async def run_tmpbo_instance1():
    project_version = mtutils.get_pyproject_version("mtmai")
    logger.info("当前项目版本 %s", project_version)
    container_image_name = "docker.io/gitgit188/tmpboai"
    await asyncio.to_thread(
        bash,
        "cd mtmai && poetry export --format requirements.txt --output requirements.txt --without-hashes --without dev",
    )
    await docker_build_mtmai()

    logger.info("应用 tembo %s/%s", settings.TEMBO_ORG, settings.TEMBO_INST)

    async with httpx.AsyncClient() as client:
        resp = await client.patch(
            url=f"https://api.tembo.io/api/v1/orgs/{settings.TEMBO_ORG}/instances/{settings.TEMBO_INST}",
            headers={"Authorization": f"Bearer {settings.TEMBO_TOKEN}"},
            json={
                "app_services": [
                    {
                        "custom": {
                            "image": f"{container_image_name}:{project_version}",
                            "name": "tmpboaiv3",
                            "routing": [
                                {
                                    "port": 8000,
                                    "ingressPath": "/api",
                                },
                            ],
                            "env": [
                                # {"name": "PORT", "value": "8000"},
                                {"name": "INTEMBO", "value": "1"},
                                {
                                    "name": "DATABASE_URL",
                                    "value": settings.DATABASE_URL,
                                },
                                {
                                    "name": "CF_TUNNEL_TOKEN",
                                    "value": settings.CF_TUNNEL_TOKEN_TEMBO,
                                },
                                {
                                    "name": "MAIN_GH_TOKEN",
                                    "value": settings.MAIN_GH_TOKEN,
                                },
                                {
                                    "name": "MAIN_GH_USER",
                                    "value": settings.MAIN_GH_USER,
                                },
                            ],
                            "resources": {
                                "requests": {"cpu": "500m", "memory": "2000Mi"},
                                "limits": {"cpu": "4000m", "memory": "4000Mi"},
                            },
                            "storage": {
                                "volumeMounts": [
                                    {
                                        "mountPath": "/app/storage",
                                        "name": "hf-model-vol",
                                    },
                                    {
                                        "mountPath": "/home/user",
                                        "name": "user-home",
                                    },
                                    {
                                        "mountPath": "/tmp",
                                        "name": "tmp",
                                    },
                                ],
                                "volumes": [
                                    {
                                        "name": "hf-model-vol",
                                        "ephemeral": {
                                            "volumeClaimTemplate": {
                                                "spec": {
                                                    "accessModes": ["ReadWriteOnce"],
                                                    "resources": {
                                                        "requests": {"storage": "2Gi"}
                                                    },
                                                }
                                            }
                                        },
                                    },
                                    {
                                        "name": "user-home",
                                        "ephemeral": {
                                            "volumeClaimTemplate": {
                                                "spec": {
                                                    "accessModes": ["ReadWriteOnce"],
                                                    "resources": {
                                                        "requests": {"storage": "2Gi"}
                                                    },
                                                }
                                            }
                                        },
                                    },
                                    # {
                                    #     "name": "user-root-home",
                                    #     "ephemeral": {
                                    #         "volumeClaimTemplate": {
                                    #             "spec": {
                                    #                 "accessModes": ["ReadWriteOnce"],
                                    #                 "resources": {
                                    #                     "requests": {"storage": "1Gi"}
                                    #                 },
                                    #             }
                                    #         }
                                    #     },
                                    # },
                                    {
                                        "name": "tmp",
                                        "ephemeral": {
                                            "volumeClaimTemplate": {
                                                "spec": {
                                                    "accessModes": ["ReadWriteOnce"],
                                                    "resources": {
                                                        "requests": {"storage": "2Gi"}
                                                    },
                                                }
                                            }
                                        },
                                    },
                                ],
                            },
                        }
                    },
                ]
            },
        )
        resp.raise_for_status()

    json_data = resp.json()
    logger.info(json_data)
    mtutils.pyproject_patch_version()

    log_file1 = "./tembo1.log"
    Path(log_file1).write_text(json.dumps(json_data, indent=2))
    return json_data
