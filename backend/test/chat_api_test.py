import requests
import json
import time
import mysql.connector
from mysql.connector import Error

# Base URL - change to match your server
BASE_URL = "http://localhost:8000"

# Login credentials for testing
USER1_CREDENTIALS = {"username": "testuser1", "password": "test123"}
USER2_CREDENTIALS = {"username": "testuser2", "password": "test123"}

def get_user_id(username):
    """Get user ID from database by username"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Peam56201",
            database="tno"
        )
        cursor = connection.cursor(dictionary=True)
        query = "SELECT ID FROM users WHERE UserName = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if result:
            return result['ID']
        return None
    except Exception as e:
        print(f"Error getting user ID: {e}")
        return None

def login(credentials):
    """Login and get session cookie"""
    response = requests.post(
        f"{BASE_URL}/login",
        json=credentials
    )
    if response.status_code == 200:
        print(f"Login response: {response.text}")
        return response.cookies.get("session_token")
    else:
        print(f"Login failed: {response.text}")
        return None

def test_chat_api():
    """Test the chat API endpoints"""
    print("\n=== TESTING CHAT API ===\n")
    
    # Get user IDs
    user1_id = get_user_id("testuser1")
    user2_id = get_user_id("testuser2")
    
    print(f"User IDs: testuser1={user1_id}, testuser2={user2_id}")
    
    # Use the known offer ID from your database query
    offer_id = 2
    
    # Step 1: Login as first user
    print("1. Logging in as User 1...")
    session1 = login(USER1_CREDENTIALS)
    if not session1:
        print("❌ Test failed: User 1 login failed")
        return
    print(f"✅ User 1 logged in successfully, session token: {session1}")
    
    # Step 2: Login as second user
    print("\n2. Logging in as User 2...")
    session2 = login(USER2_CREDENTIALS)
    if not session2:
        print("❌ Test failed: User 2 login failed")
        return
    print(f"✅ User 2 logged in successfully, session token: {session2}")
    
    # Step 3: Get accepted offers for User 1
    print("\n3. Getting accepted offers for User 1...")
    cookies1 = {"session_token": session1}
    response = requests.get(
        f"{BASE_URL}/chat/accepted-offers",
        cookies=cookies1
    )
    
    if response.status_code != 200:
        print(f"❌ Test failed: Could not get accepted offers. Status: {response.status_code}")
        print(response.text)
        return
    
    offers = response.json()
    print(f"✅ Found {len(offers)} accepted offers for User 1")
    for offer in offers:
        print(f"  - Offer ID: {offer.get('offer_id')}, Other User: {offer.get('other_user_name')}")
    
    # Step 4: Create a chat room for the offer
    print(f"\n4. Creating chat room for offer {offer_id}...")
    response = requests.post(
        f"{BASE_URL}/chat/create-chat-room/{offer_id}",
        cookies=cookies1
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    
    if response.status_code != 200:
        print(f"❌ Test failed: Could not create chat room. Status: {response.status_code}")
        print(response.text)
    else:
        print("✅ Chat room created successfully")
    
    # Step 5: Send a test message as User 1
    print("\n5. Sending test message as User 1...")
    message_data = {"message": f"Test message from User 1 at {time.time()}"}
    response = requests.post(
        f"{BASE_URL}/chat/send-message/{offer_id}",
        json=message_data,
        cookies=cookies1
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    
    if response.status_code != 200:
        print(f"❌ Test failed: Could not send message. Status: {response.status_code}")
        print(response.text)
    else:
        message_info = response.json()
        print(f"✅ Message sent successfully: {message_info['data']['content']}")
    
    # Step 6: Get messages as User 2
    print("\n6. Getting messages as User 2...")
    cookies2 = {"session_token": session2}
    response = requests.get(
        f"{BASE_URL}/chat/messages/{offer_id}",
        cookies=cookies2
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {response.headers}")
    
    if response.status_code != 200:
        print(f"❌ Test failed: Could not get messages. Status: {response.status_code}")
        print(response.text)
    else:
        messages = response.json()["messages"]
        print(f"✅ Retrieved {len(messages)} messages")
        
        # Print the last message
        if messages:
            print(f"ℹ️ Last message: {messages[-1]['content']} (From user: {messages[-1]['user_id']})")
    
    # The rest of the test steps...
    print("\n=== CHAT API TEST COMPLETED ===")

if __name__ == "__main__":
    test_chat_api()