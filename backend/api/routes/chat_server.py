# api/routes/chat.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Request
from fastapi.responses import HTMLResponse
import mysql.connector
from typing import List

# Database connection
db = mysql.connector.connect(
    host="localhost",  # Change if necessary
    user="root",  # Replace with your MySQL username
    password="",  # Replace with your MySQL password
    database="tno"  # Database you created
)
cursor = db.cursor()

router = APIRouter()

# WebSocket endpoint for real-time chat
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()  # Receive message from client
            sender_id = 1  # Replace with user ID from your authentication system
            receiver_id = 2  # Replace with the actual receiver ID from your system

            # Insert the message into the database
            cursor.execute(
                "INSERT INTO chat (sender_id, receiver_id, message) VALUES (%s, %s, %s)",
                (sender_id, receiver_id, data)
            )
            db.commit()  # Commit the transaction

            # Send the received message back to the client
            await websocket.send_text(f"Message sent: {data}")
    
    except WebSocketDisconnect:
        print("Client disconnected")


