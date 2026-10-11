from datetime import datetime

from pydantic import BaseModel, Field


class KnowledgeDocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    source: str = Field(..., min_length=1, max_length=500)
    document_type: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., min_length=1)
    environment: str = Field(
        default="development",
        max_length=100,
    )


class KnowledgeDocumentResponse(BaseModel):
    id: int
    document_id: str
    title: str
    source: str
    document_type: str
    content: str
    environment: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
