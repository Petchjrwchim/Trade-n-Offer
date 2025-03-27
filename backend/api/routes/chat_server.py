from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import mysql.connector
from app.db_config import get_db_connection  # Import MySQL connection
from app.firebase_config import chat_db  # Import Firebase database

router = APIRouter()

active_connections = {}

def user_exists(username: str):
    """ Check if a user exists in MySQL """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id FROM userpass WHERE UserName = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user  # Returns user ID if exists, otherwise None

@router.websocket("/ws/chat/{sender}/{receiver}")
async def websocket_chat(websocket: WebSocket, sender: str, receiver: str):
    await websocket.accept()

    # ✅ 1. Check if both sender & receiver exist in MySQL
    sender_data = user_exists(sender)
    receiver_data = user_exists(receiver)

    if not sender_data or not receiver_data:
        await websocket.close(code=1008)  # Close connection if users don't exist
        return

    # ✅ 2. Create a unique chat room ID for the conversation
    chat_id = f"{sender}_{receiver}" if sender < receiver else f"{receiver}_{sender}"

    # ✅ 3. Store active connections
    if chat_id not in active_connections:
        active_connections[chat_id] = []
    active_connections[chat_id].append(websocket)

    # ✅ 4. Fetch chat history from Firebase
    chat_ref = chat_db.child(chat_id).child("messages")
    messages = chat_ref.get()

    if messages:
        for msg in messages.values():
            await websocket.send_text(f"{msg['sender']}: {msg['message']}")

    try:
        while True:
            message = await websocket.receive_text()

            # ✅ 5. Store message in Firebase
            chat_db.child(chat_id).child("messages").push({
                "sender": sender,
                "message": message
            })

            # ✅ 6. Send message only to sender & receiver
            for connection in active_connections.get(chat_id, []):
                await connection.send_text(f"{sender}: {message}")

    except WebSocketDisconnect:
        print(f"{sender} disconnected")
        active_connections[chat_id].remove(websocket)

    @router.get("/chat_history/{sender}/{receiver}")
    async def get_chat_history(sender: str, receiver: str):
        chat_id = f"{sender}_{receiver}" if sender < receiver else f"{receiver}_{sender}"
        
        # Fetch messages from Firebase
        chat_ref = chat_db.child(chat_id).child("messages")
        messages = chat_ref.get()

        if not messages:
            return {"messages": []}

        return {"messages": [{"sender": msg["sender"], "message": msg["message"]} for msg in messages.values()]}

