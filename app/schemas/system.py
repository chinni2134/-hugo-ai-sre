from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SystemEntityCreate(BaseModel):
    entity_id: str
    name: str
    entity_type: str
    environment: str = "development"


class SystemEntityResponse(SystemEntityCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DependencyCreate(BaseModel):
    source_id: str
    target_id: str
    relationship: str