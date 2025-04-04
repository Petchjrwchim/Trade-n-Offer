from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db_setup import get_db
from api.models.TradeOffers import TradeOffer, Match, Item, User
from app.getUserID import check_session_cookie
from app.zodb_setup import get_root, commit_changes, close_connection

router = APIRouter(tags=["Offers_management"])


@router.get("/get-all-posts")
async def get_all_posts(request: Request, db: Session = Depends(get_db)):
    try:
        user_id = check_session_cookie(request)
        items = db.query(Item).filter(Item.userID != user_id).all()
        print(items)
        if not items:
            return {"message": "No items available."}
        
        result_items = []
        root = get_root()
        for item in items:
            print(item.zodb_id)
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
    
@router.post("/create-offers")
def create_offer(sender_id: int, receiver_id: int, sender_item_id: int, receiver_item_id: int, db: Session = Depends(get_db)):
    # db_offer = TradeOffer(
    #     sender_id=sender_id,
    #     receiver_id=receiver_id,
    #     sender_item_id=sender_item_id,
    #     receiver_item_id=receiver_item_id,
    #     status = "pending"
    # )
    # db.add(db_offer)
    # db.commit()
    # db.refresh(db_offer)

    # return db_offer

    receiver_item = db.query(Item).filter(Item.ID == receiver_item_id).first()
    
    if not receiver_item:
        raise HTTPException(status_code=404, detail="Receiver's item not found")
    
    if receiver_item.is_purchasable:
        raise HTTPException(status_code=400, detail="This item is purchasable, not available for trade.")

    db_offer = TradeOffer(
        sender_id=sender_id,
        receiver_id=receiver_id,
        sender_item_id=sender_item_id,
        receiver_item_id=receiver_item_id,
        status="pending"
    )
    db.add(db_offer)
    db.commit()
    db.refresh(db_offer)

    return db_offer

@router.get("/get-trade-offers")
async def get_trade_offers(request: Request, db: Session = Depends(get_db)):
    try:
        user_id = check_session_cookie(request)

        offers = db.query(TradeOffer).filter(
            TradeOffer.receiver_id == user_id,
            TradeOffer.status == "pending"
        ).all()
        
        if not offers:
            return []

        root = get_root()
        trade_items = root.get("trade_items", {})
        
        detailed_offers = []
        for offer in offers:
            sender = db.query(User).filter(User.ID == offer.sender_id).first()
            
            sender_item = db.query(Item).filter(Item.ID == offer.sender_item_id).first()
            sender_zodb_item = trade_items.get(sender_item.zodb_id) if sender_item else None
            
            receiver_item = db.query(Item).filter(Item.ID == offer.receiver_item_id).first()
            receiver_zodb_item = trade_items.get(receiver_item.zodb_id) if receiver_item else None
            
            offer_data = {
                "ID": offer.ID,
                "status": offer.status,
                "created_at": offer.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                
                "sender_id": offer.sender_id,
                "sender_username": sender.UserName if sender else "Unknown User",
                
                "sender_item_id": offer.sender_item_id,
                "sender_item_zodb_id": sender_item.zodb_id if sender_item else None,
                "sender_item_name": sender_zodb_item.name if sender_zodb_item else "Unknown Item",
                "sender_item_description": sender_zodb_item.description if sender_zodb_item else "",
                "sender_item_price": sender_zodb_item.price if sender_zodb_item else "",
                "sender_item_image": sender_zodb_item.image if sender_zodb_item else "",
                
                "receiver_id": offer.receiver_id,
                "receiver_item_id": offer.receiver_item_id,
                "receiver_item_zodb_id": receiver_item.zodb_id if receiver_item else None,
                "receiver_item_name": receiver_zodb_item.name if receiver_zodb_item else "Unknown Item",
                "receiver_item_image": receiver_zodb_item.image if receiver_zodb_item else ""
            }
            
            detailed_offers.append(offer_data)
            
        return detailed_offers
        
    except Exception as e:
        return HTTPException(status_code=500, detail=f"Error fetching trade offers: {str(e)}")

@router.put("/trade-offers/{offer_id}/accept")
async def accept_offer(offer_id: int, request: Request, db: Session = Depends(get_db)):
    try:
        user_id = check_session_cookie(request)

        offer = db.query(TradeOffer).filter(
            TradeOffer.ID == offer_id,
            TradeOffer.receiver_id == user_id,
            TradeOffer.status == "pending"
        ).first()
        
        if not offer:
            return HTTPException(status_code=404, detail="Offer not found or already processed")

        offer.status = "accepted"
        db.commit()
        db.refresh(offer)

        match = Match(offer_id=offer.ID)
        db.add(match)
        db.commit()
        db.refresh(match)
        
        return {"message": "Offer accepted successfully", "match_id": match.ID}
        
    except Exception as e:
        db.rollback()
        return HTTPException(status_code=500, detail=f"Error accepting offer: {str(e)}")


@router.delete("/trade-offers/{offer_id}/reject")
async def reject_offer(offer_id: int, request: Request, db: Session = Depends(get_db)):
    try:
        user_id = check_session_cookie(request)

        offer = db.query(TradeOffer).filter(
            TradeOffer.ID == offer_id,
            TradeOffer.receiver_id == user_id,
            TradeOffer.status == "pending"
        ).first()
        
        if not offer:
            return HTTPException(status_code=404, detail="Offer not found or already processed")

        offer.status = "rejected"
        db.commit()
        
        return {"message": "Offer rejected successfully"}
        
    except Exception as e:
        db.rollback()
        return HTTPException(status_code=500, detail=f"Error rejecting offer: {str(e)}")

@router.post("/purchase-item/{item_id}")
def purchase_item(item_id: int, buyer_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.ID == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if not item.is_purchasable:
        raise HTTPException(status_code=400, detail="This item is not for sale")

    # Perform purchase logic (e.g., transfer ownership)
    item.userID = buyer_id  # Transfer ownership
    db.commit()
    
    return {"message": "Item purchased successfully", "new_owner": buyer_id}
