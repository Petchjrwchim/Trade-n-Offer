from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

#authentication function
from api.routes.authentication import router as auth_router

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
@app.get("/")
async def index(request: Request):
    session_token = request.cookies.get("session_token")
    if not session_token:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("mainPage.html", 
                                      {"request": request, "message": "Welcome to Trade’n Offer"})


@app.get("/login")
async def loginPage(request: Request):
    return templates.TemplateResponse("authentication.html", 
                                      {"request": request, "message": "Welcome to Trade’n Offer"})

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="login")
    response.delete_cookie("session_token")
    return response