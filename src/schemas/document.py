from pydantic import BaseModel
from datetime import datetime


class DocumentContent(BaseModel):
    content: str


class DocumentResponse(BaseModel):
    uuid: str
    auth_key: str
    embed_url: str


class Document(BaseModel):
    uuid: str
    content: str
    auth_key: str
    created_at: datetime
    last_accessed: datetime

    class Config:
        from_attributes = True
