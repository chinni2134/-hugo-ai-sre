from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.telemetry import TelemetryRecord


class IncidentDetectionService:

    @staticmethod
    def detect(db: Session):

        latest_records = {}

        records = (
            db.query(TelemetryRecord)
            .order_by(TelemetryRecord.collected_at.desc())
            .all()
        )

        for record in records:
            if record.entity_id not in latest_records:
                latest_records[record.entity_id] = record

        incidents = []

        for entity_id, record in latest_records.items():

            severity = None
            title = None
            description = None

            if record.memory_percent >= 90:
                severity = "high"
                title = "High memory utilization"
                description = (
                    f"Memory utilization reached "
                    f"{record.memory_percent}%."
                )

            elif record.cpu_percent >= 80:
                severity = "high"
                title = "High CPU utilization"
                description = (
                    f"CPU utilization reached "
                    f"{record.cpu_percent}%."
                )

            elif record.memory_percent >= 75:
                severity = "medium"
                title = "Elevated memory utilization"
                description = (
                    f"Memory utilization reached "
                    f"{record.memory_percent}%."
                )

            elif record.cpu_percent >= 60:
                severity = "medium"
                title = "Elevated CPU utilization"
                description = (
                    f"CPU utilization reached "
                    f"{record.cpu_percent}%."
                )

            if severity is None:
                continue

            existing = (
                db.query(Incident)
                .filter(
                    Incident.entity_id == entity_id,
                    Incident.status == "open",
                    Incident.title == title,
                )
                .first()
            )

            if existing:
                incidents.append(existing)
                continue

            incident = Incident(
                entity_id=entity_id,
                severity=severity,
                title=title,
                description=description,
                status="open",
            )

            db.add(incident)
            incidents.append(incident)

        db.commit()

        return [
            {
                "id": incident.id,
                "entity_id": incident.entity_id,
                "severity": incident.severity,
                "title": incident.title,
                "description": incident.description,
                "status": incident.status,
            }
            for incident in incidents
        ]
