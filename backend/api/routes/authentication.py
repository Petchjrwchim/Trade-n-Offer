from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.db_config import get_db_connection
import mysql.connector

router = APIRouter(tags=["Authentication"])

@router.post("/login")
async def login(user: dict):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM userpass WHERE UserName = %s AND UserPass = %s", 
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

