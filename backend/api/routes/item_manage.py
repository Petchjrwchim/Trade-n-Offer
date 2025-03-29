from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from app.db_setup import get_db  # This should provide a SQLAlchemy session
from api.models.TradeOffers import Item, User  # SQLAlchemy model for trade_items
from app.zodb_setup import get_root, commit_changes
from app.getUserID import check_session_cookie
from fastapi.responses import JSONResponse
from api.models.item_class import TradeItem

from ZODB import DB

router = APIRouter(tags=["Items_management"])

@router.get("/my-items")
async def get_items_for_user(request: Request, db: Session = Depends(get_db)):
    user_id = check_session_cookie(request)

    # Query the database using SQLAlchemy
    trade_items = db.query(Item).filter(Item.userID == user_id).all()

    root = get_root()
    user_items = []
    for row in trade_items:
        zodb_id = row.zodb_id
        item_obj = root.get("trade_items", {}).get(zodb_id)
        if item_obj:
            user_items.append({
                "id": row.ID,
                "name": item_obj.name,
                "description": item_obj.description,
                "price": item_obj.price,
                "image": item_obj.image,
                "category": item_obj.category
            })
    return {"items": user_items}

@router.post("/add-item")
async def add_item(request: Request, item: dict, db: Session = Depends(get_db)):
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

    # new_item_id = len(root["trade_items"]) + 1
    trade_items = root["trade_items"]
    new_item_id = max(trade_items.keys(), default=0) + 1
    root["trade_items"][new_item_id] = TradeItem(
        name=item_name,
        description=item_description,
        price=item_price,
        image=item_image,
        category="General"
    )
    commit_changes()

    new_trade_item = Item(
        userID=user_id,
        zodb_id=new_item_id,
        is_purchasable=is_purchasable
    )
    db.add(new_trade_item)
    db.commit()

    return JSONResponse(content={"message": "Item added successfully!", "zodb_id": new_item_id, "is_purchasable": is_purchasable}, status_code=201)

@router.get("/get-all-posts")
async def get_all_posts(request: Request, db: Session = Depends(get_db)):
    try:
        user_id = check_session_cookie(request)
        items = db.query(Item).filter(Item.userID != user_id).all()

        if not items:
            return {"message": "No items available."}
        
        result_items = []
        root = get_root()
        for item in items:
            zodb_data = root.get("trade_items", {}).get(item.zodb_id)
            if zodb_data:
                item_data = {
                    "ID": item.ID,
                    "is_purchasable": item.is_purchasable,
                    "userID": item.userID,
                    "zodb_id": item.zodb_id,
                    "name": zodb_data.name,
                    "description": zodb_data.description,
                    "price": zodb_data.price,
                    "image": zodb_data.image,
                    "category": zodb_data.category
                }
                result_items.append(item_data)
            else:
                result_items.append({
                    "ID": item.ID,
                    "is_purchasable": item.is_purchasable,
                    "userID": item.userID,
                    "zodb_id": item.zodb_id,
                    "name": None,
                    "description": None,
                    "price": None,
                    "image": None,
                    "category": None
                })
        
        return result_items
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")