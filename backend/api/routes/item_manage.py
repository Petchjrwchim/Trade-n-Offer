from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from app.db_setup import get_db
from api.models.TradeOffers import Item, Wishlist
from app.zodb_setup import get_root, commit_changes, close_connection
from app.getUserID import check_session_cookie
from fastapi.responses import JSONResponse
from api.models.item_class import TradeItem

router = APIRouter(tags=["Items_management"])

@router.get("/my-items")
async def get_items_for_user(request: Request, db: Session = Depends(get_db)):
    user_id = check_session_cookie(request)
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
    return user_items

@router.post("/add-item")
async def add_item(request: Request, item: dict, db: Session = Depends(get_db)):
    user_id = check_session_cookie(request)
    
    item_name = item.get("item_name")
    item_description = item.get("item_description")
    item_image = item.get("item_image")
    item_price = item.get("item_price")
    is_purchasable = item.get("is_purchasable", False)
    is_tradeable = item.get("is_tradeable", False)
    is_available = item.get("is_available", True)

    if not item_name:
        raise HTTPException(status_code=400, detail="Item name must be provided")

    root = get_root()

    if "trade_items" not in root:
        root["trade_items"] = {}

    new_item_id = max(int(k) for k in root["trade_items"].keys()) + 1

    try:
        trade_items = root["trade_items"].copy()
        trade_items[new_item_id] = TradeItem(
            name=item_name,
            description=item_description,
            price=item_price,
            image=item_image,
            category="General",
        )

        root["trade_items"] = trade_items  

        new_trade_item = Item(
            userID=user_id,
            zodb_id=new_item_id,
            is_purchasable=is_purchasable,
            is_tradeable=is_tradeable,
            is_available=is_available
        )

        commit_changes()  # Commit ZODB changes
        db.add(new_trade_item)
        db.commit()  # Commit SQLAlchemy changes

        return JSONResponse(content={"message": "Item added successfully!", "zodb_id": new_item_id, "is_purchasable": is_purchasable}, status_code=201)

    except Exception as e:
        db.rollback()  # Rollback SQLAlchemy changes
        close_connection()  # Close the ZODB connection
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    

@router.put("/edit-item/{item_id}")
async def edit_item(request: Request, item_id: int, updated_item: dict, db: Session = Depends(get_db)):
    user_id = check_session_cookie(request)

    # Fetch item from SQL
    trade_item = db.query(Item).filter(Item.ID == item_id, Item.userID == user_id).first()
    if not trade_item:
        raise HTTPException(status_code=404, detail="Item not found or unauthorized")

    root = get_root()
    zodb_id = trade_item.zodb_id
    trade_items = root.get("trade_items", {})

    if zodb_id not in trade_items:
        raise HTTPException(status_code=404, detail="Item not found in ZODB")

    zodb_item = trade_items[zodb_id]
    zodb_item.name = updated_item.get("item_name", zodb_item.name)
    zodb_item.description = updated_item.get("item_description", zodb_item.description)
    zodb_item.price = updated_item.get("item_price", zodb_item.price)
    zodb_item.image = updated_item.get("item_image", zodb_item.image)
    zodb_item.category = updated_item.get("category", zodb_item.category)

    trade_item.is_purchasable = updated_item.get("is_purchasable", trade_item.is_purchasable)
    trade_item.is_tradeable = updated_item.get("is_tradeable", trade_item.is_tradeable)
    trade_item.is_available = updated_item.get("is_available", trade_item.is_available)

    try:
        commit_changes()  # Commit ZODB changes
        db.commit()  # Commit SQLAlchemy changes
        return JSONResponse(content={"message": "Item updated successfully!"}, status_code=200)
    except Exception as e:
        db.rollback()  # Rollback SQL if an error occurs
        close_connection()
        raise HTTPException(status_code=500, detail=f"Error updating item: {str(e)}")


@router.delete("/remove-item/{item_id}")
async def remove_item(request: Request, item_id: int, db: Session = Depends(get_db)):
    user_id = check_session_cookie(request)
    trade_item = db.query(Item).filter(Item.ID == item_id, Item.userID == user_id).first()
    item_in_wishlist = db.query(Wishlist).filter(Wishlist.item_id == trade_item.zodb_id).all()
    if not trade_item:
        raise HTTPException(status_code=404, detail="Item not found or unauthorized")

    root = get_root()
    zodb_id = trade_item.zodb_id
    trade_items = root.get("trade_items", {})

    if zodb_id in trade_items:
        del trade_items[zodb_id] 

    try:
        commit_changes() 
        db.delete(trade_item) 

        for wishlist_item in item_in_wishlist:
            db.delete(wishlist_item)

        db.commit()
        return JSONResponse(content={"message": "Item removed successfully!"}, status_code=200)
    except Exception as e:
        db.rollback()
        close_connection()
        raise HTTPException(status_code=500, detail=f"Error deleting item: {str(e)}")
