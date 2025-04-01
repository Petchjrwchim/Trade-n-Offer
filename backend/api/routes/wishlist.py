from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db_setup import get_db
from api.models.TradeOffers import Wishlist, User
from api.db_schema.wishlist import WishlistCreate
from app.getUserID import check_session_cookie
from typing import List
from app.zodb_setup import get_root
router = APIRouter(tags=["Wishlist_management"])

@router.post("/add_wishlist/{zodb_id}")
def add_to_wishlist(request: Request, zodb_id: int, db: Session = Depends(get_db)):
    user_id = check_session_cookie(request)
    existing = db.query(Wishlist).filter_by(user_id=user_id, item_id=zodb_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Item already in wishlist")
    
    wishlist_item = Wishlist(user_id=user_id, item_id=zodb_id)
    db.add(wishlist_item)
    db.commit()
    db.refresh(wishlist_item)
    return {"message": "Item added to wishlist"}

@router.delete("/remove_wishlist/{zodb_id}")
def remove_from_wishlist(request: Request, zodb_id: int, db: Session = Depends(get_db)):
    user_id = check_session_cookie(request)
    wishlist_item = db.query(Wishlist).filter_by(user_id=user_id, item_id=zodb_id).first()
    
    if not wishlist_item:
        raise HTTPException(status_code=404, detail="Wishlist item not found")

    db.delete(wishlist_item)
    db.commit()
    return {"message": "Item removed from wishlist"}


# @router.get("/{user_id}", response_model=List[WishlistCreate])
# def get_user_wishlist(user_id: int, db: Session = Depends(get_db)):
#     wishlist_items = db.query(Wishlist).filter_by(user_id=user_id).all()
#     return wishlist_items

@router.get("/status_wishlist/{item_id}")
def check_status(request: Request, item_id: int, db:Session = Depends(get_db)):
    user_id = check_session_cookie(request)
    exists = db.query(Wishlist).filter_by(user_id=user_id, item_id=item_id).first()
    return bool(exists)

@router.get("/user_wishlist")
def get_user_wishlist(request: Request, db:Session = Depends(get_db)):
    try:
        user_id = check_session_cookie(request)
        items = db.query(Wishlist).filter_by(user_id=user_id).all()
        if not items:
            return {"message": "No item in wishlist"}
        
        result_items = []
        root = get_root()
        for item in items:
            zodb_data = root.get("trade_items", {}).get(item.zodb_id)
            user = db.query(User).filter(User.ID == item.userID).first()
            username = user.UserName if user else "Unknow User"
            
            if zodb_data:
                item_data = {
                    "ID": item.ID,
                    "is_purchasable": item.is_purchasable,
                    "userID": item.userID,
                    "username": username,
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
                    "username": username,
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