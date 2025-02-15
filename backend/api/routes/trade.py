from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")

@router.get("/trade")
async def trade(request: Request):
    return templates.TemplateResponse("trade.html", {"request": request})
