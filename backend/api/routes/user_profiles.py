from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db_setup import get_db
from api.models.TradeOffers import User, Item
from app.zodb_setup import get_root
from app.getUserID import check_session_cookie

router = APIRouter(tags=["user_profiles"])

@router.get("/user/{user_id}")
async def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a user's profile information and their items
    """
    try:
        user = db.query(User).filter(User.ID == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        items = db.query(Item).filter(Item.userID == user_id).all()

        root = get_root()
        user_items = []
        
        for item in items:
            zodb_id = item.zodb_id
            item_obj = root.get("trade_items", {}).get(zodb_id)
            if item_obj:
                user_items.append({
                    "id": item.ID,
                    "zodb_id": zodb_id,
                    "name": item_obj.name,
                    "description": item_obj.description,
                    "price": item_obj.price,
                    "image": item_obj.image,
                    "category": item_obj.category if hasattr(item_obj, 'category') else None,
                    "is_purchasable": item.is_purchasable,
                    "is_available": item.is_available
                })

        return {
            "user_id": user.ID,
            "username": user.UserName,
            "items": user_items
        }
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Error in get_user_profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")