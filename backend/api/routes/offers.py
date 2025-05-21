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
def create_offer(request: Request, offer: dict, db: Session = Depends(get_db)):
    try:
        # ตรวจสอบว่าผู้ใช้เข้าสู่ระบบแล้ว
        user_id = check_session_cookie(request)
        
        # ดึงข้อมูลจาก body และแปลงเป็น integer
        receiver_id = int(offer.get("receiver_id"))
        sender_item_id = int(offer.get("sender_item_id"))
        receiver_item_id = int(offer.get("receiver_item_id"))
        
        # ตรวจสอบว่าข้อมูลมีครบถ้วน
        if not all([receiver_id, sender_item_id, receiver_item_id]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # ตรวจสอบว่าผู้ใช้เป็นเจ้าของ item ที่ส่ง
        sender_item = db.query(Item).filter(Item.ID == sender_item_id).first()
        if not sender_item:
            raise HTTPException(status_code=404, detail="Sender item not found")
            
        
        # ตรวจสอบว่า receiver เป็นเจ้าของ item ที่ต้องการ
        receiver_item = db.query(Item).filter(Item.ID == receiver_item_id).first()
        if not receiver_item:
            raise HTTPException(status_code=404, detail="Receiver item not found")
            
        if receiver_item.userID != receiver_id:
            raise HTTPException(
                status_code=400, 
                detail=f"Receiver doesn't own the requested item. Receiver ID: {receiver_id}, Item owner: {receiver_item.userID}"
            )
        
        # ตรวจสอบว่ามี offer ที่ active อยู่สำหรับสินค้าเหล่านี้หรือไม่
        existing_offer = db.query(TradeOffer).filter(TradeOffer.sender_item_id == sender_item_id , TradeOffer.receiver_item_id == receiver_item_id).first()
        if existing_offer:
            raise HTTPException(
                status_code=400, 
                detail="One or both items are ready involveasdasdasd525555d in an active trade offer"
            )
        
        # สร้าง offer ใหม่
        new_offer = TradeOffer(
            sender_id=user_id,
            receiver_id=receiver_id,
            sender_item_id=sender_item_id,
            receiver_item_id=receiver_item_id,
            status="pending"
        )
        
        db.add(new_offer)
        db.commit()
        db.refresh(new_offer)
        
        return {
            "message": "Trade offer created successfully", 
            "offer_id": new_offer.ID
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid ID format: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating trade offer: {str(e)}")
    

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

@router.get("/get-item/{item_id}")
async def get_item_details(
    item_id: int, 
    request: Request, 
    db: Session = Depends(get_db)
):
    try:
        # ดึงข้อมูลจาก SQL database
        item = db.query(Item).filter(Item.ID == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # ดึงข้อมูลจาก ZODB
        root = get_root()
        zodb_data = root.get("trade_items", {}).get(item.zodb_id)
        
        if not zodb_data:
            raise HTTPException(
                status_code=404, 
                detail="Item details not found in ZODB"
            )
        
        # ดึงข้อมูลผู้ใช้ (owner)
        owner = db.query(User).filter(User.ID == item.userID).first()
        
        # สร้าง response data - ตรงกับโครงสร้างโมเดลและตารางจริง
        item_data = {
            "ID": item.ID,
            "userID": item.userID,
            "owner_username": owner.UserName if owner else "Unknown",
            "zodb_id": item.zodb_id,
            "is_purchasable": item.is_purchasable,  # ตรงกับโมเดล is_purchasable (ไม่ใช่ is_purchaseble)
            "is_available": item.is_available,
            "is_tradeable": item.is_tradeable,
            "name": getattr(zodb_data, 'name', None),
            "description": getattr(zodb_data, 'description', None),
            "price": getattr(zodb_data, 'price', None),
            "image": getattr(zodb_data, 'image', None),
            "category": getattr(zodb_data, 'category', None)
        }
        
        return item_data
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching item details: {str(e)}"
        )

@router.get("/check-item-availability/{item_id}")
async def check_item_availability(item_id: int, request: Request, db: Session = Depends(get_db)):
    try:
        user_id = check_session_cookie(request)
        
        # ตรวจสอบว่าสินค้านี้มี offer ที่ active อยู่หรือไม่
        existing_offer = db.query(TradeOffer).filter(
            (TradeOffer.sender_item_id == item_id) | (TradeOffer.receiver_item_id == item_id),
            TradeOffer.status == "pending"
        ).first()
        
        if existing_offer:
            return {
                "available": False,
                "message": "This item is currently involved in an active trade offer"
            }
        
        return {
            "available": True,
            "message": "This item is available for trading"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking item availability: {str(e)}")