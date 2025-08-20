"""Client and database connection helpers for local deployment.

This module replaces the previous Supabase/Postgres client with a
lightweight SQLite connection and also exposes a helper to create a
Qdrant client for local vector storage.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Iterator

from qdrant_client import QdrantClient


# ---------------------------------------------------------------------------
# SQLite helpers
# ---------------------------------------------------------------------------

DB_PATH = Path(os.getenv("ARCHON_DB_PATH", "archon.db"))


def get_db() -> sqlite3.Connection:
    """Return a SQLite connection with ``Row`` factory enabled."""

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


class SQLiteCursorContext:
    """Context manager yielding a cursor and committing on exit."""

    def __enter__(self) -> sqlite3.Cursor:  # pragma: no cover - trivial
        self.conn = get_db()
        self.cur = self.conn.cursor()
        return self.cur

    def __exit__(self, exc_type, exc, tb):  # pragma: no cover - trivial
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.conn.close()


# ---------------------------------------------------------------------------
# Qdrant helpers
# ---------------------------------------------------------------------------

QDRANT_PATH = os.getenv("QDRANT_PATH", "./qdrant_db")


def get_qdrant_client() -> QdrantClient:
    """Create a local Qdrant client instance.

    The client stores data on the filesystem under ``QDRANT_PATH`` which
    defaults to ``./qdrant_db``.  Using the file based API keeps deployment
    completely local without any external dependencies.
    """

    return QdrantClient(path=QDRANT_PATH)


__all__ = ["get_db", "get_qdrant_client", "SQLiteCursorContext"]

