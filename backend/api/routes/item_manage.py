from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector

router = APIRouter()

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="tno"
    )

def get_current_user_id(request: Request):
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code=401, detail="User not authenticated")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM userpass WHERE ID = %s", (session_token,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        return result['ID']
    else:
        raise HTTPException(status_code=401, detail="Invalid session token")


@router.get("/my-items")
async def get_items_for_user(request: Request):
    user_id = get_current_user_id(request)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM trade_items WHERE userID = %s", (user_id,))
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    if result:
        return {"items": result}
    else:
        raise HTTPException(status_code=404, detail="No items found for this user")