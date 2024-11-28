from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MarkdownContent(BaseModel):
    content: str


class MarkdownResponse(BaseModel):
    uuid: str
    auth_key: str
    embed_url: str


class MarkdownDocument(BaseModel):
    uuid: str
    content: str
    auth_key: str
    created_at: datetime
    last_accessed: datetime

    class Config:
        from_attributes = True
