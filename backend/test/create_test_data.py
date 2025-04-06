"""
Script to create test data for the chat system.
This creates users, items, and trade offers, then accepts some offers.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.models.TradeOffers import Base, User, Item, TradeOffer
from app.db_setup import get_db
import random
import time
from api.services.firebase_service import create_chat_room

# Database connection
engine = create_engine("mysql+mysqlconnector://root:Peam56201@localhost/tno")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_test_users():
    """Create test users if they don't exist"""
    db = SessionLocal()
    
    # Check if test users already exist
    existing_users = db.query(User).filter(User.UserName.in_(["testuser1", "testuser2", "testuser3"])).all()
    existing_usernames = [user.UserName for user in existing_users]
    
    # Create users that don't exist
    new_users = []
    
    if "testuser1" not in existing_usernames:
        user1 = User(UserName="testuser1", UserPass="test123")
        db.add(user1)
        new_users.append(user1)
        print("Created test user 1")
    
    if "testuser2" not in existing_usernames:
        user2 = User(UserName="testuser2", UserPass="test123")
        db.add(user2)
        new_users.append(user2)
        print("Created test user 2")
    
    if "testuser3" not in existing_usernames:
        user3 = User(UserName="testuser3", UserPass="test123")
        db.add(user3)
        new_users.append(user3)
        print("Created test user 3")
    
    db.commit()
    
    # Get all test users (including newly created ones)
    test_users = db.query(User).filter(User.UserName.in_(["testuser1", "testuser2", "testuser3"])).all()
    
    db.close()
    return test_users

def create_test_items(users):
    """Create test items for users"""
    db = SessionLocal()
    
    items = []
    zodb_id_counter = 1000  # Start with a high number to avoid conflicts
    
    # Create 2 items for each user
    for user in users:
        # Check if user already has items
        existing_items = db.query(Item).filter(Item.userID == user.ID).all()
        
        # Only create items if user has less than 2
        if len(existing_items) < 2:
            items_to_create = 2 - len(existing_items)
            
            for i in range(items_to_create):
                # In a real scenario, you would also create an entry in ZODB
                # Here we just use a fake zodb_id
                zodb_id_counter += 1
                
                item = Item(
                    userID=user.ID,
                    zodb_id=zodb_id_counter,
                    is_purchasable=random.choice([True, False]),
                    is_available=True
                )
                db.add(item)
                items.append(item)
                print(f"Created test item for user {user.UserName}")
    
    db.commit()
    
    # Get all items for the test users
    all_items = db.query(Item).filter(Item.userID.in_([user.ID for user in users])).all()
    
    db.close()
    return all_items

def create_test_offers(users, items):
    """Create test trade offers between users"""
    db = SessionLocal()
    
    offers = []
    
    # Group items by user
    user_items = {}
    for item in items:
        if item.userID not in user_items:
            user_items[item.userID] = []
        user_items[item.userID].append(item)
    
    # Create offers between users if they have items
    # User 1 offers to User 2
    if len(users) >= 2 and users[0].ID in user_items and users[1].ID in user_items:
        user1_items = user_items[users[0].ID]
        user2_items = user_items[users[1].ID]
        
        if user1_items and user2_items:
            # Check if offer already exists
            existing_offer = db.query(TradeOffer).filter(
                TradeOffer.sender_id == users[0].ID,
                TradeOffer.receiver_id == users[1].ID
            ).first()
            
            if not existing_offer:
                offer = TradeOffer(
                    sender_id=users[0].ID,
                    receiver_id=users[1].ID,
                    sender_item_id=user1_items[0].ID,
                    receiver_item_id=user2_items[0].ID,
                    status="pending"
                )
                db.add(offer)
                offers.append(offer)
                print(f"Created test offer from {users[0].UserName} to {users[1].UserName}")
    
    # User 2 offers to User 3
    if len(users) >= 3 and users[1].ID in user_items and users[2].ID in user_items:
        user2_items = user_items[users[1].ID]
        user3_items = user_items[users[2].ID]
        
        if len(user2_items) >= 2 and user3_items:  # Make sure User 2 has at least 2 items
            # Check if offer already exists
            existing_offer = db.query(TradeOffer).filter(
                TradeOffer.sender_id == users[1].ID,
                TradeOffer.receiver_id == users[2].ID
            ).first()
            
            if not existing_offer:
                offer = TradeOffer(
                    sender_id=users[1].ID,
                    receiver_id=users[2].ID,
                    sender_item_id=user2_items[1].ID,  # Use second item
                    receiver_item_id=user3_items[0].ID,
                    status="pending"
                )
                db.add(offer)
                offers.append(offer)
                print(f"Created test offer from {users[1].UserName} to {users[2].UserName}")
    
    # User 3 offers to User 1
    if len(users) >= 3 and users[2].ID in user_items and users[0].ID in user_items:
        user3_items = user_items[users[2].ID]
        user1_items = user_items[users[0].ID]
        
        if user3_items and len(user1_items) >= 2:  # Make sure User 1 has at least 2 items
            # Check if offer already exists
            existing_offer = db.query(TradeOffer).filter(
                TradeOffer.sender_id == users[2].ID,
                TradeOffer.receiver_id == users[0].ID
            ).first()
            
            if not existing_offer:
                offer = TradeOffer(
                    sender_id=users[2].ID,
                    receiver_id=users[0].ID,
                    sender_item_id=user3_items[0].ID,
                    receiver_item_id=user1_items[1].ID,  # Use second item
                    status="pending"
                )
                db.add(offer)
                offers.append(offer)
                print(f"Created test offer from {users[2].UserName} to {users[0].UserName}")
    
    db.commit()
    
    # Get all pending offers
    all_offers = db.query(TradeOffer).filter(TradeOffer.status == "pending").all()
    
    db.close()
    return all_offers

def accept_test_offers(offers):
    """Accept some test offers"""
    db = SessionLocal()
    
    accepted_offers = []
    
    # Accept the first offer if there are any
    if offers:
        # Only accept if it's still pending
        offer = db.query(TradeOffer).filter(TradeOffer.ID == offers[0].ID).first()
        
        if offer and offer.status == "pending":
            offer.status = "accepted"
            db.commit()
            accepted_offers.append(offer)
            print(f"Accepted offer ID {offer.ID}")
            
            # Create a chat room for the accepted offer
            create_chat_room(offer.ID, offer.sender_id, offer.receiver_id)
            print(f"Created chat room for offer ID {offer.ID}")
    
    # If there's a second offer, accept it too
    if len(offers) >= 2:
        # Only accept if it's still pending
        offer = db.query(TradeOffer).filter(TradeOffer.ID == offers[1].ID).first()
        
        if offer and offer.status == "pending":
            offer.status = "accepted"
            db.commit()
            accepted_offers.append(offer)
            print(f"Accepted offer ID {offer.ID}")
            
            # Create a chat room for the accepted offer
            create_chat_room(offer.ID, offer.sender_id, offer.receiver_id)
            print(f"Created chat room for offer ID {offer.ID}")
    
    db.close()
    return accepted_offers

def create_all_test_data():
    """Create all test data"""
    print("\n=== CREATING TEST DATA ===\n")
    
    # Create test users
    print("Creating test users...")
    users = create_test_users()
    print(f"Created/found {len(users)} test users")
    
    # Create test items
    print("\nCreating test items...")
    items = create_test_items(users)
    print(f"Total items: {len(items)}")
    
    # Create test offers
    print("\nCreating test offers...")
    offers = create_test_offers(users, items)
    print(f"Total pending offers: {len(offers)}")
    
    # Accept some offers
    print("\nAccepting test offers...")
    accepted_offers = accept_test_offers(offers)
    print(f"Accepted {len(accepted_offers)} offers")
    
    print("\n=== TEST DATA CREATION COMPLETED ===")
    
    # Return test data summary
    return {
        "users": [{"id": user.ID, "username": user.UserName} for user in users],
        "items": [{"id": item.ID, "user_id": item.userID, "zodb_id": item.zodb_id} for item in items],
        "accepted_offers": [
            {
                "id": offer.ID, 
                "sender_id": offer.sender_id, 
                "receiver_id": offer.receiver_id,
                "sender_item_id": offer.sender_item_id, 
                "receiver_item_id": offer.receiver_item_id
            } for offer in accepted_offers
        ]
    }

if __name__ == "__main__":
    test_data = create_all_test_data()
    
    # Print test data for reference
    print("\nTest Users:")
    for user in test_data["users"]:
        print(f"  - ID: {user['id']}, Username: {user['username']}")
    
    print("\nAccepted Offers (use these for testing):")
    for offer in test_data["accepted_offers"]:
        print(f"  - Offer ID: {offer['id']}")
        print(f"    Sender ID: {offer['sender_id']}, Item ID: {offer['sender_item_id']}")
        print(f"    Receiver ID: {offer['receiver_id']}, Item ID: {offer['receiver_item_id']}")
        print("")