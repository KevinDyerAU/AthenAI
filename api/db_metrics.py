import time
from typing import Any
from sqlalchemy import event
from flask_sqlalchemy import SQLAlchemy
from .metrics import record_database_operation


def init_sqlalchemy_metrics(db: SQLAlchemy) -> None:
    """Attach SQLAlchemy listeners to emit Prometheus metrics for Postgres queries."""
    if not hasattr(db, "engine"):
        # engine will be available after first use or within app context
        return

    @event.listens_for(db.engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):  # type: ignore[no-untyped-def]
        context._query_start_time = time.time()

    @event.listens_for(db.engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):  # type: ignore[no-untyped-def]
        start = getattr(context, "_query_start_time", None)
        if start is None:
            return
        dur = time.time() - start
        # Basic classification of operation type
        op = "other"
        s = statement.strip().lower()
        if s.startswith("select"):
            op = "select"
        elif s.startswith("insert"):
            op = "insert"
        elif s.startswith("update"):
            op = "update"
        elif s.startswith("delete"):
            op = "delete"
        record_database_operation("postgres", op, dur, success=True)

    @event.listens_for(db.engine, "handle_error")
    def handle_error(context):  # type: ignore[no-untyped-def]
        # Called when an execution error occurs
        start = getattr(context.execution_context, "_query_start_time", None)
        if start is not None:
            dur = time.time() - start
            statement = (context.statement or "").strip().lower()
            op = "other"
            if statement.startswith("select"):
                op = "select"
            elif statement.startswith("insert"):
                op = "insert"
            elif statement.startswith("update"):
                op = "update"
            elif statement.startswith("delete"):
                op = "delete"
            record_database_operation("postgres", op, dur, success=False)
        # Let SQLAlchemy continue raising the error
        return None
