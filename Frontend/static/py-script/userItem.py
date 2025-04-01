from pyodide.ffi import  create_proxy, to_js
import json
from js import document, console, fetch, Promise

async def fetch_userItem():
    try:
        console.log("Fethcing user items")

        response = await fetch(
            "/my-items",
            to_js({
                "method": "GET",
                "header": {"Content-Type": "application/json"},
                "credentials": "include"
            })
        )

        console.log(f"Status {response.status}")

        if response.status == 200:
            items = await response.json()
            console.log("User Item: ", items)
            return items
        
        else:
            console.error(f"Failed to fetch posts. Status: {response.status}")
            return []
    
    except Exception as e:
        console.error(f"Error fetching posts: {e}")
        return []
    
Promise.resolve(to_js(fetch_userItem())).catch(lambda e: console.error(f"Error: {e}"))