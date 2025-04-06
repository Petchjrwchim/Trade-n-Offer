from js import document, console, window, fetch
from pyodide.ffi import create_proxy
import json
import asyncio

async def login(event=None):
    username = document.querySelector('#username').value
    password = document.querySelector('#password').value
    error_message = document.querySelector('#error-message')
    print(username, password)
    if not username or not password:
        error_message.textContent = "Please enter both username and password!"
        return

    try:
        userInfo = {
            "username": username,
            "password": password
        }

        headers = [["Content-Type", "application/json"]]

        response = await fetch("/login",
                               method="POST",
                               body=json.dumps(userInfo),
                               headers=headers,
                               credentials="include")
        
        
        
        
        
        
        
        
        data = await response.json()

        if response.status == 200:
            window.localStorage.setItem("username", username)
            window.location.href = "/"
            window.alert(data.message)
        else:
            error_message.textContent = data.get('detail', 'Login failed')
    except Exception as e:
        console.error(f"Login error: {e}")
        error_message.textContent = "I'm here"
        


document.querySelector('#loginBtn').addEventListener('click', create_proxy(login))


def on_load(event=None):
    console.log("Login page loaded")

document.addEventListener("DOMContentLoaded", create_proxy(on_load))