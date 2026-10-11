from sqlalchemy.orm import Session

from app.services.retrieval import RetrievalService


class RAGService:

    @staticmethod
    def build_context(
        db: Session,
        query: str,
        top_k: int = 5,
    ) -> dict:

        results = RetrievalService.search(
            db=db,
            query=query,
            top_k=top_k,
        )

        context = "\n\n".join(
            f"[Knowledge Chunk {index + 1}]\n{result['content']}"
            for index, result in enumerate(results)
        )

        return {
            "query": query,
            "context": context,
            "sources": [
                {
                    "chunk_id": result["chunk_id"],
                    "document_id": result["document_id"],
                    "chunk_index": result["chunk_index"],
                }
                for result in results
            ],
        }
