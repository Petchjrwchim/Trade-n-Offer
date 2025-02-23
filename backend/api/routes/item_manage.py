from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.db_config import get_db_connection
import mysql.connector

router = APIRouter()

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

    return {"items": result}

@router.post("/add-item")
async def add_item(request: Request, item: dict):
    user_id = get_current_user_id(request)
    item_name = item.get("item_name")
    item_description = item.get("item_description")
    item_image = item.get("item_image")
    item_price = item.get("item_price")
    print(user_id, item_name, item_description, item_image, item_price)
    
    if not item_name:
        raise HTTPException(status_code=400, detail="Item name must be provide")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try: 
        cursor.execute(
          "INSERT INTO trade_items (userID, image, name, description, price) VALUES (%s, %s, %s, %s, %s)",
          (user_id, item_image, item_name, item_description, item_price)
        )
        conn.commit()
    
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Failed to add item to the database")

    cursor.close()
    conn.close()

    return JSONResponse(content={"message": "Item added successfully!"}, status_code=201)