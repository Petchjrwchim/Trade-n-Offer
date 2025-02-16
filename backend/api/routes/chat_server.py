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
    active_connections.append(websocket)  # Add the connection to the active connections list

    try:
        while True:
            # Receive message from client
            message = await websocket.receive_text()
            print(f"Message from {username}: {message}")

            # Save message to the database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO chat (sender_id, message) VALUES (%s, %s)", (username, message))
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
