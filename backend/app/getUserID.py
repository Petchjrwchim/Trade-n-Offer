from fastapi import Request, HTTPException
from starlette.requests import Request

def check_session_cookie(request: Request):
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code=401, detail="Unauthorized - No session token")
    return session_token