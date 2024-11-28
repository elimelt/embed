import markdown
from ..db.crud import CRUDMarkdown
from ..schemas.markdown import MarkdownContent, MarkdownResponse
from fastapi import HTTPException
from typing import Optional


class MarkdownService:
    @staticmethod
    def create_embed(content: MarkdownContent) -> MarkdownResponse:
        result = CRUDMarkdown.create(content.content)
        return MarkdownResponse(
            uuid=result["uuid"],
            auth_key=result["auth_key"],
            embed_url=f"/embed/{result['uuid']}",
        )

    @staticmethod
    def get_document(embed_id: str, auth_key: Optional[str] = None) -> dict:
        doc = CRUDMarkdown.get(embed_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if auth_key and doc["auth_key"] != auth_key:
            raise HTTPException(status_code=403, detail="Invalid authorization key")

        return doc

    @staticmethod
    def update_document(embed_id: str, content: MarkdownContent, auth_key: str) -> dict:
        doc = CRUDMarkdown.get(embed_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc["auth_key"] != auth_key:
            raise HTTPException(status_code=403, detail="Invalid authorization key")

        if not CRUDMarkdown.update(embed_id, content.content):
            raise HTTPException(status_code=500, detail="Failed to update document")

        return {"status": "success"}

    @staticmethod
    def delete_document(embed_id: str, auth_key: str) -> dict:
        doc = CRUDMarkdown.get(embed_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc["auth_key"] != auth_key:
            raise HTTPException(status_code=403, detail="Invalid authorization key")

        if not CRUDMarkdown.delete(embed_id):
            raise HTTPException(status_code=500, detail="Failed to delete document")

        return {"status": "success"}

    @staticmethod
    def render_markdown(content: str) -> str:
        return markdown.markdown(content, extensions=["fenced_code", "tables"])
