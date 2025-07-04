from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/admin",
    responses={404: {"description": "Not found"}},
)

templates = Jinja2Templates(directory="templates")


# Add HTML routes alongside your existing API routes
@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    print("Session at /admin:")
    print(request.session)
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
        },
    )
