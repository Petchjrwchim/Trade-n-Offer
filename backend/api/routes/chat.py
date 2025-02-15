from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
from typing import List
import mysql.connector

router = APIRouter()

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Change if needed
        password="",  # Change if needed
        database="tno"
    )


class ChatManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, websocket: WebSocket, chat_id: str):
        await websocket.accept()
        self.active_connections[chat_id] = websocket

    def disconnect(self, chat_id: str):
        del self.active_connections[chat_id]

    async def send_message(self, chat_id: str, message: str):
        websocket = self.active_connections.get(chat_id)
        if websocket:
            await websocket.send_text(message)

    async def get_chat_history(self, sender_id: int, receiver_id: int) -> List[dict]:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM chat 
            WHERE (sender_id = %s AND receiver_id = %s) 
            OR (sender_id = %s AND receiver_id = %s)
            ORDER BY timestamp ASC
        """, (sender_id, receiver_id, receiver_id, sender_id))
        messages = cursor.fetchall()
        cursor.close()
        conn.close()
        return messages

chat_manager = ChatManager()

# WebSocket route for chat
@router.websocket("/ws/chat/{sender_id}/{receiver_id}")
async def websocket_chat(websocket: WebSocket, sender_id: int, receiver_id: int):
    await chat_manager.connect(websocket, f"{sender_id}-{receiver_id}")
    
    # Send chat history on connection
    history = await chat_manager.get_chat_history(sender_id, receiver_id)
    for message in history:
        await websocket.send_text(f"{message['sender_id']}: {message['message']}")

    try:
        while True:
            message = await websocket.receive_text()
            # Store the message in the database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat (sender_id, receiver_id, message) 
                VALUES (%s, %s, %s)
            """, (sender_id, receiver_id, message))
            conn.commit()
            cursor.close()
            conn.close()

            # Broadcast the message to the other user
            await chat_manager.send_message(f"{receiver_id}-{sender_id}", f"{sender_id}: {message}")
    except WebSocketDisconnect:
        chat_manager.disconnect(f"{sender_id}-{receiver_id}")
