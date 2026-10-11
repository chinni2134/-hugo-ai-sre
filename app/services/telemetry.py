import docker

from sqlalchemy.orm import Session

from app.models.telemetry import TelemetryRecord


class TelemetryCollector:

    def __init__(self):
        self.client = docker.from_env()

    def collect(self, db: Session):

        results = []

        for container in self.client.containers.list():

            stats = container.stats(
                stream=False
            )

            cpu = self._cpu_percent(stats)
            memory = self._memory_percent(stats)

            record = TelemetryRecord(
                entity_id=f"docker:{container.id}",
                status=container.status,
                cpu_percent=cpu,
                memory_percent=memory,
            )

            db.add(record)

            results.append(
                {
                    "name": container.name,
                    "status": container.status,
                    "cpu_percent": cpu,
                    "memory_percent": memory,
                }
            )

        db.commit()

        return results

    @staticmethod
    def _cpu_percent(stats):

        cpu_delta = (
            stats["cpu_stats"]["cpu_usage"]["total_usage"]
            -
            stats["precpu_stats"]["cpu_usage"]["total_usage"]
        )

        system_delta = (
            stats["cpu_stats"]["system_cpu_usage"]
            -
            stats["precpu_stats"]["system_cpu_usage"]
        )

        if system_delta <= 0:
            return 0.0

        online_cpus = stats["cpu_stats"].get(
            "online_cpus",
            1,
        )

        return round(
            (cpu_delta / system_delta)
            * online_cpus
            * 100,
            2,
        )

    @staticmethod
    def _memory_percent(stats):

        usage = stats["memory_stats"].get(
            "usage",
            0,
        )

        limit = stats["memory_stats"].get(
            "limit",
            1,
        )

        if limit <= 0:
            return 0.0

        return round(
            (usage / limit) * 100,
            2,
        )

    def close(self):
        self.client.close()


telemetry_collector = TelemetryCollector()
