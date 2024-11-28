import markdown
from ..db.crud import CRUDDocument
from ..schemas.document import DocumentContent, DocumentResponse
from fastapi import HTTPException
from typing import Optional


class DocumentService:
    @staticmethod
    def create_embed(content: DocumentContent) -> DocumentResponse:
        result = CRUDDocument.create(content.content)
        return DocumentResponse(
            uuid=result["uuid"],
            auth_key=result["auth_key"],
            embed_url=f"/embed/{result['uuid']}",
        )

    @staticmethod
    def get_document(embed_id: str, auth_key: Optional[str] = None) -> dict:
        doc = CRUDDocument.get(embed_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if auth_key and doc["auth_key"] != auth_key:
            raise HTTPException(status_code=403, detail="Invalid authorization key")

        return doc

    @staticmethod
    def update_document(embed_id: str, content: DocumentContent, auth_key: str) -> dict:
        doc = CRUDDocument.get(embed_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc["auth_key"] != auth_key:
            raise HTTPException(status_code=403, detail="Invalid authorization key")

        if not CRUDDocument.update(embed_id, content.content):
            raise HTTPException(status_code=500, detail="Failed to update document")

        return {"status": "success"}

    @staticmethod
    def delete_document(embed_id: str, auth_key: str) -> dict:
        doc = CRUDDocument.get(embed_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc["auth_key"] != auth_key:
            raise HTTPException(status_code=403, detail="Invalid authorization key")

        if not CRUDDocument.delete(embed_id):
            raise HTTPException(status_code=500, detail="Failed to delete document")

        return {"status": "success"}

    @staticmethod
    def render_markdown(content: str) -> str:
        return markdown.markdown(content, extensions=["fenced_code", "tables"])
