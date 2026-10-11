from sqlalchemy.orm import Session

from app.models.system import SystemEntity
from app.services.dependency import DependencyService


class TopologyService:

    @staticmethod
    def sync_entities(db: Session):

        entities = (
            db.query(SystemEntity)
            .order_by(SystemEntity.id)
            .all()
        )

        synced = []

        for entity in entities:

            result = DependencyService.sync_entity(
                entity_id=entity.entity_id,
                name=entity.name,
                entity_type=entity.entity_type,
                environment=entity.environment,
            )

            synced.append(dict(result))

        return synced
