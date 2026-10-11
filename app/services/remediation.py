from sqlalchemy.orm import Session

from app.models.action import RemediationAction
from app.models.incident import Incident


class RemediationService:

    @staticmethod
    def recommend(
        db: Session,
        incident_id: int,
    ):

        incident = (
            db.query(Incident)
            .filter(Incident.id == incident_id)
            .first()
        )

        if not incident:
            return {
                "error": "Incident not found"
            }

        if "CPU" in incident.title:

            action_type = "inspect_cpu_processes"
            description = (
                "Inspect the processes responsible for "
                "elevated CPU utilization."
            )

        elif "memory" in incident.title.lower():

            action_type = "inspect_memory_usage"
            description = (
                "Inspect memory consumers and determine "
                "whether the service requires additional memory."
            )

        else:

            action_type = "investigate"
            description = (
                "Collect additional telemetry and "
                "investigate the affected entity."
            )

        action = RemediationAction(
            incident_id=incident.id,
            action_type=action_type,
            description=description,
            status="proposed",
        )

        db.add(action)
        db.commit()
        db.refresh(action)

        return {
            "action_id": action.id,
            "incident_id": action.incident_id,
            "action_type": action.action_type,
            "description": action.description,
            "status": action.status,
        }
