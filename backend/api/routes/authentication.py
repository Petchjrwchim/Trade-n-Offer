from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.db_config import get_db_connection
from app.db_setup import get_db
from sqlalchemy.orm import Session
from api.models.TradeOffers import User
from app.getUserID import check_session_cookie

router = APIRouter(tags=["Authentication"])

@router.post("/login")
async def login(user: dict):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM users WHERE UserName = %s AND UserPass = %s", 
                   (user["username"], user["password"]))
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    print("call")
    if result:
        user_id = result['ID']
        response = JSONResponse(content={"message": f"Welcome, {user['username']}!"})
        response.set_cookie(key="session_token", value=int(user_id), httponly=True)
        return response
    else:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
@router.get("/getUserProfile")
async def get_user_profile(request: Request, db: Session = Depends(get_db)):
    user_id = check_session_cookie(request)
    user_profile = db.query(User).filter(User.ID == user_id).first()

    return user_profile

