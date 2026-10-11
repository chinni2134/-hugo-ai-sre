
from pydantic import BaseModel

class ServiceEndpoint(BaseModel):

    entity_id: str

    container_name: str

    service_name: str

    protocol: str

    container_port: int

    host_port: int | None = None

