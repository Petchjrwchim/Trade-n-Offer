from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db_setup import get_db
from api.models.TradeOffers import Wishlist
from api.db_schema.wishlist import WishlistCreate
from typing import List
router = APIRouter(prefix="/wishlist", tags=["Wishlist_management"])

@router.post("/")
def add_to_wishlist(wishlist_data: WishlistCreate, db: Session = Depends(get_db)):
    existing = db.query(Wishlist).filter_by(user_id=wishlist_data.user_id, item_id=wishlist_data.item_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Item already in wishlist")
    
    wishlist_item = Wishlist(user_id=wishlist_data.user_id, item_id=wishlist_data.item_id)
    db.add(wishlist_item)
    db.commit()
    db.refresh(wishlist_item)
    return {"message": "Item added to wishlist"}

@router.delete("/{wishlist_id}")
def remove_from_wishlist(wishlist_id: int, db: Session = Depends(get_db)):
    wishlist_item = db.query(Wishlist).filter_by(ID=wishlist_id).first()
    if not wishlist_item:
        raise HTTPException(status_code=404, detail="Wishlist item not found")

    db.delete(wishlist_item)
    db.commit()
    return {"message": "Item removed from wishlist"}

@router.get("/{user_id}", response_model=List[WishlistCreate])
def get_user_wishlist(user_id: int, db: Session = Depends(get_db)):
    wishlist_items = db.query(Wishlist).filter_by(user_id=user_id).all()
    return wishlist_items