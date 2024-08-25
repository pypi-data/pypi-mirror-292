import logging
from pathlib import Path

from fastapi import APIRouter

from mtmai.core.config import settings
from mtmai.mtlibs.process_helper import bash

router = APIRouter()
logger = logging.getLogger(__name__)


# @router.get(
#     "/hf_space_clone",
#     dependencies=[Depends(get_current_active_superuser)],
#     status_code=201,
# )
def hf_trans1_clone():
    target_dir = (
        Path(settings.storage_dir)
        .joinpath(settings.gitsrc_dir)
        .joinpath(settings.HUGGINGFACEHUB_DEFAULT_WORKSPACE)
    )
    if not Path(target_dir).exists():
        cmd = f"git clone --depth=1 https://{settings.HUGGINGFACEHUB_USER}:{settings.HUGGINGFACEHUB_API_TOKEN}@huggingface.co/spaces/{settings.HUGGINGFACEHUB_USER}/{settings.HUGGINGFACEHUB_DEFAULT_WORKSPACE} {target_dir}"
        bash(cmd)
