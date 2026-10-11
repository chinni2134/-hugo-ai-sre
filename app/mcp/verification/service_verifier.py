import docker


class ServiceVerifier:
    """
    Verifies the state of infrastructure after HUGO executes
    a controlled operation.
    """

    def __init__(self):
        self.client = docker.from_env()

    def verify_container(self, service_name: str) -> dict:
        container = self.client.containers.get(service_name)
        container.reload()

        status = container.status

        return {
            "service": service_name,
            "status": status,
            "healthy": status == "running",
            "verified": True,
        }

    def close(self):
        self.client.close()


service_verifier = ServiceVerifier()
