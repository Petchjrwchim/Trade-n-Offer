import firebase_admin
from firebase_admin import credentials, db, storage
import json
import os
import time
import base64
import uuid
from typing import Dict, List, Any, Optional

# Import Firebase configuration
try:
    from .firebase_config import FIREBASE_CONFIG, SERVICE_ACCOUNT_PATH, SERVICE_ACCOUNT_EXISTS
except ImportError:
    # Fallback configuration if import fails
    SERVICE_ACCOUNT_PATH = None
    SERVICE_ACCOUNT_EXISTS = False
    FIREBASE_CONFIG = {
        "apiKey": "AIzaSyDx43F34QRLQss07udVOf7wfURDaVIZ9EY",
        "authDomain": "tnof-98bb3.firebaseapp.com",
        "databaseURL": "https://tnof-98bb3-default-rtdb.asia-southeast1.firebasedatabase.app",
        "projectId": "tnof-98bb3",
        "storageBucket": "tnof-98bb3.firebasestorage.app",
        "messagingSenderId": "770087345899",
        "appId": "1:770087345899:web:3c7759b395c57ea8a4a8ae"
    }
    print("Warning: Firebase config import failed. Using fallback values.")

# Firebase initialization flag
_is_initialized = False

# Get the correct path to the service account file
SERVICE_ACCOUNT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "firebase-service-account.json")

def initialize_firebase():
    """Initialize Firebase Admin SDK if not already initialized"""
    global _is_initialized
    
    # Skip initialization if already done
    if _is_initialized:
        return
        
    try:
        # Check if Firebase app is already initialized
        firebase_admin.get_app()
        print("Firebase already initialized")
        _is_initialized = True
    except ValueError:
        # If not, initialize with service account credentials
        print(f"Initializing Firebase with service account: {SERVICE_ACCOUNT_PATH}")
        try:
            cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://tnof-98bb3-default-rtdb.asia-southeast1.firebasedatabase.app',
                'storageBucket': 'tnof-98bb3.firebasestorage.app'
            })
            print("Firebase initialization successful")
            _is_initialized = True
        except Exception as e:
            print(f"Firebase initialization failed: {e}")
            raise

def get_chat_reference(offer_id: int, chat_type: str = "trade"):
    """Get a reference to a chat in Firebase"""
    initialize_firebase()
    if chat_type == "purchase":
        return db.reference(f"/purchase_chats/{offer_id}")
    else:
        return db.reference(f"/chats/{offer_id}")

def get_messages_reference(offer_id: int):
    """Get a reference to messages in a chat"""
    initialize_firebase()
    return db.reference(f"/chats/{offer_id}/messages")

def get_storage_bucket():
    """Get a reference to Firebase Storage bucket"""
    initialize_firebase()
    try:
        bucket = storage.bucket()
        print(f"Storage bucket name: {bucket.name}")
        return bucket
    except Exception as e:
        print(f"Error getting storage bucket: {e}")
        raise

def create_chat_room(offer_id: int, sender_id: int, receiver_id: int, chat_type: str = "trade") -> bool:
    try:
        initialize_firebase()
        chat_ref = get_chat_reference(offer_id)
        
        # Check if the chat room already exists
        if chat_ref.get() is None:
            # Create a new chat room
            chat_ref.set({
                "offer_id": offer_id,
                "chat_type": chat_type,  # Store the chat type
                "participants": [sender_id, receiver_id],
                "created_at": int(time.time() * 1000),
                "messages": {},
                "last_read": {
                    str(sender_id): 0,
                    str(receiver_id): 0
                }
            })
            
            print(f"Created new {chat_type} chat room for offer {offer_id}")
        else:
            print(f"Chat room for offer {offer_id} already exists")
            
        return True
    except Exception as e:
        print(f"Error creating chat room: {e}")
        return False
    
def upload_image(offer_id: int, user_id: int, image_data: str) -> Optional[str]:
    """Upload image to Firebase Storage"""
    try:
        print(f"Starting image upload for offer {offer_id}, user {user_id}")
        
        if not image_data:
            print("Error: No image data provided")
            return None
            
        print(f"Image data length: {len(image_data)}")
        
        # Ensure we have a valid base64 string
        if "base64," in image_data:
            parts = image_data.split("base64,")
            if len(parts) < 2:
                print("Error: Invalid base64 data format")
                return None
            image_data = parts[1]
            print("Extracted base64 data from data URL")
        
        # Decode the base64 image
        try:
            image_bytes = base64.b64decode(image_data)
            print(f"Successfully decoded image, size: {len(image_bytes)} bytes")
        except Exception as e:
            print(f"Failed to decode base64 image: {str(e)}")
            return None
        
        # Generate unique filename
        filename = f"chat_images/{offer_id}/{user_id}_{uuid.uuid4()}.jpg"
        print(f"Generated filename: {filename}")
        
        # Get storage bucket
        bucket = get_storage_bucket()
        
        # Upload image
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type="image/jpeg")
        print("Successfully uploaded image to Firebase Storage")
        
        # Make the image publicly accessible
        blob.make_public()
        print(f"Image is now public at: {blob.public_url}")

        image_url = blob.public_url
        print(f"Made image public, URL: {image_url}")
        
        # Verify the URL was actually obtained
        if not image_url:
            print("Error: Failed to get public URL after upload")
            return None
            
        return image_url
    except Exception as e:
        print(f"Error in upload_image: {str(e)}")
        return None
    
def send_message(offer_id: int, user_id: int, message: str, image_data: str = None, chat_type: str = "trade") -> Optional[str]:
    try:
        print(f"Sending message to {chat_type} chat {offer_id} from user {user_id}")
        initialize_firebase()
        messages_ref = get_messages_reference(offer_id)
        
        # Prepare message data
        message_data = {
            "user_id": user_id,
            "content": message,
            "timestamp": int(time.time() * 1000),  # Current timestamp in milliseconds
            "read": False,
            "has_image": False,  # Default to false
            "chat_type": chat_type  # Include chat type in message
        }
        
        # Handle image if provided
        if image_data:
            print(f"Image data received for message, length: {len(image_data)}")
            
            # Upload image - only once!
            try:
                # Upload to Firebase Storage and get URL
                image_url = upload_image(offer_id, user_id, image_data)
                
                if image_url:
                    # Only set has_image to true if we actually have a URL
                    message_data["image_url"] = image_url
                    message_data["has_image"] = True
                    print("Added image_url to message data:", image_url)
                else:
                    print("WARNING: Image upload failed - no URL returned")
            except Exception as e:
                print(f"Error uploading image: {e}")
        
        # Push the new message
        new_message_ref = messages_ref.push()
        new_message_ref.set(message_data)
        print(f"New message created with ID: {new_message_ref.key}")
        
        # Update the chat's last message
        chat_ref = get_chat_reference(offer_id)
        preview_content = message
        
        # If there's an image but no text, set preview to "[Image]"
        if message_data["has_image"] and not message.strip():
            preview_content = "[Image]"
        
        # Truncate preview if necessary
        if len(preview_content) > 50:
            preview_content = preview_content[:47] + "..."
        
        # Include the same image URL in the last_message data
        last_message_data = {
            "content": preview_content,
            "timestamp": message_data["timestamp"],
            "sender_id": user_id,
            "has_image": message_data["has_image"]
        }
        
        if "image_url" in message_data:
            last_message_data["image_url"] = message_data["image_url"]
            
        chat_ref.child("last_message").set(last_message_data)
        print(f"Updated last message preview: '{preview_content}', has_image: {message_data['has_image']}")
        
        # Mark as read for the sender
        mark_messages_as_read(offer_id, user_id)
        
        # Return the new message with complete data for client-side use
        return new_message_ref.key
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

def get_messages(offer_id: int) -> List[Dict[str, Any]]:
    """Get all messages for a chat room
    
    Args:
        offer_id: The ID of the trade offer / chat room
        
    Returns:
        List[Dict[str, Any]]: List of messages, sorted by timestamp
    """
    try:
        initialize_firebase()
        messages_ref = get_messages_reference(offer_id)
        messages_data = messages_ref.get()
        
        if not messages_data:
            return []
        
        # Convert the messages from a dict to a list
        messages_list = []
        for key, data in messages_data.items():
            message_item = {
                "id": key,
                **data
            }
            
            # Ensure the has_image flag and image_url are correctly set
            if message_item.get("has_image", False) and "image_url" not in message_item:
                print(f"Warning: Message {key} has has_image=True but missing image_url")
            
            messages_list.append(message_item)
        
        # Sort by timestamp
        messages_list.sort(key=lambda x: x.get("timestamp", 0))
        
        return messages_list
    except Exception as e:
        print(f"Error getting messages: {e}")
        return []

def get_user_chat_rooms(user_id: int) -> List[Dict[str, Any]]:
    """Get all chat rooms where the user is a participant
    
    Args:
        user_id: The ID of the user
        
    Returns:
        List[Dict[str, Any]]: List of chat rooms
    """
    try:
        initialize_firebase()
        chats_ref = db.reference("/chats")
        chats_data = chats_ref.get()
        
        if not chats_data:
            return []
        
        # Filter chats where user is a participant
        user_chats = []
        for chat_id, chat_data in chats_data.items():
            participants = chat_data.get("participants", [])
            
            if user_id in participants:
                # Determine chat type and user's role
                chat_type = chat_data.get("chat_type", "trade")
                is_buyer = False
                is_seller = False
                
                if chat_type == "purchase":
                    # For purchase offers, first participant is usually buyer, second is seller
                    # This assumes your participants list has buyer at index 0 and seller at index 1
                    is_buyer = participants[0] == user_id if len(participants) > 0 else False
                    is_seller = participants[1] == user_id if len(participants) > 1 else False
                
                # Get other user info
                other_user_id = None
                for participant_id in participants:
                    if participant_id != user_id:
                        other_user_id = participant_id
                        break
                
                # Add the chat ID to the data along with role information
                user_chats.append({
                    "id": chat_id,
                    "offer_id": chat_data.get("offer_id"),
                    "offer_type": chat_type,  # Include chat type as offer_type for frontend consistency
                    "is_buyer": is_buyer,
                    "is_seller": is_seller,
                    "other_user_id": other_user_id,
                    "last_message": chat_data.get("last_message", {}),
                    "unread_count": get_unread_message_count(int(chat_id), user_id),
                    "created_at": chat_data.get("created_at"),
                    **chat_data
                })
        
        # Sort by last message timestamp, if available
        user_chats.sort(
            key=lambda x: x.get("last_message", {}).get("timestamp", 0),
            reverse=True
        )
        
        return user_chats
    except Exception as e:
        print(f"Error getting user chat rooms: {e}")
        return []

def get_unread_message_count(offer_id: int, user_id: int) -> int:
    """Get the number of unread messages for a user in a chat room
    
    Args:
        offer_id: The ID of the trade offer / chat room
        user_id: The ID of the user
        
    Returns:
        int: Number of unread messages
    """
    try:
        initialize_firebase()
        chat_ref = get_chat_reference(offer_id)
        
        # Get last read timestamp for the user
        last_read_ref = chat_ref.child(f"last_read/{user_id}")
        last_read_timestamp = last_read_ref.get() or 0
        
        # Get all messages
        messages = get_messages(offer_id)
        
        # Count messages from other users after the last read timestamp
        unread_count = 0
        for message in messages:
            if (message.get("user_id") != user_id and 
                message.get("timestamp", 0) > last_read_timestamp):
                unread_count += 1
        
        return unread_count
    except Exception as e:
        print(f"Error getting unread message count: {e}")
        return 0

def mark_messages_as_read(offer_id: int, user_id: int) -> bool:
    """Mark all messages in a chat room as read for a user
    
    Args:
        offer_id: The ID of the trade offer / chat room
        user_id: The ID of the user
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        initialize_firebase()
        chat_ref = get_chat_reference(offer_id)
        
        # Update the last read timestamp for the user
        chat_ref.child(f"last_read/{user_id}").set(int(time.time() * 1000))
        
        return True
    except Exception as e:
        print(f"Error marking messages as read: {e}")
        return False

def delete_chat_room(offer_id: int) -> bool:
    """Delete a chat room
    
    Args:
        offer_id: The ID of the trade offer / chat room
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        initialize_firebase()
        chat_ref = get_chat_reference(offer_id)
        
        # Delete the chat room
        chat_ref.delete()
        
        return True
    except Exception as e:
        print(f"Error deleting chat room: {e}")
        return False

def get_total_unread_messages(user_id: int) -> int:
    """Get the total number of unread messages across all chat rooms for a user
    
    Args:
        user_id: The ID of the user
        
    Returns:
        int: Total number of unread messages
    """
    try:
        initialize_firebase()
        
        # Get all user chat rooms
        user_chats = get_user_chat_rooms(user_id)
        
        # Sum unread messages across all chats
        total_unread = 0
        for chat in user_chats:
            chat_id = chat.get("id")
            if chat_id:
                total_unread += get_unread_message_count(int(chat_id), user_id)
        
        return total_unread
    except Exception as e:
        print(f"Error getting total unread messages: {e}")
        return 0

def update_chat_metadata(offer_id: int, metadata: Dict[str, Any]) -> bool:
    """Update metadata for a chat room
    
    Args:
        offer_id: The ID of the trade offer / chat room
        metadata: The metadata to update
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        initialize_firebase()
        chat_ref = get_chat_reference(offer_id)
        
        # Update the metadata
        for key, value in metadata.items():
            # Don't overwrite messages or participants
            if key not in ["messages", "participants"]:
                chat_ref.child(key).set(value)
        
        return True
    except Exception as e:
        print(f"Error updating chat metadata: {e}")
        return False