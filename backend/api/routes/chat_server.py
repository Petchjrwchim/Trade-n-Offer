from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import time
from app.db_setup import get_db
from api.models.TradeOffers import TradeOffer, Match, Item, User, PurchaseOffer
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
        # Get current user ID from session
        user_id = check_session_cookie(request)
        print(f"Current user ID: {user_id}")
        
        # Import ZODB root to fetch item details
        from app.zodb_setup import get_root
        root = get_root()
        
        result = []
        
        # Get accepted trade offers
        trade_offers = db.query(TradeOffer).filter(
            (TradeOffer.sender_id == user_id) | (TradeOffer.receiver_id == user_id),
            TradeOffer.status == "accepted"
        ).all()
        
        print(f"Found {len(trade_offers)} accepted trade offers")
        
        for offer in trade_offers:
            print(f"Processing offer ID: {offer.ID}")
            print(f"Sender ID: {offer.sender_id}, Receiver ID: {offer.receiver_id}")
            print(f"Sender item ID: {offer.sender_item_id}, Receiver item ID: {offer.receiver_item_id}")
            
            # First, get the database items directly
            sender_db_item = db.query(Item).filter(Item.ID == offer.sender_item_id).first()
            receiver_db_item = db.query(Item).filter(Item.ID == offer.receiver_item_id).first()
            
            if not sender_db_item or not receiver_db_item:
                print(f"Warning: Missing database items for offer {offer.ID}")
                continue
                
            print(f"Sender item ZODB ID: {sender_db_item.zodb_id}, Receiver item ZODB ID: {receiver_db_item.zodb_id}")
            
            # Now get the ZODB items using the zodb_id from the database items
            sender_zodb_item = root.get("trade_items", {}).get(sender_db_item.zodb_id)
            receiver_zodb_item = root.get("trade_items", {}).get(receiver_db_item.zodb_id)
            
            if not sender_zodb_item or not receiver_zodb_item:
                print(f"Warning: Missing ZODB items for offer {offer.ID}")
            
            # Get other user based on who the current user is
            if str(offer.sender_id) == str(user_id):
                # Current user is sender
                other_user_id = offer.receiver_id
                is_sender = True
                # If user is sender, they're giving sender_item and getting receiver_item
                my_item_image = sender_zodb_item.image if sender_zodb_item and hasattr(sender_zodb_item, 'image') else "/static/image_test/camera.jpg"
                other_item_image = receiver_zodb_item.image if receiver_zodb_item and hasattr(receiver_zodb_item, 'image') else "/static/image_test/guitar.jpg"
                my_item_name = sender_zodb_item.name if sender_zodb_item and hasattr(sender_zodb_item, 'name') else "My Item"
                other_item_name = receiver_zodb_item.name if receiver_zodb_item and hasattr(receiver_zodb_item, 'name') else "Their Item"
            else:
                # Current user is receiver
                other_user_id = offer.sender_id
                is_sender = False
                # If user is receiver, they're giving receiver_item and getting sender_item
                my_item_image = receiver_zodb_item.image if receiver_zodb_item and hasattr(receiver_zodb_item, 'image') else "/static/image_test/guitar.jpg"
                other_item_image = sender_zodb_item.image if sender_zodb_item and hasattr(sender_zodb_item, 'image') else "/static/image_test/camera.jpg"
                my_item_name = receiver_zodb_item.name if receiver_zodb_item and hasattr(receiver_zodb_item, 'name') else "My Item"
                other_item_name = sender_zodb_item.name if sender_zodb_item and hasattr(sender_zodb_item, 'name') else "Their Item"
            
            # Get other user details
            other_user = db.query(User).filter(User.ID == other_user_id).first()
            
            # Prepare offer data with item details
            offer_data = {
                "offer_id": offer.ID,
                "offer_type": "trade",
                "other_user_id": other_user.ID if other_user else None,
                "other_user_name": other_user.UserName if other_user else "Unknown User",
                
                # Sender item details - these are the consistent labels used by the frontend
                "sender_item_id": offer.sender_item_id,
                "sender_item_zodb_id": sender_db_item.zodb_id,
                "sender_item_name": sender_zodb_item.name if sender_zodb_item and hasattr(sender_zodb_item, 'name') else "Unnamed Item",
                "sender_item_image": sender_zodb_item.image if sender_zodb_item and hasattr(sender_zodb_item, 'image') else "/static/image_test/camera.jpg",
                
                # Receiver item details - these are the consistent labels used by the frontend
                "receiver_item_id": offer.receiver_item_id,
                "receiver_item_zodb_id": receiver_db_item.zodb_id,
                "receiver_item_name": receiver_zodb_item.name if receiver_zodb_item and hasattr(receiver_zodb_item, 'name') else "Unnamed Item",
                "receiver_item_image": receiver_zodb_item.image if receiver_zodb_item and hasattr(receiver_zodb_item, 'image') else "/static/image_test/guitar.jpg",
                
                # User role flag - this is what the frontend uses to know which item to show
                "is_sender": is_sender,
                "created_at": offer.created_at.isoformat() if offer.created_at else None,
                
                # Extra fields to help debug
                "my_item_name": my_item_name,
                "my_item_image": my_item_image,
                "other_item_name": other_item_name,
                "other_item_image": other_item_image,
                
                # Match status info - important for chat status display
                "status": "active",  # Default for trade offers with status "accepted"
                
                # Placeholder for last message and unread count
                "last_message": None,
                "unread_count": 0
            }
            
            # Try to get match status for trade offers
            match = db.query(Match).filter(Match.offer_id == offer.ID).first()
            if match:
                offer_data["status"] = match.status  # Update with actual match status
            
            result.append(offer_data)
            
        # Get active purchase offers
        purchase_offers = db.query(PurchaseOffer).filter(
            (PurchaseOffer.buyer_id == user_id) | (PurchaseOffer.seller_id == user_id),
            PurchaseOffer.status == "active"  # Only include active purchase offers
        ).all()
        
        print(f"Found {len(purchase_offers)} active purchase offers")
        
        for offer in purchase_offers:
            # Determine if current user is buyer or seller
            if str(offer.buyer_id) == str(user_id):
                other_user_id = offer.seller_id
                is_buyer = True
            else:
                other_user_id = offer.buyer_id
                is_buyer = False
            
            # Get other user details
            other_user = db.query(User).filter(User.ID == other_user_id).first()
            
            # Get the item in the purchase
            purchase_item = db.query(Item).filter(Item.ID == offer.item_id).first()
            if not purchase_item:
                print(f"Warning: Missing database item for purchase offer {offer.ID}")
                continue
            
            # Fetch ZODB item details
            zodb_item = root.get("trade_items", {}).get(purchase_item.zodb_id) if purchase_item else None
            if not zodb_item:
                print(f"Warning: Missing ZODB item for purchase offer {offer.ID}")
            
            # Prepare offer data
            offer_data = {
                "offer_id": offer.ID,
                "offer_type": "purchase",
                "other_user_id": other_user.ID if other_user else None,
                "other_user_name": other_user.UserName if other_user else "Unknown User",
                
                # Item details
                "item_id": purchase_item.ID if purchase_item else None,
                "item_zodb_id": purchase_item.zodb_id if purchase_item else None,
                "item_name": zodb_item.name if zodb_item and hasattr(zodb_item, 'name') else "Unnamed Item",
                "item_image": zodb_item.image if zodb_item and hasattr(zodb_item, 'image') else "/static/image_test/camera.jpg",
                "item_price": zodb_item.price if zodb_item and hasattr(zodb_item, 'price') else "",
                
                # User role info
                "is_buyer": is_buyer,
                "buyerName": "You" if is_buyer else (other_user.UserName if other_user else "Unknown Buyer"),
                "sellerName": "You" if not is_buyer else (other_user.UserName if other_user else "Unknown Seller"),
                
                # Status info
                "status": offer.status,
                "created_at": offer.created_at.isoformat() if offer.created_at else None,
                
                # Placeholder for last message and unread count
                "last_message": None,
                "unread_count": 0
            }
            
            result.append(offer_data)
        
        return result
    
    except Exception as e:
        print(f"Error in get_accepted_offers: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/create-chat-room/{offer_id}")
async def create_chat_room_handler(
    offer_id: int, 
    offer_type: str = "trade",
    request: Request = None, 
    db: Session = Depends(get_db)
):
    """Create a chat room for an accepted trade offer or active purchase offer"""
    try:
        user_id = check_session_cookie(request)
        
        if offer_type == "trade":
            # Check if the trade offer exists and is accepted
            offer = db.query(TradeOffer).filter(
                TradeOffer.ID == offer_id,
                TradeOffer.status == "accepted"
            ).first()
            
            if not offer:
                raise HTTPException(status_code=404, detail="Accepted trade offer not found")
            
            # Verify that the current user is part of this offer
            if not check_user_in_offer(user_id, offer, offer_type):
                raise HTTPException(status_code=403, detail="Not authorized to create this chat")
            
            # Create a chat room in Firebase
            success = create_chat_room(offer_id, offer.sender_id, offer.receiver_id)
        
        elif offer_type == "purchase":
            # Check if the purchase offer exists and is active
            offer = db.query(PurchaseOffer).filter(
                PurchaseOffer.ID == offer_id,
                PurchaseOffer.status == "active"
            ).first()
            
            if not offer:
                raise HTTPException(status_code=404, detail="Active purchase offer not found")
            
            # Verify that the current user is part of this offer
            if not check_user_in_offer(user_id, offer, offer_type):
                raise HTTPException(status_code=403, detail="Not authorized to create this chat")
            
            # Create a chat room in Firebase
            success = create_chat_room(offer_id, offer.buyer_id, offer.seller_id)
        
        else:
            raise HTTPException(status_code=400, detail="Invalid offer type")
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to create chat room")
        
        return {
            "message": "Chat room created or already exists", 
            "offer_id": offer_id,
            "offer_type": offer_type
        }
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
        
        # Check both trade and purchase offers
        trade_offer = db.query(TradeOffer).filter(TradeOffer.ID == offer_id).first()
        purchase_offer = db.query(PurchaseOffer).filter(PurchaseOffer.ID == offer_id).first()
        
        if trade_offer:
            # Verify that the current user is part of this offer
            if not check_user_in_offer(user_id, trade_offer, "trade"):
                raise HTTPException(status_code=403, detail="Not authorized for this chat")
        
        elif purchase_offer:
            # Verify that the current user is part of this offer
            if not check_user_in_offer(user_id, purchase_offer, "purchase"):
                raise HTTPException(status_code=403, detail="Not authorized for this chat")
        
        else:
            raise HTTPException(status_code=404, detail="Offer not found")
        
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
        
        # Check both trade and purchase offers
        trade_offer = db.query(TradeOffer).filter(TradeOffer.ID == offer_id).first()
        purchase_offer = db.query(PurchaseOffer).filter(PurchaseOffer.ID == offer_id).first()
        
        if trade_offer:
            # Verify that the current user is part of this offer
            if not check_user_in_offer(user_id, trade_offer, "trade"):
                raise HTTPException(status_code=403, detail="Not authorized for this chat")
        
        elif purchase_offer:
            # Verify that the current user is part of this offer
            if not check_user_in_offer(user_id, purchase_offer, "purchase"):
                raise HTTPException(status_code=403, detail="Not authorized for this chat")
        
        else:
            raise HTTPException(status_code=404, detail="Offer not found")
        
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

@router.get("/trade-offers/{offer_id}/match-status")
async def get_trade_match_status(offer_id: int, request: Request, db: Session = Depends(get_db)):
    """Get the status of a trade match"""
    try:
        user_id = check_session_cookie(request)
        
        # Get the trade offer
        trade_offer = db.query(TradeOffer).filter(TradeOffer.ID == offer_id).first()
        
        if not trade_offer:
            raise HTTPException(status_code=404, detail="Trade offer not found")
        
        # Verify that the current user is part of this offer
        if not check_user_in_offer(user_id, trade_offer, "trade"):
            raise HTTPException(status_code=403, detail="Not authorized to view this trade")
        
        # Get the match status
        match = db.query(Match).filter(Match.offer_id == offer_id).first()
        
        if not match:
            # If no match exists yet, create one with default active status
            match = Match(offer_id=offer_id, status="active")
            db.add(match)
            db.commit()
            db.refresh(match)
        
        return {"status": match.status}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_trade_match_status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/purchase-offers/{offer_id}/status")
async def get_purchase_offer_status(offer_id: int, request: Request, db: Session = Depends(get_db)):
    """Get the status of a purchase offer"""
    try:
        user_id = check_session_cookie(request)
        
        # Get the purchase offer
        purchase_offer = db.query(PurchaseOffer).filter(PurchaseOffer.ID == offer_id).first()
        
        if not purchase_offer:
            raise HTTPException(status_code=404, detail="Purchase offer not found")
        
        # Verify that the current user is part of this offer
        if not check_user_in_offer(user_id, purchase_offer, "purchase"):
            raise HTTPException(status_code=403, detail="Not authorized to view this purchase")
        
        return {"status": purchase_offer.status}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_purchase_offer_status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/trade-offers/{offer_id}/status")
async def update_trade_status(
    offer_id: int, 
    status_data: Dict[str, str], 
    request: Request, 
    db: Session = Depends(get_db)
):
    """Update the status of a trade match"""
    try:
        user_id = check_session_cookie(request)
        
        # Get the trade offer
        trade_offer = db.query(TradeOffer).filter(TradeOffer.ID == offer_id).first()
        
        if not trade_offer:
            raise HTTPException(status_code=404, detail="Trade offer not found")
        
        # Verify that the current user is part of this offer
        if not check_user_in_offer(user_id, trade_offer, "trade"):
            raise HTTPException(status_code=403, detail="Not authorized to update this trade")
        
        # Validate status
        new_status = status_data.get("status")
        if new_status not in ["active", "completed", "cancelled"]:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        # Get the match
        match = db.query(Match).filter(Match.offer_id == offer_id).first()
        
        if not match:
            # If no match exists yet, create one
            match = Match(offer_id=offer_id, status=new_status)
            db.add(match)
        else:
            # Update existing match
            match.status = new_status
        
        db.commit()
        db.refresh(match)
        
        return {"message": f"Trade status updated to {new_status}", "status": match.status}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_trade_status: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/purchase-offers/{offer_id}/status")
async def update_purchase_status(
    offer_id: int, 
    status_data: Dict[str, str], 
    request: Request, 
    db: Session = Depends(get_db)
):
    """Update the status of a purchase offer"""
    try:
        user_id = check_session_cookie(request)
        
        # Get the purchase offer
        purchase_offer = db.query(PurchaseOffer).filter(PurchaseOffer.ID == offer_id).first()
        
        if not purchase_offer:
            raise HTTPException(status_code=404, detail="Purchase offer not found")
        
        # Verify that the current user is part of this offer
        if not check_user_in_offer(user_id, purchase_offer, "purchase"):
            raise HTTPException(status_code=403, detail="Not authorized to update this purchase")
        
        # Validate status - purchase offers have different status options
        new_status = status_data.get("status")
        if new_status not in ["idle", "active", "completed", "cancelled"]:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        # Update purchase offer status
        purchase_offer.status = new_status
        
        # Handle item availability based on status
        if new_status == "completed":
            # Complete the purchase - transfer ownership
            item = db.query(Item).filter(Item.ID == purchase_offer.item_id).first()
            if item:
                item.userID = purchase_offer.buyer_id
                item.is_available = False
        elif new_status == "cancelled":
            # Cancel the purchase - make item available again
            item = db.query(Item).filter(Item.ID == purchase_offer.item_id).first()
            if item:
                item.is_available = True
        
        db.commit()
        db.refresh(purchase_offer)
        
        return {"message": f"Purchase status updated to {new_status}", "status": purchase_offer.status}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_purchase_status: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))