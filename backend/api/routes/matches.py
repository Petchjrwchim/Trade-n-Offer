from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from api.models.TradeOffers import TradeOffer, Match, Item
from app.db_setup import get_db

router = APIRouter(tags=["matches_management"])

# @router.put("/accept_offer/")
# def accept_offer(offer_id: int, db: Session = Depends(get_db)):
#     db_offer = db.query(TradeOffer).filter(TradeOffer.ID == offer_id).first()
#     if not db_offer:
#         raise HTTPException(status_code=404, detail="Offer not found")
    
#     db_offer.status = "accepted"
#     db.commit()
#     db.refresh(db_offer)

#     # Create the match entry
#     match = Match(offer_id=db_offer.ID)
#     db.add(match)
#     db.commit()
#     db.refresh(match)
    
#     return {"message": "Offer accepted, match created", "match": match}

@router.put("/trade-offers/{offer_id}/complete")
def complete_trade(offer_id: int, db: Session = Depends(get_db)):
    db_offer = db.query(TradeOffer).filter(TradeOffer.ID == offer_id).first()
    if not db_offer:
        raise HTTPException(status_code=404, detail="Offer not found")

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

@router.put("/trade-offers/{offer_id}/cancel")
def cancel_trade(offer_id: int, db: Session = Depends(get_db)):
    db_offer = db.query(TradeOffer).filter(TradeOffer.ID == offer_id).first()
    if not db_offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    db_match = db.query(Match).filter(Match.offer_id == db_offer.ID).first()
    if not db_match:
        raise HTTPException(status_code=404, detail="Match not found")

    db_match.status = "cancelled"
    db.commit()
    db.refresh(db_match)

    return {"message": "Trade cancelled", "match": db_match}

@router.get("/get_active_matches/{user_id}")
def get_active_matches(user_id: int, db: Session = Depends(get_db)):
    matches = db.query(Match).join(TradeOffer).filter(
        (TradeOffer.sender_id == user_id) | (TradeOffer.receiver_id == user_id),
        Match.status == "active"
    ).all()
    return matches
