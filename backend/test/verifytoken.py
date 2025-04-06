import requests
import mysql.connector
from mysql.connector import Error

# Base URL - change to match your server
BASE_URL = "http://localhost:8000"

def get_db_connection():
    """Connect to the database"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Peam56201",
            database="tno"
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def get_user_by_id(user_id):
    """Get user details from database by ID"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE ID = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result
    except Error as e:
        print(f"Error querying database: {e}")
        return None

def get_user_by_name(username):
    """Get user details from database by username"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE UserName = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result
    except Error as e:
        print(f"Error querying database: {e}")
        return None

def login_and_verify_session():
    """Login and verify that the session token matches a user ID"""
    print("\n=== VERIFYING SESSION TOKEN ===\n")
    
    # Test user credentials
    username = "testuser1"
    credentials = {"username": username, "password": "test123"}
    
    # Step 1: Get user ID from database
    user = get_user_by_name(username)
    if not user:
        print(f"❌ User '{username}' not found in database")
        return
    
    user_id = user["ID"]
    print(f"✅ Found user in database: ID={user_id}, UserName={user['UserName']}")
    
    # Step 2: Login to get session token
    print("\nLogging in...")
    response = requests.post(
        f"{BASE_URL}/login",
        json=credentials
    )
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return
    
    session_token = response.cookies.get("session_token")
    if not session_token:
        print("❌ No session token in response")
        return
    
    print(f"✅ Login successful, received session token: {session_token}")
    
    # Step 3: Verify if session token matches user ID
    if str(session_token) == str(user_id):
        print("✅ Session token MATCHES user ID!")
    else:
        print(f"❌ Session token ({session_token}) DOES NOT MATCH user ID ({user_id})")
        # Try to find which user this token corresponds to
        token_user = get_user_by_id(session_token)
        if token_user:
            print(f"ℹ️ Session token corresponds to user: ID={token_user['ID']}, UserName={token_user['UserName']}")
        else:
            print("ℹ️ Session token does not correspond to any user in the database")
    
    # Step 4: Check session with API
    print("\nChecking session via API...")
    response = requests.get(
        f"{BASE_URL}/check-session",
        cookies={"session_token": session_token}
    )
    
    print(f"Status code: {response.status_code}")
    print(f"Response body: {response.text}")
    
    print("\n=== SESSION VERIFICATION COMPLETED ===")

if __name__ == "__main__":
    login_and_verify_session()