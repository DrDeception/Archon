"""Project service backed by SQLite.

This module provides a greatly simplified replacement for the previous
Supabase based implementation.  Only a subset of the original behaviour
is currently supported: creating, listing, retrieving and deleting
projects.  The goal is to keep the local demo lightweight while retaining
the core project–management features.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from ..client_manager import SQLiteCursorContext
from ...config.logfire_config import get_logger

logger = get_logger(__name__)


@dataclass
class Project:
    title: str
    github_repo: str | None = None
    created_at: str = datetime.now().isoformat()
    updated_at: str = datetime.now().isoformat()
    id: int | None = None


class ProjectService:
    """Service class for project operations using SQLite."""

    def __init__(self, db_context: type[SQLiteCursorContext] = SQLiteCursorContext):
        self.db_context = db_context

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------

    def create_project(self, title: str, github_repo: str | None = None) -> tuple[bool, dict[str, Any]]:
        """Create a new project."""

        if not title or not isinstance(title, str):
            return False, {"error": "Project title is required"}

        project = Project(title=title.strip(), github_repo=github_repo)

        with self.db_context() as cur:
            cur.execute(
                """
                INSERT INTO archon_projects (title, github_repo, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (project.title, project.github_repo, project.created_at, project.updated_at),
            )
            project.id = cur.lastrowid

        logger.info("Project created", project_id=project.id)
        return True, {"project": asdict(project)}

    def list_projects(self) -> tuple[bool, dict[str, Any]]:
        """Return all projects ordered by creation date."""

        with self.db_context() as cur:
            cur.execute(
                "SELECT id, title, github_repo, created_at, updated_at FROM archon_projects ORDER BY created_at DESC"
            )
            rows = [dict(row) for row in cur.fetchall()]

        return True, {"projects": rows, "total_count": len(rows)}

    def get_project(self, project_id: int) -> tuple[bool, dict[str, Any]]:
        """Get a project by its ID."""

        with self.db_context() as cur:
            cur.execute(
                "SELECT id, title, github_repo, created_at, updated_at FROM archon_projects WHERE id = ?",
                (project_id,),
            )
            row = cur.fetchone()

        if row is None:
            return False, {"error": f"Project with ID {project_id} not found"}

        return True, {"project": dict(row)}

    def delete_project(self, project_id: int) -> tuple[bool, dict[str, Any]]:
        """Delete a project by ID."""

        with self.db_context() as cur:
            cur.execute("DELETE FROM archon_projects WHERE id = ?", (project_id,))
            deleted = cur.rowcount

        if deleted:
            logger.info("Project deleted", project_id=project_id)
            return True, {"deleted": project_id}
        return False, {"error": f"Project with ID {project_id} not found"}


__all__ = ["ProjectService", "Project"]

