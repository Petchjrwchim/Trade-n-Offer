from pyodide.ffi import  create_proxy, to_js
import json
from js import document, console, fetch, Promise, window

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
            console.log("User Item from userItems.py:", items)
            return items
        
        else:
            console.error(f"Failed to fetch posts. Status: {response.status}")
            return []
    
    except Exception as e:
        console.error(f"Error fetching posts: {e}")
        return []
    
Promise.resolve(to_js(fetch_userItem())).catch(lambda e: console.error(f"Error: {e}"))

def update_product_grid():
    run_async(update_product_grid_with_search)

def run_async(async_func):
    Promise.resolve(to_js(async_func())).catch(lambda e: console.error(f"Error: {e}"))

async def update_product_grid_with_search():
    search_query = document.querySelector('#searchInput').value.strip().lower()
    userItems = await fetch_userItem()

    productGrid = document.querySelector("#productGrid")
    if not productGrid:
        console.error("Product grid element not found!")
        return
    else:
        productGrid.innerHTML = ""
        for item in userItems:
            add_product_element(item, False)
        console.log("Product grid update")

def add_product_element(item, is_new):
    productGrid = document.querySelector("#productGrid")
    productDiv = document.createElement("div")
    productDiv.classList.add("product-item")

    item = item.to_py()

    if is_new:
        productDiv.classList.add("new-product")
    
    img = document.createElement("img")
    img.src = item["image"]
    img.alt = item["name"]
    img.classList.add("product-image")

    name = document.createElement("div")
    name.classList.add("product-name")
    name.textContent = item["name"]

    description = document.createElement("div")
    description.classList.add("product-description")
    description.textContent = item["description"]

    price = document.createElement("div")
    price.classList.add("product-price")
    price.textContent = f"${item['price']}"

    productDiv.appendChild(img)
    productDiv.appendChild(name)
    productDiv.appendChild(description)
    productDiv.appendChild(price)
    productGrid.appendChild(productDiv)


console.log("Initializing product grid...")
update_product_grid()

# window.addEventListener("load", create_proxy(lambda e: update_product_grid()))