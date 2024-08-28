import asyncio
import logging
import threading

from fastapi import APIRouter
from opentelemetry import trace

from mtmai.api.deps import SessionDep
from mtmai.worker import worker

tracer = trace.get_tracer_provider().get_tracer(__name__)
logger = logging.getLogger()


router = APIRouter()


@router.get("/start_worker", include_in_schema=False)
async def start_worker(
    session: SessionDep,
):
    threading.Thread(target=lambda: asyncio.run(worker.run_worker(session))).start()
