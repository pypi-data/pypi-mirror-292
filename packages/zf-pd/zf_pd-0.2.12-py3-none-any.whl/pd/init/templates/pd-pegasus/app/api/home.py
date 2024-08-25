from urllib.parse import unquote

from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from loguru import logger
from starlette.requests import Request
from starlette.responses import HTMLResponse

from app.lib.seo import metadata

router = APIRouter(
    prefix="",
    tags=["home"],
)

templates = Jinja2Templates(directory="ui")


@router.get("/{full_path:path}", response_class=HTMLResponse)
async def catch_all(request: Request, full_path: str):
    path = "/" + unquote(full_path)
    seo = metadata.get(path, metadata.get("/"))  # Default to home page metadata
    logger.debug(f"SEO metadata for {path}: {seo}")
    return templates.TemplateResponse("index.html", {
        "request": request,
        "data": {},
        "seo": seo,
    })
