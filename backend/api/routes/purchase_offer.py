from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List
from datetime import datetime, timedelta
from enum import Enum

from app.db_setup import get_db
from app.getUserID import check_session_cookie
from app.zodb_setup import get_root, commit_changes
from api.models.TradeOffers import (
    PurchaseOffer, 
    Item, 
    User
)

# Logging setup (replace with your preferred logging mechanism)
import logging
logger = logging.getLogger(__name__)

# Purchase Offer Status Enum
class PurchaseOfferStatus(str, Enum):
    IDLE = "idle"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

router = APIRouter(tags=["Purchase Offers"])

@router.post("/purchase-offers/create")
async def create_purchase_offer(
    request: Request, 
    purchase_data: dict, 
    db: Session = Depends(get_db)
):
    """
    Create a new purchase offer for an item
    
    Workflow:
    1. Validate item existence and availability
    2. Check for existing active offers
    3. Create purchase offer
    4. Mark item as unavailable
    """
    try:
        # Get current user ID
        user_id = check_session_cookie(request)
        
        # Extract item ID from request
        item_id = purchase_data.get("item_id")
        if not item_id:
            raise HTTPException(status_code=400, detail="Item ID is required")
        
        # Fetch item details
        item = db.query(Item).filter(Item.ID == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Prevent purchasing own item
        if item.userID == user_id:
            raise HTTPException(status_code=400, detail="You cannot purchase your own item")
        
        # Check item availability and purchasability
        if not item.is_available:
            raise HTTPException(status_code=400, detail="Item is no longer available")
        
        if not item.is_purchasable:
            raise HTTPException(status_code=400, detail="Item is not available for purchase")
        
        # Check for existing active offers
        existing_offer = db.query(PurchaseOffer).filter(
            PurchaseOffer.item_id == item_id,
            PurchaseOffer.status.in_([
                PurchaseOfferStatus.IDLE, 
                PurchaseOfferStatus.ACTIVE
            ])
        ).first()
        
        if existing_offer:
            raise HTTPException(
                status_code=400, 
                detail="Item already has an active purchase offer"
            )
        
        # Get seller (current item owner)
        seller = db.query(User).filter(User.ID == item.userID).first()
        if not seller:
            raise HTTPException(status_code=404, detail="Seller not found")
        
        # Create purchase offer
        purchase_offer = PurchaseOffer(
            buyer_id=user_id,
            seller_id=seller.ID,
            item_id=item_id,
            status=PurchaseOfferStatus.ACTIVE,
            created_at=datetime.utcnow()
        )
        
        # Mark item as unavailable
        item.is_available = False
        
        # Save to database
        db.add(purchase_offer)
        db.commit()
        db.refresh(purchase_offer)
        
        # Fetch item details from ZODB
        root = get_root()
        zodb_item = root.get("trade_items", {}).get(item.zodb_id)
        
        # Log the event
        logger.info(f"Purchase offer created: ID {purchase_offer.ID}, Item {item_id}")
        
        return {
            "message": "Purchase offer created successfully",
            "offer_id": purchase_offer.ID,
            "status": purchase_offer.status,
            "item_details": {
                "id": item.ID,
                "name": zodb_item.name if zodb_item else "Unknown Item",
                "price": zodb_item.price if zodb_item else None
            }
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error in create_purchase_offer: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/purchase-offers/{offer_id}/complete")
async def complete_purchase_offer(
    offer_id: int, 
    request: Request, 
    db: Session = Depends(get_db)
):
    """
    Complete a purchase offer
    
    Workflow:
    1. Validate offer existence
    2. Check user permissions
    3. Transfer item ownership
    4. Update offer status
    """
    try:
        # Get current user ID
        user_id = check_session_cookie(request)
        
        # Fetch purchase offer
        purchase_offer = db.query(PurchaseOffer).filter(
            PurchaseOffer.ID == offer_id,
            PurchaseOffer.status == PurchaseOfferStatus.ACTIVE
        ).first()
        
        if not purchase_offer:
            raise HTTPException(status_code=404, detail="Active purchase offer not found")
        
        # Verify user permission (buyer or seller can complete)
        if user_id not in [purchase_offer.buyer_id, purchase_offer.seller_id]:
            raise HTTPException(
                status_code=403, 
                detail="You don't have permission to complete this purchase"
            )
        
        # Fetch the item
        item = db.query(Item).filter(Item.ID == purchase_offer.item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Transfer ownership
        item.userID = purchase_offer.buyer_id
        item.is_available = False  # Mark as sold
        
        # Update purchase offer status
        purchase_offer.status = PurchaseOfferStatus.COMPLETED
        
        # Commit changes
        db.commit()
        
        # Fetch item details from ZODB for logging
        root = get_root()
        zodb_item = root.get("trade_items", {}).get(item.zodb_id)
        
        # Log the event
        logger.info(f"Purchase offer completed: ID {offer_id}, Item {item.ID}")
        
        return {
            "message": "Purchase completed successfully",
            "offer_id": offer_id,
            "item_id": item.ID,
            "new_owner_id": purchase_offer.buyer_id
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error in complete_purchase_offer: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/purchase-offers/{offer_id}/cancel")
async def cancel_purchase_offer(
    offer_id: int, 
    request: Request, 
    db: Session = Depends(get_db)
):
    """
    Cancel an active purchase offer
    
    Workflow:
    1. Validate offer existence
    2. Check user permissions
    3. Restore item availability
    4. Update offer status
    """
    try:
        # Get current user ID
        user_id = check_session_cookie(request)
        
        # Fetch purchase offer
        purchase_offer = db.query(PurchaseOffer).filter(
            PurchaseOffer.ID == offer_id,
            PurchaseOffer.status == PurchaseOfferStatus.ACTIVE
        ).first()
        
        if not purchase_offer:
            raise HTTPException(status_code=404, detail="Active purchase offer not found")
        
        # Verify user permission (buyer or seller can cancel)
        if user_id not in [purchase_offer.buyer_id, purchase_offer.seller_id]:
            raise HTTPException(
                status_code=403, 
                detail="You don't have permission to cancel this purchase"
            )
        
        # Fetch the item
        item = db.query(Item).filter(Item.ID == purchase_offer.item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Restore item availability
        item.is_available = True
        
        # Update purchase offer status
        purchase_offer.status = PurchaseOfferStatus.CANCELLED
        
        # Commit changes
        db.commit()
        
        # Fetch item details from ZODB for logging
        root = get_root()
        zodb_item = root.get("trade_items", {}).get(item.zodb_id)
        
        # Log the event
        logger.info(f"Purchase offer cancelled: ID {offer_id}, Item {item.ID}")
        
        return {
            "message": "Purchase offer cancelled successfully",
            "offer_id": offer_id,
            "item_id": item.ID
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error in cancel_purchase_offer: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/purchase-offers/check-item/{item_id}")
async def check_item_purchase_status(
    item_id: int, 
    request: Request, 
    db: Session = Depends(get_db)
):
    """
    Check the purchase status of a specific item
    
    Returns:
    - Availability status
    - Active offer details if exists
    """
    try:
        # Get current user ID
        user_id = check_session_cookie(request)
        
        # Fetch the item
        item = db.query(Item).filter(Item.ID == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Check for active purchase offers
        active_offer = db.query(PurchaseOffer).filter(
            PurchaseOffer.item_id == item_id,
            PurchaseOffer.status.in_([
                PurchaseOfferStatus.IDLE, 
                PurchaseOfferStatus.ACTIVE
            ])
        ).first()
        
        # Fetch item details from ZODB
        root = get_root()
        zodb_item = root.get("trade_items", {}).get(item.zodb_id)
        
        # Prepare response
        if active_offer:
            return {
                "available": False,
                "has_active_offer": True,
                "offer_id": active_offer.ID,
                "offer_status": active_offer.status,
                "buyer_id": active_offer.buyer_id,
                "seller_id": active_offer.seller_id,
                "is_current_user_buyer": active_offer.buyer_id == user_id,
                "is_current_user_seller": active_offer.seller_id == user_id,
                "item_details": {
                    "name": zodb_item.name if zodb_item else "Unknown Item",
                    "price": zodb_item.price if zodb_item else None
                }
            }
        
        return {
            "available": item.is_available and item.is_purchasable,
            "has_active_offer": False,
            "item_details": {
                "name": zodb_item.name if zodb_item else "Unknown Item",
                "price": zodb_item.price if zodb_item else None
            }
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error in check_item_purchase_status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/purchase-offers/my-offers")
async def get_my_purchase_offers(
    request: Request, 
    status: Optional[PurchaseOfferStatus] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve purchase offers for the current user
    
    Allows filtering by status
    """
    try:
        # Get current user ID
        user_id = check_session_cookie(request)
        
        # Build query
        query = db.query(PurchaseOffer).filter(
            (PurchaseOffer.buyer_id == user_id) | (PurchaseOffer.seller_id == user_id)
        )
        
        # Optional status filtering
        if status:
            query = query.filter(PurchaseOffer.status == status)
        
        # Execute query
        purchase_offers = query.all()
        
        # Fetch ZODB details
        root = get_root()
        trade_items = root.get("trade_items", {})
        
        # Prepare response
        offers_details = []
        for offer in purchase_offers:
            # Fetch item and ZODB details
            item = db.query(Item).filter(Item.ID == offer.item_id).first()
            zodb_item = trade_items.get(item.zodb_id) if item else None
            
            # Prepare offer details
            offer_detail = {
                "id": offer.ID,
                "status": offer.status,
                "created_at": offer.created_at.isoformat(),
                "is_buyer": offer.buyer_id == user_id,
                "item_id": offer.item_id,
                "item_details": {
                    "name": zodb_item.name if zodb_item else "Unknown Item",
                    "description": zodb_item.description if zodb_item else "",
                    "price": zodb_item.price if zodb_item else None,
                    "image": zodb_item.image if zodb_item else None
                }
            }
            offers_details.append(offer_detail)
        
        return offers_details
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error in get_my_purchase_offers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")