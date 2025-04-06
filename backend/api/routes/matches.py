from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from api.models.TradeOffers import TradeOffer, Match, Item, PurchaseOffer
from app.db_setup import get_db

router = APIRouter(tags=["matches_management"])

@router.put("/trade-offers/{offer_id}/complete")
def complete_trade(offer_id: int, db: Session = Depends(get_db)):
    db_offer = db.query(TradeOffer).filter(TradeOffer.ID == offer_id).first()
    if not db_offer:
        raise HTTPException(status_code=404, detail="Trade Offer not found")

    db_match = db.query(Match).filter(Match.offer_id == db_offer.ID).first()
    if not db_match:
        raise HTTPException(status_code=404, detail="Match not found")

    db_match.status = "completed"
    db.commit()
    db.refresh(db_match)

    sender_item = db.query(Item).filter(Item.ID == db_offer.sender_item_id).first()
    receiver_item = db.query(Item).filter(Item.ID == db_offer.receiver_item_id).first()

    sender_item.user_id = db_offer.receiver_id
    receiver_item.user_id = db_offer.sender_id
    db.commit()

    return {"message": "Trade completed successfully", "match": db_match}

@router.put("/purchase-offers/{offer_id}/complete")
def complete_purchase(offer_id: int, db: Session = Depends(get_db)):
    db_offer = db.query(PurchaseOffer).filter(PurchaseOffer.ID == offer_id).first()
    if not db_offer:
        raise HTTPException(status_code=404, detail="Purchase Offer not found")

    # Update offer status
    db_offer.status = "accepted"
    
    # Update item ownership
    item = db.query(Item).filter(Item.ID == db_offer.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Transfer ownership
    item.userID = db_offer.buyer_id
    item.is_available = False  # Mark item as sold
    
    db.commit()

    return {"message": "Purchase completed successfully", "offer_id": offer_id}

@router.put("/trade-offers/{offer_id}/cancel")
def cancel_trade(offer_id: int, db: Session = Depends(get_db)):
    db_offer = db.query(TradeOffer).filter(TradeOffer.ID == offer_id).first()
    if not db_offer:
        raise HTTPException(status_code=404, detail="Trade Offer not found")

    db_match = db.query(Match).filter(Match.offer_id == db_offer.ID).first()
    if not db_match:
        raise HTTPException(status_code=404, detail="Match not found")

    db_match.status = "cancelled"
    db.commit()
    db.refresh(db_match)

    return {"message": "Trade cancelled", "match": db_match}

@router.put("/purchase-offers/{offer_id}/cancel")
def cancel_purchase(offer_id: int, db: Session = Depends(get_db)):
    db_offer = db.query(PurchaseOffer).filter(PurchaseOffer.ID == offer_id).first()
    if not db_offer:
        raise HTTPException(status_code=404, detail="Purchase Offer not found")

    # Update offer status
    db_offer.status = "rejected"
    db.commit()

    return {"message": "Purchase cancelled", "offer_id": offer_id}

@router.get("/get_active_matches/{user_id}")
def get_active_matches(user_id: int, db: Session = Depends(get_db)):
    # Get active trade matches
    trade_matches = db.query(Match).join(TradeOffer).filter(
        (TradeOffer.sender_id == user_id) | (TradeOffer.receiver_id == user_id),
        Match.status == "active"
    ).all()
    
    # Get active purchase offers
    purchase_offers = db.query(PurchaseOffer).filter(
        (PurchaseOffer.buyer_id == user_id) | (PurchaseOffer.seller_id == user_id),
        PurchaseOffer.status == "pending"
    ).all()
    
    return {
        "trade_matches": trade_matches,
        "purchase_offers": purchase_offers
    }

@router.put("/trade-offers/{offer_id}/status")
def update_trade_status(offer_id: int, status_data: dict, db: Session = Depends(get_db)):
    new_status = status_data.get("status")
    
    if not new_status or new_status not in ["active", "completed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    db_match = db.query(Match).filter(Match.offer_id == offer_id).first()
    if not db_match:
        raise HTTPException(status_code=404, detail="Match not found")

    # Get the offer details
    db_offer = db.query(TradeOffer).filter(TradeOffer.ID == offer_id).first()
    if not db_offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    # Get the items
    sender_item = db.query(Item).filter(Item.ID == db_offer.sender_item_id).first()
    receiver_item = db.query(Item).filter(Item.ID == db_offer.receiver_item_id).first()
    
    if not sender_item or not receiver_item:
        raise HTTPException(status_code=404, detail="Items not found")

    # Update the match status
    db_match.status = new_status
    
    # Handle item availability based on new status
    if new_status == "completed":
        # Mark both items as unavailable when completed
        sender_item.is_available = False
        receiver_item.is_available = False
    elif new_status in ["active", "cancelled"]:
        # Mark both items as available if reverting to active or cancelled
        sender_item.is_available = True
        receiver_item.is_available = True
    
    # Commit changes
    db.commit()
    db.refresh(db_match)
    
    return {
        "message": f"Match status updated to {new_status}",
        "status": new_status,
        "match_id": db_match.ID,
        "offer_id": offer_id
    }

@router.put("/purchase-offers/{offer_id}/status")
def update_purchase_status(offer_id: int, status_data: dict, db: Session = Depends(get_db)):
    new_status = status_data.get("status")
    
    if not new_status or new_status not in ["pending", "accepted", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    # Get the purchase offer
    db_offer = db.query(PurchaseOffer).filter(PurchaseOffer.ID == offer_id).first()
    if not db_offer:
        raise HTTPException(status_code=404, detail="Purchase offer not found")

    # Get the item
    item = db.query(Item).filter(Item.ID == db_offer.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Update the offer status
    db_offer.status = new_status
    
    # Handle item availability based on new status
    if new_status == "accepted":
        # Mark item as unavailable when accepted
        item.is_available = False
        item.userID = db_offer.buyer_id
    elif new_status in ["pending", "rejected"]:
        # Mark item as available if pending or rejected
        item.is_available = True
    
    # Commit changes
    db.commit()
    
    return {
        "message": f"Purchase offer status updated to {new_status}",
        "status": new_status,
        "offer_id": offer_id
    }

@router.get("/trade-offers/{offer_id}/match-status")
def get_trade_match_status(offer_id: int, db: Session = Depends(get_db)):
    """Get the current status of a match for a trade offer"""
    print(f"Getting match status for trade offer {offer_id}")
    
    # Find the match for this offer
    db_match = db.query(Match).filter(Match.offer_id == offer_id).first()
    
    if not db_match:
        # If no match exists, check if offer exists
        db_offer = db.query(TradeOffer).filter(TradeOffer.ID == offer_id).first()
        if not db_offer:
            raise HTTPException(status_code=404, detail="Trade offer not found")
            
        # If offer exists but match doesn't, create a new match with active status
        if db_offer.status == "accepted":
            db_match = Match(offer_id=offer_id, status="active")
            db.add(db_match)
            db.commit()
            db.refresh(db_match)
            
            return {"status": db_match.status, "match_id": db_match.ID, "type": "trade"}
        else:
            # Not an accepted offer
            raise HTTPException(status_code=400, detail="Trade offer not yet accepted")
    
    # Return the status
    return {"status": db_match.status, "match_id": db_match.ID, "type": "trade"}

@router.get("/purchase-offers/{offer_id}/status")
def get_purchase_offer_status(offer_id: int, db: Session = Depends(get_db)):
    """Get the current status of a purchase offer"""
    print(f"Getting status for purchase offer {offer_id}")
    
    # Find the purchase offer
    db_offer = db.query(PurchaseOffer).filter(PurchaseOffer.ID == offer_id).first()
    
    if not db_offer:
        raise HTTPException(status_code=404, detail="Purchase offer not found")
    
    return {
        "status": db_offer.status, 
        "offer_id": offer_id, 
        "type": "purchase"
    }