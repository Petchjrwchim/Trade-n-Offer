from js import document, console, fetch, Promise, window
from pyodide.ffi import create_proxy, to_js
import json
import asyncio

selected_product = None

def open_add_popup(event=None):
    document.querySelector("#addProductName").value = ""
    document.querySelector("#addProductDescription").value = ""
    document.querySelector("#addProductPrice").value = ""
    document.querySelector("#addProductImage").value = ""
    document.querySelector("#addProductImagePreview").style.display = "none"
    document.querySelector("#addProductImagePreview").src = ""
    document.querySelector("#addProductPopup").style.display = "block"

def close_add_popup(event=None):
    document.querySelector("#addProductPopup").style.display = "none"

async def save_new_product(event=None):
    try:
        name = document.querySelector("#addProductName").value.strip()
        description = document.querySelector("#addProductDescription").value.strip()
        price = document.querySelector("#addProductPrice").value.strip()
        image_url = document.querySelector("#addProductImagePreview").src
        is_trade = document.querySelector("#addProductTrade").checked
        is_sell = document.querySelector("#addProductSell").checked
        
        console.log(f"Attempting to save: name={name}, description={description}, price={price}, image_url={image_url}, trade={is_trade}, sell={is_sell}")
        
        if name and description and price and image_url and (is_trade or is_sell):
            if not image_url.startswith("data:image/"):
                console.error("Invalid image URL detected")
                return
    
            new_product = {
                "item_name": name,
                "item_description": description,
                "item_price": price,
                "item_image": image_url,
                "is_available": True,
                "is_tradeable": is_trade,
                "is_purchasable": is_sell
            }
            
            # Instead of a dictionary, pass headers as an array of key-value pairs.
            headers = [["Content-Type", "application/json"]]
        
            # Send data to the backend via POST request with credentials included
            response = await fetch("/add-item", 
                                   method="POST", 
                                   body=json.dumps(new_product), 
                                   headers=headers, 
                                   credentials="include")
        
            data = await response.json()
            console.log("Product added:", data)
            close_add_popup()
            window.location.reload()
        else:
            console.error("Please fill in all fields, select an image, and choose at least one option (Trade or Sell)")
    except Exception as e:
        console.error(f"Error in save_new_product: {e}")


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
    
# Promise.resolve(to_js(fetch_userItem())).catch(lambda e: console.error(f"Error: {e}"))

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

    buttonContainer = document.createElement("div")
    buttonContainer.classList.add("product-buttons")

    editBtn = document.createElement("div")
    editBtn.classList.add("edit-btn")
    editBtn.textContent = "Edit"
    editBtn.addEventListener("click", create_proxy(lambda e: open_edit_popup(item["id"])))

    removeBtn = document.createElement("div")
    removeBtn.classList.add("remove-btn")
    removeBtn.textContent = "Remove"
    removeBtn.addEventListener("click", create_proxy(lambda e: remove_btn(item["id"])))

    buttonContainer.appendChild(editBtn)
    buttonContainer.appendChild(removeBtn)

    productDiv.appendChild(img)
    productDiv.appendChild(name)
    productDiv.appendChild(description)
    productDiv.appendChild(price)
    productDiv.appendChild(buttonContainer)
    productGrid.appendChild(productDiv)


console.log("Initializing product grid...")
update_product_grid()


async def remove_product(product_id):
    try:
        console.log(f"Attempting to remove product with ID: {product_id}")
        
        headers = [["Content-Type", "application/json"]]
        response = await fetch(f"/remove-item/{product_id}",
                               method="delete",
                               headers=headers,
                               credentials="include")

        if response.status == 200:
            console.log("Product removed successfully")
        else:
            data = await response.json()
            console.error(f"Failed to remove product: {data.get('detail', 'Unknown error')}")
    except Exception as e:
        console.error(f"Error removing product: {e}")

def remove_btn(item_id):
    console.log(f"Remove button clicked for item ID: {item_id}") 
    Promise.resolve(to_js(remove_product(item_id))).catch(lambda e: console.error(f"Error: {e}"))
    window.location.reload()

def open_edit_popup(product_id):
    global selected_product
    selected_product = next((p for p in product_data if p["id"] == product_id), None)
    if selected_product:
        document.querySelector("#editProductImage").src = selected_product["image"]
        document.querySelector("#editProductName").value = selected_product["name"]
        document.querySelector("#editProductDescription").value = selected_product["description"]
        document.querySelector("#editProductPrice").value = selected_product["price"]
        document.querySelector("#editProductPopup").style.display = "block"
    else:
        console.error(f"Product with ID {product_id} not found")

def close_edit_popup(event=None):
    document.querySelector("#editProductPopup").style.display = "none"

def save_product_changes(event=None):
    if selected_product:
        selected_product["name"] = document.querySelector("#editProductName").value
        selected_product["description"] = document.querySelector("#editProductDescription").value
        selected_product["price"] = document.querySelector("#editProductPrice").value
        update_product_grid_with_search()
        close_edit_popup()
    else:
        console.error("No product selected for editing")




















# def update_product_grid():
#     update_product_grid_with_search()
    
# def update_product_grid_with_search():
#     search_query = document.querySelector("#searchInput").value.strip().lower()
#     # filter_option = document.querySelector("#filterSelect").value

#     filtered_data = [product for product in product_data if 
#                     (search_query in product["name"].lower() or 
#                         search_query in product["price"].lower())]

#     if filter_option == "name_asc":
#         filtered_data.sort(key=lambda x: x["name"].lower())
#     elif filter_option == "name_desc":
#         filtered_data.sort(key=lambda x: x["name"].lower(), reverse=True)
#     elif filter_option == "price_asc":
#         filtered_data.sort(key=lambda x: float(x["price"]))
#     elif filter_option == "price_desc":
#         filtered_data.sort(key=lambda x: float(x["price"]), reverse=True)

#     productGrid = document.querySelector("#productGrid")
#     if not productGrid:
#         console.error("Product grid element (#productGrid) not found!")
#         return
#     productGrid.innerHTML = ""
#     for product in filtered_data:
#         add_product_element(product, False)
    # console.log("Product grid updated with search and filter")

# def add_product_element(product, is_new):
#     productGrid = document.querySelector("#productGrid")
#     productDiv = document.createElement("div")
#     productDiv.classList.add("product-item")
#     if is_new:
#         productDiv.classList.add("new-product")

#     img = document.createElement("img")
#     img.src = product["image"]
#     img.alt = product["name"]
#     img.classList.add("product-image")

#     name = document.createElement("div")
#     name.classList.add("product-name")
#     name.textContent = product["name"]

#     description = document.createElement("div")
#     description.classList.add("product-description")
#     description.textContent = product["description"]

#     price = document.createElement("div")
#     price.classList.add("product-price")
#     price.textContent = f"${product['price']}"

#     buttonContainer = document.createElement("div")
#     buttonContainer.classList.add("product-buttons")

#     editBtn = document.createElement("div")
#     editBtn.classList.add("edit-btn")
#     editBtn.textContent = "Edit"
#     editBtn.addEventListener("click", create_proxy(lambda e: open_edit_popup(product["id"])))

#     removeBtn = document.createElement("div")
#     removeBtn.classList.add("remove-btn")
#     removeBtn.textContent = "Remove"

#     buttonContainer.appendChild(editBtn)
#     buttonContainer.appendChild(removeBtn)

#     productDiv.appendChild(img)
#     productDiv.appendChild(name)
#     productDiv.appendChild(description)
#     productDiv.appendChild(price)
#     productDiv.appendChild(buttonContainer)
#     productGrid.appendChild(productDiv)

# console.log("Initializing product grid...")
# update_product_grid()

# window.addEventListener("load", create_proxy(lambda e: update_product_grid()))

# def handle_image_preview(event):
#     files = event.target.files  # Get the FileList object
#     if files.length > 0:  # Use .length to check if there are files
#         file = files.item(0)  # Use .item() to access the first file
#         if file:
#             preview = document.querySelector("#addProductImagePreview")
#             reader = FileReader.new()
            
#             def on_load(e):
#                 preview.src = e.target.result
#                 preview.style.display = "block"
            
#             reader.onload = create_proxy(on_load)
#             reader.readAsDataURL(file)
#     else:
#         preview = document.querySelector("#addProductImagePreview")
#         preview.style.display = "none"
#         preview.src = ""

# document.querySelector("#addProductImage").addEventListener("change", create_proxy(handle_image_preview))

# document.querySelector("#searchInput").addEventListener("input", create_proxy(lambda e: update_product_grid_with_search()))
# document.querySelector("#filterSelect").addEventListener("change", create_proxy(lambda e: update_product_grid_with_search()))