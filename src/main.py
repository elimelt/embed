from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .api.routes import embeds, views
from .db.database import init_db
from .config import settings

app = FastAPI(title="Markdown Embed Service")

app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")

app.include_router(embeds.router)
app.include_router(views.router)


@app.on_event("startup")
async def startup_event():
    init_db()
