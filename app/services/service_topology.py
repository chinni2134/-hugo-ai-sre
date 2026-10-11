
from app.database.neo4j import neo4j_connection

from app.services.docker_services import docker_services

class ServiceTopologyService:

    @staticmethod

    def sync_services():

        services = docker_services.discover_services()

        synced = []

        query = """

        MATCH (entity:SystemEntity {

            entity_id: $entity_id

        })

        MERGE (service:Service {

            name: $service_name,

            entity_id: $entity_id

        })

        SET

            service.protocol = $protocol,

            service.container_port = $container_port,

            service.host_port = $host_port

        MERGE (entity)-[:EXPOSES]->(service)

        MERGE (endpoint:Endpoint {

            protocol: $protocol,

            port: $container_port

        })

        MERGE (service)-[:LISTENS_ON]->(endpoint)

        RETURN

            entity.name AS container,

            service.name AS service,

            endpoint.protocol AS protocol,

            endpoint.port AS port

        """

        with neo4j_connection.driver.session() as session:

            for item in services:

                result = session.run(

                    query,

                    entity_id=item["entity_id"],

                    service_name=item["service_name"],

                    protocol=item["protocol"],

                    container_port=item["container_port"],

                    host_port=item["host_port"],

                )

                record = result.single()

                if record:

                    synced.append(dict(record))

        return synced

