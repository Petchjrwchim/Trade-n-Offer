import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Path to service account file
SERVICE_ACCOUNT_PATH = Path(__file__).parent.parent.parent / "firebase-service-account.json"

# Firebase configuration
FIREBASE_CONFIG = {
    "apiKey": os.getenv("FIREBASE_API_KEY", "AIzaSyDx43F34QRLQss07udVOf7wfURDaVIZ9EY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", "tnof-98bb3.firebaseapp.com"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL", "https://tnof-98bb3-default-rtdb.asia-southeast1.firebasedatabase.app"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID", "tnof-98bb3"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", "tnof-98bb3.firebasestorage.app"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", "770087345899"),
    "appId": os.getenv("FIREBASE_APP_ID", "1:770087345899:web:3c7759b395c57ea8a4a8ae")
}

# Check if service account file exists
SERVICE_ACCOUNT_EXISTS = os.path.exists(SERVICE_ACCOUNT_PATH)