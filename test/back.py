from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to a specific domain in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Change if needed
        password="",  # Change if needed
        database="tno"
    )

# Login endpoint
@app.post("/login")
async def login(user: dict):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM userpass WHERE UserName = %s AND UserPass = %s", 
                   (user["username"], user["password"]))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        return {"message": f"Welcome, {user['username']}!"}
    else:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

@app.post("/register")
async def register(user: dict):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM userpass WHERE UserName = %s", (user["username"],))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Username already exists")

    cursor.execute("INSERT INTO userpass (UserName, UserPass) VALUES (%s, %s)", 
                   (user["username"], user["password"]))
    conn.commit()
    cursor.close()
    conn.close()
    
    return {"message": f"User {user['username']} registered successfully!"}