import docker


class DockerServiceDiscovery:

    def __init__(self):
        self.client = docker.from_env()

    def discover_services(self):

        containers = self.client.containers.list(all=True)

        services = []

        for container in containers:

            entity_id = f"docker:{container.id}"

            ports = container.attrs.get(
                "NetworkSettings", {}
            ).get("Ports", {})

            for container_port, bindings in ports.items():

                if "/" in container_port:
                    port_number, protocol = container_port.split("/", 1)
                else:
                    port_number = container_port
                    protocol = "tcp"

                host_port = None

                if bindings:
                    host_port = int(
                        bindings[0]["HostPort"]
                    )

                services.append(
                    {
                        "entity_id": entity_id,
                        "container_name": container.name,
                        "service_name": self.identify_service(
                            container.name,
                            container.image.tags,
                            int(port_number),
                        ),
                        "protocol": protocol,
                        "container_port": int(port_number),
                        "host_port": host_port,
                    }
                )

        return services

    @staticmethod
    def identify_service(
        container_name,
        image_tags,
        port,
    ):

        name = container_name.lower()

        if "postgres" in name:
            return "PostgreSQL"

        if "neo4j" in name:
            if port == 7687:
                return "Neo4j Bolt"
            if port == 7474:
                return "Neo4j HTTP"

            return "Neo4j"

        if "redis" in name:
            return "Redis"

        if "prometheus" in name:
            return "Prometheus"

        if "elastic" in name:
            return "Elasticsearch"

        return "Unknown Service"

    def close(self):
        self.client.close()


docker_services = DockerServiceDiscovery()
