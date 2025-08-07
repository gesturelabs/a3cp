# apps/ui/main.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="apps/ui/templates")


@router.get("/", response_class=HTMLResponse)
async def landing_view(request: Request):
    return templates.TemplateResponse(
        "landing.html", {"request": request, "current_page": "landing"}
    )


@router.get("/demonstrator", response_class=HTMLResponse)
async def demonstrator_view(request: Request):
    return templates.TemplateResponse(
        "demonstrator.html", {"request": request, "current_page": "demonstrator"}
    )


@router.get("/documentation", response_class=HTMLResponse)
async def docs_view(request: Request):
    return templates.TemplateResponse(
        "docs.html", {"request": request, "current_page": "documentation"}
    )


@router.get("/about", response_class=HTMLResponse)
async def about_view(request: Request):
    return templates.TemplateResponse(
        "about.html", {"request": request, "current_page": "about"}
    )
