from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.db_config import get_db_connection  
from app.zodb_setup import get_root, commit_changes  
from api.routes.item_class import TradeItem 
from app.getUserID import check_session_cookie
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector

router = APIRouter(tags=["Items_management"])

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
    cursor.execute("SELECT ID, zodb_id FROM trade_items WHERE userID = %s", (user_id,))
    trade_items = cursor.fetchall()
    cursor.close()
    conn.close()

    root = get_root()
    user_items = []
    for row in trade_items:
        zodb_id = row["zodb_id"]
        item_obj = root.get("trade_items", {}).get(zodb_id)
        if item_obj:
            user_items.append({
                "id": row["ID"],
                "name": item_obj.name,
                "description": item_obj.description,
                "price": item_obj.price,
                "image": item_obj.image,
                "category": item_obj.category
            })
    return {"items": user_items}

def get_next_zodb_id():
    """Find the next available zodb_id in MySQL."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT MAX(zodb_id) AS max_id FROM trade_items")
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    return (result["max_id"] or 0) + 1  # If no data, start from 1


@router.post("/add-item")
async def add_item(request: Request, item: dict):
    user_id = check_session_cookie(request)
    
    item_name = item.get("item_name")
    item_description = item.get("item_description")
    item_image = item.get("item_image")
    item_price = item.get("item_price")
    is_purchasable = item.get("is_purchasable", False)

    if not item_name:
        raise HTTPException(status_code=400, detail="Item name must be provided")

    root = get_root()

    if "trade_items" not in root:
        root["trade_items"] = {}

    new_item_id = get_next_zodb_id()

    root["trade_items"][new_item_id] = TradeItem(
        name=item_name,
        description=item_description,
        price=item_price,
        image=item_image,
        category="General"
    )
    commit_changes()

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO trade_items (userID, zodb_id, is_purchasable) VALUES (%s, %s, %s)",
            (user_id, new_item_id, is_purchasable)
        )
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to add item: {err}")

    cursor.close()
    conn.close()

    return JSONResponse(content={"message": "Item added successfully!", "zodb_id": new_item_id, "is_purchasable": is_purchasable}, status_code=201)



@router.get("/debug-zodb")
async def debug_zodb():
    """Retrieve all items from ZODB and check if they exist in MySQL."""
    root = get_root()

    if "trade_items" not in root or not root["trade_items"]:
        return {"message": "No trade items found in ZODB."}

    zodb_items = {
        item_id: {
            "name": item.name,
            "description": item.description,
            "price": item.price,
            "image": item.image,
            "category": item.category,
        }
        for item_id, item in root["trade_items"].items()
    }

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM trade_items")
    mysql_items = cursor.fetchall()
    cursor.close()
    conn.close()

    return {
        "zodb_items_count": len(root["trade_items"]),
        "zodb_items": zodb_items,
        "mysql_items_count": len(mysql_items),
        "mysql_items": mysql_items
    }