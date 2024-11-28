import sqlite3
import markdown
import uuid
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from contextlib import contextmanager

app = FastAPI()

# mount templates
templates = Jinja2Templates(directory="templates")

# database configuration
DATABASE_URL = "markdown.db"

class MarkdownContent(BaseModel):
    content: str

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize the database with required tables"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS markdown_documents (
                uuid TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

@app.on_event("startup")
async def startup_event():
    """Run database initialization when the app starts"""
    init_db()

@app.post("/create")
async def create_embed(content: MarkdownContent):
    embed_id = str(uuid.uuid4())

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO markdown_documents (uuid, content) VALUES (?, ?)",
            (embed_id, content.content)
        )
        conn.commit()

    return {
        "uuid": embed_id,
        "embed_url": f"/embed/{embed_id}"
    }

@app.get("/embed/{embed_id}", response_class=HTMLResponse)
async def get_embed(embed_id: str, request: Request):
    with get_db() as conn:
        cursor = conn.cursor()

        # get the markdown content
        cursor.execute(
            "SELECT content FROM markdown_documents WHERE uuid = ?",
            (embed_id,)
        )
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Embed not found")

        # update last accessed timestamp
        cursor.execute(
            "UPDATE markdown_documents SET last_accessed = CURRENT_TIMESTAMP WHERE uuid = ?",
            (embed_id,)
        )
        conn.commit()

        # convert markdown to HTML
        html_content = markdown.markdown(result[0], extensions=['fenced_code', 'tables'])

        return templates.TemplateResponse(
            "embed.html",
            {"request": request, "content": html_content}
        )

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.delete("/cleanup")
async def cleanup_old_documents():
    """Remove documents that haven't been accessed in 30 days"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM markdown_documents
            WHERE last_accessed < datetime('now', '-30 days')
        """)
        deleted_count = cursor.rowcount
        conn.commit()

    return {"deleted_count": deleted_count}

@app.get("/view/{embed_id}", response_class=HTMLResponse)
async def view_embed(embed_id: str, request: Request):
    """Direct viewing route with full page layout"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT content FROM markdown_documents WHERE uuid = ?",
            (embed_id,)
        )
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Document not found")

        # update last accessed timestamp
        cursor.execute(
            "UPDATE markdown_documents SET last_accessed = CURRENT_TIMESTAMP WHERE uuid = ?",
            (embed_id,)
        )
        conn.commit()

        html_content = markdown.markdown(result[0], extensions=['fenced_code', 'tables'])

        return templates.TemplateResponse(
            "view.html",
            {"request": request, "content": html_content}
        )