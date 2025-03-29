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

        response = await fetch("http://127.0.0.1:8000/login",
                               method="POST",
                               body=json.dumps(userInfo),
                               headers=headers,
                               credentials="include")
        # response = await fetch(
        #     "http://127.0.0.1:8000/login",
        #     {
        #         "method": "POST",
        #         "headers": {"Content-Type": "application/json"},
        #         "body": json.dumps({"username": username, "password": password})
        #     }
        # )
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
        # error_message.textContent = "An error occurred during login. Please try again."

# Event listeners
document.querySelector('#loginBtn').addEventListener('click', create_proxy(login))

# Initialize the page (optional, if needed)
def on_load(event=None):
    console.log("Login page loaded")

document.addEventListener("DOMContentLoaded", create_proxy(on_load))