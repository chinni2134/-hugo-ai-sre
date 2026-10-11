# pyrefly: ignore [missing-import]
# pyrefly: ignore [missing-import]
from sqlalchemy import func  
# pyrefly: ignore [missing-import]       
from sqlalchemy.orm import Session

from app.models.knowledge_chunk import KnowledgeChunk
from app.services.embedding import embedding_service


class RetrievalService:

    @staticmethod
    def search(
        db: Session,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:

        query_embedding = embedding_service.embed_text(query)

        distance = KnowledgeChunk.embedding.cosine_distance(
            query_embedding
        )

        results = (
            db.query(KnowledgeChunk)
            .filter(
                KnowledgeChunk.embedding.is_not(None)
            )
            .order_by(distance)
            .limit(top_k)
            .all()
        )

        return [
            {
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
            }
            for chunk in results
        ]
