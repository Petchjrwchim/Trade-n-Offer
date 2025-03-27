from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db_setup import get_db
from api.models.TradeOffers import TradeOffer, Match, Item

router = APIRouter(tags=["Offers_management"])

@router.post("/C-offers")
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

@router.get("/trade-offers/")
def get_trade_offers(db: Session = Depends(get_db)):
    trade_ofers = db.query(TradeOffer).all()
    return trade_ofers

# @router.put("/trade-offers/{offer_id}/accept")
# def accept_offer(offer_id: int, db: Session = Depends(get_db)):
#     db_offer = db.query(TradeOffer).filter(TradeOffer.ID == offer_id).first()
#     if not db_offer:
#         raise HTTPException(status_code=404, detail="OFfer not found")
#     db_offer.status = "accepted"
#     db.commit()
#     db.refresh(db_offer)
#     return db_offer

@router.put("/trade-offers/{offer_id}/accept")
def accept_offer(offer_id: int, db: Session = Depends(get_db)):
    db_offer = db.query(TradeOffer).filter(TradeOffer.ID == offer_id).first()
    if not db_offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    db_offer.status = "accepted"
    db.commit()
    db.refresh(db_offer)

    match = Match(offer_id=db_offer.ID)
    db.add(match)
    db.commit()
    db.refresh(match)

    return {"message": "Offer accepted, match created", "match": match}


@router.delete("/trade-offers/{offer_id}/reject")
def reject_offer(offer_id: int, db: Session = Depends(get_db)):
    db_offer = db.query(TradeOffer).filter(TradeOffer.ID == offer_id).first()
    if not db_offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    db.delete(db_offer)
    db.commit()

    return {"message": "Offer rejected and removed"}

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
