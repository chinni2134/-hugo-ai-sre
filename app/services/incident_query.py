from sqlalchemy.orm import Session

from app.models.incident import Incident


class IncidentQueryService:

    @staticmethod
    def list_incidents(
        db: Session,
        status: str | None = None,
    ):

        query = (
            db.query(Incident)
            .order_by(Incident.created_at.desc())
        )

        if status:
            query = query.filter(
                Incident.status == status
            )

        incidents = query.all()

        return [
            {
                "id": incident.id,
                "entity_id": incident.entity_id,
                "severity": incident.severity,
                "title": incident.title,
                "description": incident.description,
                "status": incident.status,
                "created_at": incident.created_at,
            }
            for incident in incidents
        ]
