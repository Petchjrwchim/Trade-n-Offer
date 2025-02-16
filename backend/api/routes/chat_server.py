from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import mysql.connector

# Create the router instance
router = APIRouter()

# WebSocket connection storage (for demonstration purposes)
active_connections = []

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Change if needed
        password="",  # Change if needed
        database="tno"
    )

# WebSocket endpoint for chat
@router.websocket("/ws/chat/{username}")
async def websocket_chat(websocket: WebSocket, username: str):
    await websocket.accept()

    # Get the user ID based on the username
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id FROM userpass WHERE UserName = %s", (username,))
    user = cursor.fetchone()

    if user is None:
        await websocket.close(code=1003)  # Close the connection if user doesn't exist
        return

    user_id = user['id']
    cursor.close()
    conn.close()

    # Fetch chat history from the database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM chat_messages ORDER BY timestamp ASC")
    chat_history = cursor.fetchall()
    cursor.close()
    conn.close()

    # Send chat history to the user upon connection
    for message in chat_history:
        # Get the sender's username
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT UserName FROM userpass WHERE id = %s", (message['user_id'],))
        sender = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if sender:
            await websocket.send_text(f"{sender['UserName']}: {message['message']}")

    # Add the connection to the active connections list
    active_connections.append(websocket)

    try:
        while True:
            # Receive message from client
            message = await websocket.receive_text()
            print(f"Message from {username}: {message}")  # Check the message and username

            # Save message to the database with the user_id
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO chat_messages (user_id, message) VALUES (%s, %s)", (user_id, message))
            conn.commit()
            cursor.close()
            conn.close()

            # Broadcast the message to all connected clients
            for connection in active_connections:
                await connection.send_text(f"{username}: {message}")

    except WebSocketDisconnect:
        print(f"User {username} disconnected")
        active_connections.remove(websocket)  # Remove the connection from active connections list

    finally:
        # Ensure the connection is removed
        active_connections.remove(websocket)
        await websocket.close()



# Chat history retrieval (optional, to fetch old messages)
@router.get("/chat_history/{username}")
async def get_chat_history(username: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM chat ORDER BY timestamp ASC")
    chat_history = cursor.fetchall()

    cursor.close()
    conn.close()

    return {"messages": chat_history}

