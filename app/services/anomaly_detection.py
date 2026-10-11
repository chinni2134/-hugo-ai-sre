from sqlalchemy.orm import Session

from app.models.telemetry import TelemetryRecord


class AnomalyDetectionService:

    @staticmethod
    def analyze(
        db: Session,
        entity_id: str,
    ):

        records = (
            db.query(TelemetryRecord)
            .filter(
                TelemetryRecord.entity_id == entity_id
            )
            .order_by(
                TelemetryRecord.collected_at.desc()
            )
            .limit(20)
            .all()
        )

        if not records:
            return {
                "entity_id": entity_id,
                "status": "no_data",
                "anomalies": [],
            }

        anomalies = []

        latest = records[0]

        if latest.cpu_percent >= 80:
            anomalies.append({
                "metric": "cpu_percent",
                "value": latest.cpu_percent,
                "threshold": 80,
                "severity": "high",
            })

        elif latest.cpu_percent >= 60:
            anomalies.append({
                "metric": "cpu_percent",
                "value": latest.cpu_percent,
                "threshold": 60,
                "severity": "medium",
            })

        if latest.memory_percent >= 90:
            anomalies.append({
                "metric": "memory_percent",
                "value": latest.memory_percent,
                "threshold": 90,
                "severity": "high",
            })

        elif latest.memory_percent >= 75:
            anomalies.append({
                "metric": "memory_percent",
                "value": latest.memory_percent,
                "threshold": 75,
                "severity": "medium",
            })

        return {
            "entity_id": entity_id,
            "status": "anomaly" if anomalies else "normal",
            "anomalies": anomalies,
            "latest": {
                "cpu_percent": latest.cpu_percent,
                "memory_percent": latest.memory_percent,
                "collected_at": latest.collected_at,
            },
        }
