"""Basic vector search using Qdrant."""

from __future__ import annotations

from typing import Any

from qdrant_client import QdrantClient, models

from ..client_manager import get_qdrant_client
from ...config.logfire_config import get_logger

logger = get_logger(__name__)


class BaseSearchStrategy:
    """Wrapper around :class:`QdrantClient.search`.

    The collection name is determined by the ``table_rpc`` parameter which
    mirrors the previous Supabase RPC function names.  ``match_archon_crawled_pages``
    maps to the ``docs`` collection and ``match_archon_code_examples`` maps to
    ``code``.
    """

    COLLECTION_MAP = {
        "match_archon_crawled_pages": "docs",
        "match_archon_code_examples": "code",
    }

    def __init__(self, client: QdrantClient | None = None):
        self.client = client or get_qdrant_client()

    async def vector_search(
        self,
        query_embedding: list[float],
        match_count: int,
        filter_metadata: dict | None = None,
        table_rpc: str = "match_archon_crawled_pages",
    ) -> list[dict[str, Any]]:
        collection = self.COLLECTION_MAP.get(table_rpc, table_rpc)

        logger.debug(
            "Vector search", collection=collection, match_count=match_count, filter=filter_metadata
        )

        query_filter = None
        if filter_metadata:
            must = [models.FieldCondition(key=k, match=models.MatchValue(v)) for k, v in filter_metadata.items()]
            query_filter = models.Filter(must=must)

        results = self.client.search(
            collection_name=collection,
            query_vector=query_embedding,
            limit=match_count,
            query_filter=query_filter,
        )

        return [
            {
                "id": r.id,
                "score": r.score,
                **(r.payload or {}),
            }
            for r in results
        ]


__all__ = ["BaseSearchStrategy"]

