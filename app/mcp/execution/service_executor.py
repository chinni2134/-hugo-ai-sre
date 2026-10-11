import docker


class ServiceExecutor:
    """
    Controlled infrastructure execution layer for HUGO.

    All infrastructure-changing operations must pass through
    this layer after authorization and approval.
    """

    def __init__(self):
        self.client = docker.from_env()

    def restart_container(self, service_name: str) -> dict:
        container = self.client.containers.get(service_name)

        previous_status = container.status
        container.restart()
        container.reload()

        return {
            "service": service_name,
            "previous_status": previous_status,
            "current_status": container.status,
            "action": "restart",
            "executed": True,
        }

    def close(self):
        self.client.close()


service_executor = ServiceExecutor()
