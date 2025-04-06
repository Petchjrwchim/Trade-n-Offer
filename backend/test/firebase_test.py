"""
Firebase connection test script.
Run this to verify your Firebase configuration is working correctly.
"""

import sys
import os
import time
import json

# Add the parent directory to the Python path so 'api' module can be found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import the Firebase service
from api.services.firebase_service import (
    initialize_firebase, create_chat_room, 
    send_message, get_messages, delete_chat_room
)

def test_firebase_connection():
    """Test the Firebase connection and basic operations"""
    print("\n=== TESTING FIREBASE CONNECTION ===\n")
    
    try:
        # Step 1: Initialize Firebase
        print("1. Initializing Firebase...")
        initialize_firebase()
        print("✅ Firebase initialized successfully")
        
        # Step 2: Create a test chat room
        test_chat_id = int(time.time())  # Use timestamp as a unique ID
        print(f"\n2. Creating test chat room with ID: {test_chat_id}...")
        result = create_chat_room(test_chat_id, 999, 888)  # Test user IDs
        
        if result:
            print("✅ Test chat room created successfully")
        else:
            print("❌ Failed to create test chat room")
            return
        
        # Step 3: Send a test message
        print("\n3. Sending a test message...")
        message_content = f"Test message at {time.time()}"
        message_id = send_message(test_chat_id, 999, message_content)
        
        if message_id:
            print(f"✅ Test message sent successfully with ID: {message_id}")
        else:
            print("❌ Failed to send test message")
            return
        
        # Step 4: Get messages from the chat room
        print("\n4. Getting messages from the test chat room...")
        messages = get_messages(test_chat_id)
        
        if messages:
            print(f"✅ Retrieved {len(messages)} messages")
            print("ℹ️ Last message:")
            print(json.dumps(messages[-1], indent=2))
        else:
            print("❌ No messages found or failed to retrieve messages")
            return
        
        # Step 5: Clean up - delete the test chat room
        print("\n5. Cleaning up - deleting test chat room...")
        result = delete_chat_room(test_chat_id)
        
        if result:
            print("✅ Test chat room deleted successfully")
        else:
            print("❌ Failed to delete test chat room")
        
        print("\n=== FIREBASE CONNECTION TEST COMPLETED SUCCESSFULLY ===")
        return True
    
    except Exception as e:
        print(f"❌ Error during Firebase test: {str(e)}")
        return False

if __name__ == "__main__":
    test_firebase_connection()