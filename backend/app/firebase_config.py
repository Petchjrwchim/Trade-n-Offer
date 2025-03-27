import firebase_admin
from firebase_admin import credentials, db

# Load Firebase Admin SDK
cred = credentials.Certificate("firebase/tradenoffer-1fc06-firebase-adminsdk-fbsvc-56541571ef.json")  # Ensure the correct path
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://tradenoffer-1fc06-default-rtdb.asia-southeast1.firebasedatabase.app/"
})

# Firebase database references
chat_db = db.reference("private_chats")  # Private chat messages
users_db = db.reference("users")  # User storage

print("✅ Firebase Connected Successfully!")
