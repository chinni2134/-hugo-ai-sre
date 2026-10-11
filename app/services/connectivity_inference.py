import docker

from app.database.neo4j import neo4j_connection


class ConnectivityInferenceService:

    def __init__(self):
        self.client = docker.from_env()

    def test_and_store(self):

        containers = self.client.containers.list()
        results = []

        for source in containers:

            source_networks = source.attrs.get(
                "NetworkSettings", {}
            ).get("Networks", {})

            for network_name in source_networks:

                network = self.client.networks.get(network_name)

                members = network.attrs.get("Containers", {})

                for target_id, target_data in members.items():

                    if target_id == source.id:
                        continue

                    target_ip = target_data.get(
                        "IPv4Address", ""
                    ).split("/")[0]

                    if not target_ip:
                        continue

                    target = self.client.containers.get(target_id)

                    ports = target.attrs.get(
                        "NetworkSettings", {}
                    ).get("Ports", {})

                    for port_definition in ports:

                        if not port_definition:
                            continue

                        port = int(
                            port_definition.split("/")[0]
                        )

                        reachable = self._test_from_network(
                            network_name,
                            target_ip,
                            port,
                        )

                        if not reachable:
                            continue

                        query = """
                        MATCH (source:SystemEntity {
                            entity_id: $source_id
                        })

                        MATCH (target:SystemEntity {
                            entity_id: $target_id
                        })

                        MERGE (source)-[r:OBSERVED_CONNECTIVITY]->(target)

                        SET
                            r.network = $network,
                            r.port = $port,
                            r.evidence = "tcp_connectivity",
                            r.confidence = 0.85

                        RETURN
                            source.name AS source,
                            target.name AS target,
                            r.port AS port,
                            r.confidence AS confidence
                        """

                        with neo4j_connection.driver.session() as session:

                            record = session.run(
                                query,
                                source_id=f"docker:{source.id}",
                                target_id=f"docker:{target.id}",
                                network=network_name,
                                port=port,
                            ).single()

                            if record:
                                results.append(dict(record))

        return results

    def _test_from_network(
        self,
        network_name,
        host,
        port,
    ):

        try:

            result = self.client.containers.run(
                "busybox:latest",
                [
                    "sh",
                    "-c",
                    f"nc -z -w 1 {host} {port}",
                ],
                network=network_name,
                remove=True,
            )

            return True

        except docker.errors.ContainerError:
            return False

        except Exception:
            return False

    def close(self):
        self.client.close()


connectivity_inference = ConnectivityInferenceService()
