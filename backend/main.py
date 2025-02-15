from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

# Import the authentication router
from api.routes import authentication

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

# Include the authentication router
app.include_router(authentication.router, prefix="/auth", tags=["Authentication"])

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "message": "Welcome to Trade’n Offer"})
