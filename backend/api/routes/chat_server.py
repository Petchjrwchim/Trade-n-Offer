from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import time
from app.db_setup import get_db
from api.models.TradeOffers import TradeOffer, Match, Item, User, PurchaseOffer
from app.zodb_setup import get_root
from app.getUserID import check_session_cookie
from api.services.firebase_service import (
    create_chat_room, send_message, get_messages, 
    mark_messages_as_read, get_unread_message_count,
    get_user_chat_rooms, get_total_unread_messages
)

router = APIRouter(tags=["Chat_System"])

def check_user_in_offer(user_id: int, offer: Any, offer_type: str) -> bool:
    """Check if a user is part of an offer (trade or purchase)"""
    str_user_id = str(user_id)
    
    if offer_type == "trade":
        str_sender_id = str(offer.sender_id)
        str_receiver_id = str(offer.receiver_id)
        return str_user_id == str_sender_id or str_user_id == str_receiver_id
    elif offer_type == "purchase":
        str_buyer_id = str(offer.buyer_id)
        str_seller_id = str(offer.seller_id)
        return str_user_id == str_buyer_id or str_user_id == str_seller_id
    
    return False

@router.get("/chat/accepted-offers")
async def get_accepted_offers(request: Request, db: Session = Depends(get_db)):
    try:
        user_id = check_session_cookie(request)
        offers = db.query(TradeOffer).filter(TradeOffer.sender_id == user_id, TradeOffer.status == "accepted").all()

        offer = []
        for item in offers:
            root = get_root()
            receiver_item_id = item.receiver_item_id
            receiver_item_zodb = db.query(Item).filter(Item.ID == receiver_item_id).first()
            sender_item_id = item.sender_item_id
            sender_item_zodb = db.query(Item).filter(Item.ID == sender_item_id).first()
            
            receiver_item_obj = root.get("trade_items", {}).get(receiver_item_zodb.zodb_id)
            sender_item_obj = root.get("trade_items", {}).get(sender_item_zodb.zodb_id)

            if receiver_item_obj and sender_item_obj:
                offer.append({
                    "trade_ID": item.ID,
                    "re_ID": item.receiver_id,
                    "re_item_name": receiver_item_obj.name,
                    "re_item_image": receiver_item_obj.image,
                    "se_ID": item.sender_id,
                    "se_item_name": sender_item_obj.name,
                    "se_item_image": sender_item_obj.image
                })
        return offer
    
    except Exception as e:
        print(f"Error in get_accepted_offers: {e}")

@router.get("/chat/chat-detail")
async def get_chat_detail(request: Request, db: Session = Depends(get_db)):
    try:
        offers = await get_accepted_offers()

        root = get_root()
        offer = []
        for item in offers:
            receiver_item_id = item.receiver_item_id
            receiver_item_zodb = db.query(Item).filter(Item.ID == receiver_item_id).first()
            sender_item_id = item.sender_item_id
            sender_item_zodb = db.query(Item).filter(Item.ID == sender_item_id).first()

            receiver_item_obj = root.get("trade_items", {}).get(receiver_item_zodb)
            sender_item_obj = root.get("trade_items", {}).get(sender_item_zodb)

            if receiver_item_obj and sender_item_obj:
                offer.append({
                    "re_item_name": receiver_item_obj.name,
                    "re_item_image": receiver_item_obj.image,
                    "se_item_name": sender_item_obj.name,
                    "se_item_image": sender_item_obj.image,

                })

        return offer
    except Exception as e:
        print(f"Error in get_accepted_offers: {e}")
        


@router.post("/chat/create-chat-room/{offer_id}")
async def create_chat_room_handler(offer_id: int, request: Request, db: Session = Depends(get_db)):
    """Create a chat room for an accepted offer"""
    try:
        user_id = check_session_cookie(request)
        
        offer = db.query(TradeOffer).filter(
            TradeOffer.ID == offer_id,
            TradeOffer.status == "accepted"
        ).first()
        
        if not offer:
            raise HTTPException(status_code=404, detail="Accepted offer not found")
        
        # Verify that the current user is part of this offer
        if not check_user_in_offer(user_id, offer):
            raise HTTPException(status_code=403, detail="Not authorized to create this chat")
        
        # Create a chat room in Firebase
        success = create_chat_room(offer_id, offer.sender_id, offer.receiver_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to create chat room")
        
        return {"message": "Chat room created or already exists", "offer_id": offer_id}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in create_chat_room_handler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/send-message/{offer_id}")
async def send_message_handler(offer_id: int, message_data: Dict[str, Any], request: Request, db: Session = Depends(get_db)):
    """Send a message to a chat room for either trade or purchase offer"""
    try:
        # Get current user ID from the session cookie
        user_id = check_session_cookie(request)
        print(f"Message sender user ID: {user_id}")
        
        # Check both trade and purchase offers
        trade_offer = db.query(TradeOffer).filter(TradeOffer.ID == offer_id).first()
        purchase_offer = db.query(PurchaseOffer).filter(PurchaseOffer.ID == offer_id).first()
        
        if trade_offer:
            # Verify that the current user is part of this offer
            if not check_user_in_offer(user_id, trade_offer, "trade"):
                print(f"Authorization failed: user_id={user_id}, sender_id={trade_offer.sender_id}, receiver_id={trade_offer.receiver_id}")
                raise HTTPException(status_code=403, detail="Not authorized to send messages in this trade chat")
        
        elif purchase_offer:
            # Verify that the current user is part of this offer
            if not check_user_in_offer(user_id, purchase_offer, "purchase"):
                print(f"Authorization failed: user_id={user_id}, buyer_id={purchase_offer.buyer_id}, seller_id={purchase_offer.seller_id}")
                raise HTTPException(status_code=403, detail="Not authorized to send messages in this purchase chat")
        
        else:
            raise HTTPException(status_code=404, detail="Offer not found")
        
        # Get the message content and image data
        content = message_data.get("message", "")
        image_data = message_data.get("image", None)
        
        # Ensure either text or image is provided
        if not content.strip() and not image_data:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Send message to Firebase
        message_id = send_message(offer_id, user_id, content, image_data)
        
        if not message_id:
            raise HTTPException(status_code=500, detail="Failed to send message")
        
        # Get the message data to return to the client (including the correct image URL)
        all_messages = get_messages(offer_id)
        new_message = next((msg for msg in all_messages if msg.get('id') == message_id), None)
        
        if not new_message:
            # If we can't find the message, create a basic response
            new_message = {
                "id": message_id,
                "user_id": user_id,
                "content": content,
                "timestamp": int(time.time() * 1000),
                "has_image": image_data is not None
            }
        
        print(f"Message sent: {new_message}")
        return {"message": "Message sent successfully", "data": new_message}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in send_message_handler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/messages/{offer_id}")
async def get_messages_handler(offer_id: int, request: Request, db: Session = Depends(get_db)):
    """Get all messages for a chat room for either trade or purchase offer"""
    try:
        user_id = check_session_cookie(request)
        
        # Check both trade and purchase offers
        trade_offer = db.query(TradeOffer).filter(TradeOffer.ID == offer_id).first()
        purchase_offer = db.query(PurchaseOffer).filter(PurchaseOffer.ID == offer_id).first()
        
        if trade_offer:
            # Verify that the current user is part of this offer
            if not check_user_in_offer(user_id, trade_offer, "trade"):
                raise HTTPException(status_code=403, detail="Not authorized to view messages in this trade chat")
        
        elif purchase_offer:
            # Verify that the current user is part of this offer
            if not check_user_in_offer(user_id, purchase_offer, "purchase"):
                raise HTTPException(status_code=403, detail="Not authorized to view messages in this purchase chat")
        
        else:
            raise HTTPException(status_code=404, detail="Offer not found")
        
        # Get messages from Firebase
        messages = get_messages(offer_id)
        
        # Ensure all messages with has_image=True have an image_url
        for message in messages:
            if message.get('has_image') and not message.get('image_url'):
                print(f"Warning: Message {message.get('id')} missing image_url")
                # Add a placeholder in development
                if 'image_url' not in message:
                    message['image_url'] = f"https://via.placeholder.com/300?text=Image+{message['id']}"
        
        # Mark messages as read
        mark_messages_as_read(offer_id, user_id)
        
        return {"messages": messages}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_messages_handler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/mark-as-read/{offer_id}")
async def mark_as_read_handler(offer_id: int, request: Request, db: Session = Depends(get_db)):
    """Mark all messages in a chat room as read"""
    try:
        user_id = check_session_cookie(request)
        
        # Check if the offer exists and is accepted
        offer = db.query(TradeOffer).filter(
            TradeOffer.ID == offer_id,
            TradeOffer.status == "accepted"
        ).first()
        
        if not offer:
            raise HTTPException(status_code=404, detail="Accepted offer not found")
        
        # Verify that the current user is part of this offer
        if not check_user_in_offer(user_id, offer):
            raise HTTPException(status_code=403, detail="Not authorized for this chat")
        
        # Mark messages as read
        success = mark_messages_as_read(offer_id, user_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to mark messages as read")
        
        return {"message": "Messages marked as read"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in mark_as_read_handler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/unread-count/{offer_id}")
async def get_unread_count_handler(offer_id: int, request: Request, db: Session = Depends(get_db)):
    """Get the number of unread messages for a chat room"""
    try:
        user_id = check_session_cookie(request)
        
        # Check if the offer exists and is accepted
        offer = db.query(TradeOffer).filter(
            TradeOffer.ID == offer_id,
            TradeOffer.status == "accepted"
        ).first()
        
        if not offer:
            raise HTTPException(status_code=404, detail="Accepted offer not found")
        
        # Verify that the current user is part of this offer
        if not check_user_in_offer(user_id, offer):
            raise HTTPException(status_code=403, detail="Not authorized for this chat")
        
        # Get unread message count
        unread_count = get_unread_message_count(offer_id, user_id)
        
        return {"unread_count": unread_count}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_unread_count_handler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/total-unread")
async def get_total_unread_handler(request: Request):
    """Get the total number of unread messages across all chat rooms"""
    try:
        user_id = check_session_cookie(request)
        
        # Get total unread message count
        total_unread = get_total_unread_messages(user_id)
        
        return {"total_unread": total_unread}
    except Exception as e:
        print(f"Error in get_total_unread_handler: {e}")
        raise HTTPException(status_code=500, detail=str(e))