from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from typing import List
#authentication function
from api.routes.authentication import router as auth_router
from api.routes.item_manage import router as item_router
from api.routes.chat_server import router as chat_router
from api.routes.item import router as itemlis_router

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static and template mounting
app.mount("/static", StaticFiles(directory="../Frontend/static"), name="static")
templates = Jinja2Templates(directory="../Frontend/templates")

app.include_router(auth_router)
app.include_router(item_router)
app.include_router(chat_router)
app.include_router(itemlis_router)


@app.get("/")
async def index(request: Request):
    session_token = request.cookies.get("session_token")
    if not session_token:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("main_page.html", 
                                      {"request": request})

@app.get("/login")
async def loginPage(request: Request):
    return templates.TemplateResponse("authentication.html", 
                                      {"request": request, "message": "Welcome to Trade’n Offer"})

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="login")
    response.delete_cookie("session_token")
    return response

@app.get("/chat")
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/MyItem")
async def myItem_page(request: Request):
    return templates.TemplateResponse("myItem_page.html", {"request": request})

def check_session_cookie(request: Request):
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code=401, detail="Unauthorized - No session token")
    return session_token

@app.get("/check-session")
async def check_session(request: Request):
    session_token = check_session_cookie(request)
    print(f"Session Token from request: {session_token}")  # Print session token
    print("i'm heasdre")
    return {"message": "Session token exists", "session_token": session_token}

@app.get("/trade_offer")
async def trade_offer_page(request: Request):
    return templates.TemplateResponse("trade_offer.html", {
        "request": request,
        "image_url": "/static/image_test/camera.jpg"  # Pass the image URL here
    })