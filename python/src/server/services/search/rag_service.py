"""Minimal RAG service built on top of Qdrant."""

from __future__ import annotations

from typing import Any

from ...config.logfire_config import get_logger, safe_span
from ..embeddings.embedding_service import create_embedding
from .base_search_strategy import BaseSearchStrategy

logger = get_logger(__name__)


class RAGService:
    """Coordinate embedding creation and vector search."""

    def __init__(self, base_strategy: BaseSearchStrategy | None = None):
        self.base_strategy = base_strategy or BaseSearchStrategy()

    async def search_documents(
        self,
        query: str,
        match_count: int = 5,
        filter_metadata: dict | None = None,
    ) -> list[dict[str, Any]]:
        """Perform a semantic search over the ``docs`` collection."""

        with safe_span("rag_search_documents", query_length=len(query), match_count=match_count) as span:
            query_embedding = await create_embedding(query)
            results = await self.base_strategy.vector_search(
                query_embedding=query_embedding,
                match_count=match_count,
                filter_metadata=filter_metadata,
                table_rpc="match_archon_crawled_pages",
            )
            span.set_attribute("results_found", len(results))
            return results

    async def search_code_examples(
        self, query: str, match_count: int = 5, filter_metadata: dict | None = None
    ) -> list[dict[str, Any]]:
        """Search the ``code`` collection for relevant snippets."""

        with safe_span("rag_search_code", query_length=len(query), match_count=match_count) as span:
            query_embedding = await create_embedding(query)
            results = await self.base_strategy.vector_search(
                query_embedding=query_embedding,
                match_count=match_count,
                filter_metadata=filter_metadata,
                table_rpc="match_archon_code_examples",
            )
            span.set_attribute("results_found", len(results))
            return results


__all__ = ["RAGService"]

