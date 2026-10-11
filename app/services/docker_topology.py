import docker

from app.database.neo4j import neo4j_connection


class DockerTopologyService:

    def __init__(self):
        self.client = docker.from_env()

    def discover_networks(self):

        containers = self.client.containers.list(all=True)

        networks = {}

        for container in containers:

            container_name = container.name

            for network_name, network_data in container.attrs.get(
                "NetworkSettings", {}
            ).get("Networks", {}).items():

                if network_name not in networks:
                    networks[network_name] = []

                networks[network_name].append(
                    {
                        "container": container_name,
                        "container_id": container.id,
                        "ip": network_data.get("IPAddress"),
                    }
                )

        return networks

    def sync_network_dependencies(self):

        networks = self.discover_networks()

        relationships = []

        for network_name, containers in networks.items():

            for source in containers:

                for target in containers:

                    if source["container_id"] == target["container_id"]:
                        continue

                    source_id = f"docker:{source['container_id']}"
                    target_id = f"docker:{target['container_id']}"

                    query = """
                    MATCH (source:SystemEntity {
                        entity_id: $source_id
                    })

                    MATCH (target:SystemEntity {
                        entity_id: $target_id
                    })

                    MERGE (source)-[r:NETWORK_CONNECTED {
                        network: $network
                    }]->(target)

                    RETURN
                        source.name AS source,
                        target.name AS target,
                        r.network AS network
                    """

                    with neo4j_connection.driver.session() as session:

                        result = session.run(
                            query,
                            source_id=source_id,
                            target_id=target_id,
                            network=network_name,
                        )

                        record = result.single()

                        if record:
                            relationships.append(dict(record))

        return relationships

    def close(self):
        self.client.close()


docker_topology = DockerTopologyService()
