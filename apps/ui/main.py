# apps/ui/main.py
from pathlib import Path

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from apps.session_manager.routes.router import router as session_manager_router

templates = Jinja2Templates(directory="apps/ui/templates")
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home_view(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "current_page": "home"},
    )


@router.get("/about", response_class=HTMLResponse)
async def about_view(request: Request):
    return templates.TemplateResponse(
        "about.html",
        {"request": request, "current_page": "about"},
    )


@router.get("/technology", response_class=HTMLResponse)
async def technology_view(request: Request):
    return templates.TemplateResponse(
        "technology.html",
        {"request": request, "current_page": "technology"},
    )


@router.get("/docs", response_class=HTMLResponse)
async def docs_view(request: Request):
    return templates.TemplateResponse(
        "docs.html", {"request": request, "current_page": "docs"}
    )


@router.get("/get-involved", response_class=HTMLResponse)
async def get_involved_view(request: Request):
    return templates.TemplateResponse(
        "get_involved.html",
        {"request": request, "current_page": "get-involved"},
    )


@router.get("/contact", response_class=HTMLResponse)
async def contact_view(request: Request):
    return templates.TemplateResponse(
        "contact.html",
        {"request": request, "current_page": "contact"},
    )


@router.get("/demo/session", response_class=HTMLResponse)
async def demo_session_view(request: Request):
    return templates.TemplateResponse(
        "demo_session.html",
        {"request": request, "current_page": None},
    )


app = FastAPI(
    title="GestureLabs Website",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

STATIC_DIR = Path(__file__).parent / "static"

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)


app.include_router(router)
app.include_router(session_manager_router)
