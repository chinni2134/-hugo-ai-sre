import docker

# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.models.system import SystemEntity


class DockerDiscovery:

    def __init__(self):
        self.client = docker.from_env()

    def discover_containers(self):
        containers = self.client.containers.list(all=True)

        discovered = []

        for container in containers:

            image_tags = container.image.tags

            discovered.append(
                {
                    "container_id": container.id,
                    "name": container.name,
                    "image": image_tags,
                    "status": container.status,
                    "ports": container.ports,
                }
            )

        return discovered

    def sync_to_database(self, db: Session):

        containers = self.discover_containers()

        synced = []

        for container in containers:

            entity_id = f"docker:{container['container_id']}"

            existing = (
                db.query(SystemEntity)
                .filter(
                    SystemEntity.entity_id == entity_id
                )
                .first()
            )

            if existing:

                existing.name = container["name"]
                existing.entity_type = "docker_container"

                synced.append(existing)

                continue

            entity = SystemEntity(
                entity_id=entity_id,
                name=container["name"],
                entity_type="docker_container",
                environment="development",
            )

            db.add(entity)

            synced.append(entity)

        db.commit()

        for entity in synced:
            db.refresh(entity)

        return synced

    def close(self):
        self.client.close()


docker_discovery = DockerDiscovery()
