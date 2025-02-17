from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from api.routes.authentication import router as auth_router
from api.routes.item import router as item_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="../Frontend/static"), name="static")
templates = Jinja2Templates(directory="../Frontend/templates")

app.include_router(auth_router)
app.include_router(item_router)

@app.get("/")
async def index(request: Request):
    session_token = request.cookies.get("session_token")
    if not session_token:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("main_page.html", {"request": request})

@app.get("/login")
async def loginPage(request: Request):
    return templates.TemplateResponse("authentication.html", {"request": request, "message": "Welcome to Trade’n Offer"})

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="login")
    response.delete_cookie("session_token")
    return response

# Route ใหม่สำหรับ Trade’n Offer
@app.get("/trade_offer")
async def trade_offer_page(request: Request):
    return templates.TemplateResponse("trade_offer.html", {"request": request})
