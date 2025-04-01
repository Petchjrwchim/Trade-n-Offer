from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from app.db_setup import get_db  # This should provide a SQLAlchemy session
from api.models.TradeOffers import Item, User  # SQLAlchemy model for trade_items
from app.zodb_setup import get_root, commit_changes, close_connection
from app.getUserID import check_session_cookie
from fastapi.responses import JSONResponse
from api.models.item_class import TradeItem
from api.models.TradeOffers import Item, User, TradeOffer, Match  # SQLAlchemy models

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
    is_available = item.get("is_available", True)

    if not item_name:
        raise HTTPException(status_code=400, detail="Item name must be provided")

    root = get_root()

    if "trade_items" not in root:
        root["trade_items"] = {}

    new_item_id = len(root["trade_items"]) + 1

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
    

@router.get("/get-trade-offers")
async def get_trade_offers(request: Request, db: Session = Depends(get_db)):
    try:
        # ตรวจสอบ session token
        user_id = check_session_cookie(request)
        
        # ดึงข้อเสนอที่ส่งถึงผู้ใช้ปัจจุบัน และมีสถานะ "pending"
        offers = db.query(TradeOffer).filter(
            TradeOffer.receiver_id == user_id,
            TradeOffer.status == "pending"
        ).all()
        
        if not offers:
            return []
        
        # ดึงข้อมูลเพิ่มเติมสำหรับแต่ละข้อเสนอ
        root = get_root()
        trade_items = root.get("trade_items", {})
        
        detailed_offers = []
        for offer in offers:
            # ดึงข้อมูลผู้ส่ง
            sender = db.query(User).filter(User.ID == offer.sender_id).first()
            
            # ดึงข้อมูลรายการของผู้ส่ง
            sender_item = db.query(Item).filter(Item.ID == offer.sender_item_id).first()
            sender_zodb_item = trade_items.get(sender_item.zodb_id) if sender_item else None
            
            # ดึงข้อมูลรายการของผู้รับ
            receiver_item = db.query(Item).filter(Item.ID == offer.receiver_item_id).first()
            receiver_zodb_item = trade_items.get(receiver_item.zodb_id) if receiver_item else None
            
            # สร้างข้อมูลข้อเสนอที่มีรายละเอียดเพิ่มเติม
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
        # ตรวจสอบ session token
        user_id = check_session_cookie(request)
        
        # ตรวจสอบว่าข้อเสนอมีอยู่จริงและเป็นของผู้ใช้ปัจจุบัน
        offer = db.query(TradeOffer).filter(
            TradeOffer.ID == offer_id,
            TradeOffer.receiver_id == user_id,
            TradeOffer.status == "pending"
        ).first()
        
        if not offer:
            return HTTPException(status_code=404, detail="Offer not found or already processed")
        
        # อัปเดตสถานะข้อเสนอเป็น "accepted"
        offer.status = "accepted"
        db.commit()
        db.refresh(offer)
        
        # สร้างรายการ match
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
        # ตรวจสอบ session token
        user_id = check_session_cookie(request)
        
        # ตรวจสอบว่าข้อเสนอมีอยู่จริงและเป็นของผู้ใช้ปัจจุบัน
        offer = db.query(TradeOffer).filter(
            TradeOffer.ID == offer_id,
            TradeOffer.receiver_id == user_id,
            TradeOffer.status == "pending"
        ).first()
        
        if not offer:
            return HTTPException(status_code=404, detail="Offer not found or already processed")
        
        # อัปเดตสถานะข้อเสนอเป็น "rejected"
        offer.status = "rejected"
        db.commit()
        
        return {"message": "Offer rejected successfully"}
        
    except Exception as e:
        db.rollback()
        return HTTPException(status_code=500, detail=f"Error rejecting offer: {str(e)}")