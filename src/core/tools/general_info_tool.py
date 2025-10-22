from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field

from core.base_tool import BaseTool

if TYPE_CHECKING:
    from core.models import ResearchContext


class GeneralInfoTool(BaseTool):
    """Tool for general university information queries using knowledge base or RAG system."""

    query: str = Field(description="User's question or information request")
    category: str | None = Field(
        default=None,
        description="Category of query: 'admission', 'contacts', 'departments', 'events', 'rules', 'services', or 'general'",
    )
    keywords: list[str] | None = Field(default=None, description="Key terms or concepts to search for in knowledge base")
    context_needed: bool = Field(default=True, description="Whether to include contextual information from knowledge base")

    async def __call__(self, context: "ResearchContext") -> str:
        # TODO: Implement actual RAG/knowledge base retrieval
        # This should integrate with vector store, knowledge base, or RAG system
        # This is a stub implementation
        result = {
            "query": self.query,
            "category": self.category or "general",
            "keywords": self.keywords or [],
            "retrieved_info": {
                "source": "Knowledge Base",
                "relevance_score": 0.95,
                "content": "This is a stub answer. Real information will be retrieved from RAG system or knowledge base.",
                "sources": ["Document 1", "Document 2"],
            },
            "note": "This is a stub implementation. Real data will be retrieved from RAG/vector store.",
        }
        return self.model_dump_json(indent=2) + f"\n\nStub Result: {result}"
