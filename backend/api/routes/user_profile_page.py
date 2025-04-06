import os
from pathlib import Path
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db_setup import get_db

# คำนวณเส้นทางที่ถูกต้องจากโครงสร้างโปรเจ็ค
base_dir = Path(__file__).resolve().parent.parent.parent.parent
templates_dir = os.path.join(base_dir, "Frontend", "templates")
templates = Jinja2Templates(directory=templates_dir)

# หรือระบุเส้นทางแบบแน่นอน
# templates = Jinja2Templates(directory="./Frontend/templates")

router = APIRouter()

# Calculate the correct path to templates directory
base_dir = Path(__file__).resolve().parent.parent.parent.parent
templates_dir = os.path.join(base_dir, "Frontend", "templates")
templates = Jinja2Templates(directory=templates_dir)

router = APIRouter()

@router.get("/user-profile/{user_id}", response_class=HTMLResponse)
async def user_profile(request: Request, user_id: int, db: Session = Depends(get_db)):
    try:
        print(f"Rendering user profile page for user ID: {user_id}")
        print(f"Using templates from: {templates_dir}")
        return templates.TemplateResponse(
            "user_profile.html",
            {"request": request, "user_id": user_id}
        )
    except Exception as e:
        print(f"Error rendering user profile: {str(e)}")
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; color: white; background-color: #333; }}
                .error-container {{ max-width: 600px; margin: 50px auto; padding: 20px; border-radius: 10px; 
                                   background-color: #444; box-shadow: 0 0 10px rgba(0,0,0,0.3); }}
                h1 {{ color: #f44336; }}
                a {{ color: #2196F3; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <h1>Error Displaying Profile</h1>
                <p>Sorry, we couldn't display this user profile. Please try again later.</p>
                <p>Error details: {str(e)}</p>
                <p><a href="/">Return to Home</a></p>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=500)