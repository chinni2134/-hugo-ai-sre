from sqlalchemy.orm import Session

from app.models.telemetry import TelemetryRecord


class TelemetryQueryService:

    @staticmethod
    def latest(
        db: Session,
        entity_id: str,
        limit: int = 20,
    ):

        records = (
            db.query(TelemetryRecord)
            .filter(
                TelemetryRecord.entity_id == entity_id
            )
            .order_by(
                TelemetryRecord.collected_at.desc()
            )
            .limit(limit)
            .all()
        )

        return [
            {
                "entity_id": record.entity_id,
                "status": record.status,
                "cpu_percent": record.cpu_percent,
                "memory_percent": record.memory_percent,
                "collected_at": record.collected_at,
            }
            for record in records
        ]
