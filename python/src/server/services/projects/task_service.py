"""Task service backed by SQLite.

Only the essentials for a Kanban style workflow are implemented.  The
service intentionally mirrors the simplified :mod:`ProjectService`.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from ..client_manager import SQLiteCursorContext
from ...config.logfire_config import get_logger

logger = get_logger(__name__)


class TaskService:
    VALID_STATUSES = ["todo", "doing", "review", "done"]

    def __init__(self, db_context: type[SQLiteCursorContext] = SQLiteCursorContext):
        self.db_context = db_context

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------

    def create_task(
        self,
        project_id: int,
        title: str,
        description: str = "",
        status: str = "todo",
        assignee: str = "User",
    ) -> tuple[bool, dict[str, Any]]:
        if status not in self.VALID_STATUSES:
            return False, {"error": f"Invalid status '{status}'"}

        with self.db_context() as cur:
            cur.execute(
                """
                INSERT INTO archon_tasks (project_id, title, description, status, assignee, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    title,
                    description,
                    status,
                    assignee,
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )
            task_id = cur.lastrowid

        return True, {"task": {"id": task_id, "title": title, "status": status}}

    def list_tasks(self, project_id: int | None = None) -> tuple[bool, dict[str, Any]]:
        query = "SELECT * FROM archon_tasks"
        params: tuple[Any, ...] = ()
        if project_id is not None:
            query += " WHERE project_id = ?"
            params = (project_id,)

        with self.db_context() as cur:
            cur.execute(query, params)
            rows = [dict(r) for r in cur.fetchall()]

        return True, {"tasks": rows, "total_count": len(rows)}

    def update_status(self, task_id: int, status: str) -> tuple[bool, dict[str, Any]]:
        if status not in self.VALID_STATUSES:
            return False, {"error": f"Invalid status '{status}'"}

        with self.db_context() as cur:
            cur.execute(
                "UPDATE archon_tasks SET status = ?, updated_at = ? WHERE id = ?",
                (status, datetime.now().isoformat(), task_id),
            )
            if cur.rowcount == 0:
                return False, {"error": f"Task with ID {task_id} not found"}

        return True, {"task": {"id": task_id, "status": status}}


__all__ = ["TaskService"]

