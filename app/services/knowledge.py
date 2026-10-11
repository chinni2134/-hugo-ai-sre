from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.knowledge import KnowledgeDocument


class KnowledgeService:

    @staticmethod
    def create_document(
        db: Session,
        title: str,
        source: str,
        document_type: str,
        content: str,
        environment: str = "development",
    ) -> KnowledgeDocument:

        document = KnowledgeDocument(
            document_id=f"knowledge:{uuid4()}",
            title=title,
            source=source,
            document_type=document_type,
            content=content,
            environment=environment,
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    @staticmethod
    def get_documents(
        db: Session,
    ) -> list[KnowledgeDocument]:

        return (
            db.query(KnowledgeDocument)
            .order_by(KnowledgeDocument.created_at.desc())
            .all()
        )

    @staticmethod
    def get_document(
        db: Session,
        document_id: str,
    ) -> KnowledgeDocument | None:

        return (
            db.query(KnowledgeDocument)
            .filter(
                KnowledgeDocument.document_id == document_id
            )
            .first()
        )
