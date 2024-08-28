from fastapi import APIRouter

from mtmai.agents import agent_api
from mtmai.api.routes import (
    agent,
    auth,
    blogwriter,
    chat_input,
    chat_messages,
    completions,
    config,
    dash,
    dataset,
    doccolls,
    items,
    joke,
    metrics,
    mise,
    posts,
    retrieval,
    tasks_queue,
    users,
    utils,
    webhook,
    workspace,
)
from mtmai.core.coreutils import is_in_vercel
from mtmai.teams.storm import storm

api_router = APIRouter()

api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(config.router, prefix="/config", tags=["config"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(mise.router, prefix="/mise", tags=["mise"])
api_router.include_router(joke.router, prefix="/joke", tags=["joke"])
api_router.include_router(blogwriter.router, prefix="/blogwriter", tags=["blogwriter"])
api_router.include_router(retrieval.router, prefix="/retrieval", tags=["retrieval"])
api_router.include_router(doccolls.router, prefix="/doccolls", tags=["doccolls"])
api_router.include_router(dash.router, prefix="/dash", tags=["dash"])
api_router.include_router(dataset.router, prefix="/dataset", tags=["dataset"])
api_router.include_router(webhook.router, prefix="/webhook", tags=["webhook"])

api_router.include_router(
    completions.router, prefix="/completions", tags=["completions"]
)
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])

api_router.include_router(
    chat_messages.router, prefix="/chat_messages", tags=["chat_messages"]
)
api_router.include_router(workspace.router, prefix="/workspace", tags=["workspace"])
api_router.include_router(chat_input.router, prefix="/chat_input", tags=["chat_input"])
api_router.include_router(agent.router, prefix="/agents", tags=["agents"])
api_router.include_router(agent_api.router, prefix="/agent_api", tags=["agent_api"])

api_router.include_router(storm.router, prefix="/storm", tags=["storm"])
api_router.include_router(
    tasks_queue.router, prefix="/tasks_queue", tags=["tasks_queue"]
)


if not is_in_vercel():
    from mtmai.api.routes import admin

    api_router.include_router(
        admin.router,
        prefix="/admin",
        tags=["admin"],
    )

    from mtmai.api.routes import search

    api_router.include_router(search.router, prefix="/search", tags=["search"])

    from mtmai.api.serve import tunnel

    api_router.include_router(tunnel.router, prefix="/tunnel", tags=["tunnel"])

    from mtmai.api.serve import vnc

    api_router.include_router(vnc.router, prefix="/vnc", tags=["vnc"])

    from mtmai.api.demos import demo_pgmq

    api_router.include_router(demo_pgmq.router, prefix="/demo_pgmq", tags=["demo_pgmq"])

    from mtmai.api.serve import codeserver

    api_router.include_router(
        codeserver.router, prefix="/codeserver", tags=["codeserver"]
    )

    from mtmai.api.demos import demos

    api_router.include_router(demos.router, prefix="/demos/demos", tags=["demos_demos"])

    from mtmai.trans import trans_api

    api_router.include_router(trans_api.router, prefix="/trans", tags=["trans"])

    from mtmai.api.serve import front

    api_router.include_router(front.router, prefix="/front", tags=["front"])
    from mtmai.api.serve import worker

    api_router.include_router(worker.router, prefix="/worker", tags=["worker"])
