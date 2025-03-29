from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from app.db_setup import get_db  # This should provide a SQLAlchemy session
from api.models.TradeOffers import Item  # SQLAlchemy model for trade_items
from app.zodb_setup import get_root, commit_changes
from app.getUserID import check_session_cookie
from fastapi.responses import JSONResponse
from api.models.item_class import TradeItem

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

    new_item_id = len(root["trade_items"]) + 1
    root["trade_items"][new_item_id] = TradeItem(
        name=item_name,
        description=item_description,
        price=item_price,
        image=item_image,
        category="General"
    )
    commit_changes()

    # Add to the SQLAlchemy database
    new_trade_item = Item(
        userID=user_id,
        zodb_id=new_item_id,
        is_purchasable=is_purchasable
    )
    db.add(new_trade_item)
    db.commit()

    return JSONResponse(content={"message": "Item added successfully!", "zodb_id": new_item_id, "is_purchasable": is_purchasable}, status_code=201)

@router.get("/get-post/{item_id}")
async def get_post(item_id: int, db: Session = Depends(get_db)):
    trade_item = db.query(Item).filter(Item.ID == item_id).first()
    if not trade_item:
        raise HTTPException(status_code=404, detail="Item not found in SQL database")
    
    root = get_root()
    item_obj = root["trade_items"].get(trade_item.zodb_id)
    if not item_obj:
        raise HTTPException(status_code=404, detail="Item not found in ZODB")
    
    post_data = {
        "id": trade_item.ID,
        "name": item_obj.name,
        "description": item_obj.description,
        "price": item_obj.print,
        "image": item_obj.image,
        "category": item_obj.category,
        "is_purchasable": trade_item.is_purchasable,
        "ownerID": trade_item.userID,
    }

    post_data["likes"] = 100  # Example static likes count, you can retrieve this from a 'likes' table if needed
    post_data["comments"] = [
        {"username": "user1", "comment": "Great item!"},
        {"username": "user2", "comment": "I would love to trade for this!"}
    ]
    post_data["comments_count"] = len(post_data["comments"])

    return post_data