from fastapi import APIRouter, Depends, Header, HTTPException
from typing import Optional
from ...schemas.document import DocumentContent, DocumentResponse
from ...services.document import DocumentService

router = APIRouter(prefix="/api/embeds", tags=["embeds"])


@router.post("", response_model=DocumentResponse)
async def create_embed(content: DocumentContent):
    return DocumentService.create_embed(content)


@router.get("/{embed_id}")
async def get_document(embed_id: str, authorization: Optional[str] = Header(None)):
    return DocumentService.get_document(embed_id, authorization)


@router.put("/{embed_id}")
async def update_embed(
    embed_id: str, content: DocumentContent, authorization: str = Header(...)
):
    return DocumentService.update_document(embed_id, content, authorization)


@router.delete("/{embed_id}")
async def delete_embed(embed_id: str, authorization: str = Header(...)):
    return DocumentService.delete_document(embed_id, authorization)
