from datetime import datetime
from pydantic import BaseModel


class MarkdownDocument(BaseModel):
    uuid: str
    content: str
    auth_key: str
    created_at: datetime
    last_accessed: datetime
