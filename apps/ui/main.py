# apps/ui/main.py
from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

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


app = FastAPI(
    title="GestureLabs Website",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.include_router(router)
