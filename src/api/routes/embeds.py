from fastapi import APIRouter, Depends, Header, HTTPException
from typing import Optional
from ...schemas.markdown import MarkdownContent, MarkdownResponse
from ...services.markdown import MarkdownService

router = APIRouter(prefix="/api/embeds", tags=["embeds"])


@router.post("", response_model=MarkdownResponse)
async def create_embed(content: MarkdownContent):
    return MarkdownService.create_embed(content)


@router.get("/{embed_id}")
async def get_document(embed_id: str, authorization: Optional[str] = Header(None)):
    return MarkdownService.get_document(embed_id, authorization)


@router.put("/{embed_id}")
async def update_embed(
    embed_id: str, content: MarkdownContent, authorization: str = Header(...)
):
    return MarkdownService.update_document(embed_id, content, authorization)


@router.delete("/{embed_id}")
async def delete_embed(embed_id: str, authorization: str = Header(...)):
    return MarkdownService.delete_document(embed_id, authorization)
