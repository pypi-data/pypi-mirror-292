from typing import Literal

from mtmai.core.config import settings


def get_langgraph_checkpointer(
    checkpointer_type: Literal["memory", "postgres"] = "memory",
):
    if checkpointer_type == "postgres":
        from psycopg_pool import ConnectionPool

        from .postgres_saver import PostgresSaver

        pool = ConnectionPool(
            conninfo=str(settings.DATABASE_URL),
            max_size=20,
        )

        checkpointer = PostgresSaver(sync_connection=pool)
        checkpointer.create_tables(pool)
        return checkpointer
    # from langgraph.checkpoint.memory import MemorySaver

    # memory = AsyncSqliteSaver.from_conn_string(":memory:")
    from langgraph.checkpoint.memory import MemorySaver

    memory = MemorySaver()
    return memory
