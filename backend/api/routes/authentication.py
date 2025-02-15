from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector

# Create the router instance
router = APIRouter()

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Change if needed
        password="",  # Change if needed
        database="tno"
    )

# Login endpoint
@router.post("/login")
async def login(user: dict):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM userpass WHERE UserName = %s AND UserPass = %s", 
                   (user["username"], user["password"]))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        # Set the session token
        response = JSONResponse(content={"message": f"Welcome, {user['username']}!"})
        response.set_cookie(key="session_token", value=user["username"], httponly=True)  # Set session cookie
        return response
    else:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    # if result:
    #     return {"message": f"Welcome, {user['username']}!"}
    # else:
    #     raise HTTPException(status_code=401, detail="Incorrect username or password")

# @router.post("/register")
# async def register(user: dict):
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     cursor.execute("SELECT * FROM userpass WHERE UserName = %s", (user["username"],))
#     if cursor.fetchone():
#         cursor.close()
#         conn.close()
#         raise HTTPException(status_code=400, detail="Username already exists")

#     cursor.execute("INSERT INTO userpass (UserName, UserPass) VALUES (%s, %s)", 
#                    (user["username"], user["password"]))
#     conn.commit()
#     cursor.close()
#     conn.close()
    
#     return {"message": f"User {user['username']} registered successfully!"}
