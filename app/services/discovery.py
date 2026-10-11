# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session  

from app.models.system import SystemEntity
from app.schemas.system import SystemEntityCreate


class DiscoveryService:

    @staticmethod
    def register_entity(
        db: Session,
        entity: SystemEntityCreate,
    ):
        existing = (
            db.query(SystemEntity)
            .filter(
                SystemEntity.entity_id == entity.entity_id
            )
            .first()
        )

        if existing:
            return existing

        new_entity = SystemEntity(
            entity_id=entity.entity_id,
            name=entity.name,
            entity_type=entity.entity_type,
            environment=entity.environment,
        )

        db.add(new_entity)
        db.commit()
        db.refresh(new_entity)

        return new_entity

    @staticmethod
    def get_entities(db: Session):
        return db.query(SystemEntity).all()