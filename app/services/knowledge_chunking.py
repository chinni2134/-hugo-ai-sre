from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.knowledge import KnowledgeDocument
from app.models.knowledge_chunk import KnowledgeChunk
from app.services.embedding import embedding_service


class KnowledgeChunkingService:
    DEFAULT_CHUNK_SIZE = 500
    DEFAULT_OVERLAP = 50

    @classmethod
    def chunk_text(
        cls,
        content: str,
        chunk_size: int | None = None,
        overlap: int | None = None,
    ) -> list[str]:

        chunk_size = chunk_size or cls.DEFAULT_CHUNK_SIZE
        overlap = overlap or cls.DEFAULT_OVERLAP

        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

        if overlap < 0:
            raise ValueError("overlap cannot be negative")

        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

        content = " ".join(content.strip().split())

        if not content:
            return []

        words = content.split()

        chunks = []
        current_words = []
        current_length = 0

        for word in words:
            additional_length = len(word) + (1 if current_words else 0)

            if current_words and current_length + additional_length > chunk_size:
                chunks.append(" ".join(current_words))

                overlap_words = []
                overlap_length = 0

                for previous_word in reversed(current_words):
                    extra = len(previous_word) + (
                        1 if overlap_words else 0
                    )

                    if overlap_length + extra > overlap:
                        break

                    overlap_words.insert(0, previous_word)
                    overlap_length += extra

                current_words = overlap_words
                current_length = len(" ".join(current_words))

            current_words.append(word)
            current_length = len(" ".join(current_words))

        if current_words:
            chunks.append(" ".join(current_words))

        return chunks

    @classmethod
    def create_chunks_for_document(
        cls,
        db: Session,
        document: KnowledgeDocument,
        chunk_size: int | None = None,
        overlap: int | None = None,
    ) -> list[KnowledgeChunk]:

        chunks = cls.chunk_text(
            content=document.content,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        existing_chunks = (
            db.query(KnowledgeChunk)
            .filter(
                KnowledgeChunk.document_id == document.document_id
            )
            .all()
        )

        for existing_chunk in existing_chunks:
            db.delete(existing_chunk)

        db.flush()

        embeddings = embedding_service.embed_texts(chunks)

        records = []

        for index, (content, embedding) in enumerate(
            zip(chunks, embeddings)
        ):
            record = KnowledgeChunk(
                chunk_id=f"chunk:{uuid4()}",
                document_id=document.document_id,
                chunk_index=index,
                content=content,
                embedding=embedding,
            )

            db.add(record)
            records.append(record)

        db.commit()

        for record in records:
            db.refresh(record)

        return records
