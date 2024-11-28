from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from ...services.markdown import MarkdownService
from ...config import settings
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["views"])
templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))


@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/embed/{embed_id}", response_class=HTMLResponse)
async def get_embed(embed_id: str, request: Request):
    doc = MarkdownService.get_document(embed_id)
    html_content = MarkdownService.render_markdown(doc["content"])
    return templates.TemplateResponse(
        "embed.html", {"request": request, "content": html_content}
    )


@router.get("/view/{embed_id}", response_class=HTMLResponse)
async def view_embed(embed_id: str, request: Request):
    doc = MarkdownService.get_document(embed_id)
    html_content = MarkdownService.render_markdown(doc["content"])
    return templates.TemplateResponse(
        "view.html", {"request": request, "content": html_content}
    )
