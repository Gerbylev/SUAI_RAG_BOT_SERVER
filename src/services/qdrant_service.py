from typing import List, Dict, Any

from openai import AsyncOpenAI
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, ScoredPoint

from utils.config import CONFIG
from utils.logger import get_logger

logger = get_logger("QdrantService")


class QdrantService:

    def __init__(self):
        self.client = AsyncQdrantClient(
            host=CONFIG.qdrant.host,
            port=CONFIG.qdrant.port,
            api_key=CONFIG.qdrant.api_key if CONFIG.qdrant.api_key else None,
        )
        self.embeddings_client = AsyncOpenAI(
            api_key=CONFIG.embeddings.api_key,
            base_url=CONFIG.embeddings.base_url,
        )
        self.embeddings_model = CONFIG.embeddings.model

    async def get_embedding(self, text: str) -> List[float]:
        try:
            response = await self.embeddings_client.embeddings.create(
                model=self.embeddings_model,
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Ошибка при получении эмбединга: {e}")
            raise

    async def search(
        self, collection_name: str, query: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        try:
            query_embedding = await self.get_embedding(query)

            results: List[ScoredPoint] = await self.client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=limit,
            )

            documents = []
            for result in results:
                documents.append({
                    "id": result.id,
                    "score": result.score,
                    "text": result.payload.get("text", ""),
                    "metadata": {
                        k: v for k, v in result.payload.items() if k != "text"
                    },
                })

            logger.info(f"Найдено {len(documents)} документов в коллекции {collection_name}")
            return documents

        except Exception as e:
            logger.error(f"Ошибка при поиске документов: {e}")
            raise


qdrant_service = QdrantService()