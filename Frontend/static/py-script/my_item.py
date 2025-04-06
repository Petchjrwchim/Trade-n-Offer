from js import document, console, fetch, Promise, window
from pyodide.ffi import create_proxy, to_js
import json
import asyncio

selected_product = None

def open_add_popup(event=None):
    
    reset_add_product_form()
    document.querySelector("#addProductPopup").style.display = "block"

def reset_add_product_form():
    
    document.querySelector("#addProductName").value = ""
    document.querySelector("#addProductDescription").value = ""
    document.querySelector("#addProductPrice").value = ""
    document.querySelector("#addProductImage").value = ""
    
    
    preview = document.querySelector("#addProductImagePreview")
    placeholder = document.querySelector(".image-placeholder")
    
    if preview:
        preview.style.display = "none"
        preview.src = ""
    
    if placeholder:
        placeholder.style.display = "flex"
    
    
    trade_checkbox = document.querySelector("#addProductTrade")
    sell_checkbox = document.querySelector("#addProductSell")
    if trade_checkbox:
        trade_checkbox.checked = False
    if sell_checkbox:
        sell_checkbox.checked = False

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
            
            
            headers = [["Content-Type", "application/json"]]
        
            
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
        console.log("Fetching user items")

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

def update_product_grid():
    run_async(update_product_grid_with_search)

def run_async(async_func):
    Promise.resolve(to_js(async_func())).catch(lambda e: console.error(f"Error: {e}"))

async def update_product_grid_with_search():
    search_query = document.querySelector('#searchInput').value.strip().lower() if document.querySelector('#searchInput') else ""
    userItems = await fetch_userItem()

    productGrid = document.querySelector("#productGrid")
    if not productGrid:
        console.error("Product grid element not found!")
        return
    else:
        productGrid.innerHTML = ""
        if userItems:
            for item in userItems:
                add_product_element(item, False)
            console.log("Product grid updated")

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
    price.textContent = f"฿ {item['price']}"

    buttonContainer = document.createElement("div")
    buttonContainer.classList.add("product-buttons")

    editBtn = document.createElement("div")
    editBtn.classList.add("edit-btn")
    editBtn.textContent = "Edit"
    editBtn.addEventListener("click", create_proxy(lambda e: open_edit_popup(item)))

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

async def remove_product(product_id):
    try:
        console.log(f"Attempting to remove product with ID: {product_id}")
        
        headers = [["Content-Type", "application/json"]]
        response = await fetch(f"/remove-item/{product_id}",
                               method="DELETE",
                               headers=headers,
                               credentials="include")

        if response.status == 200:
            console.log("Product removed successfully")
            window.location.reload()
        else:
            data = await response.json()
            console.error(f"Failed to remove product: {data.get('detail', 'Unknown error')}")
    except Exception as e:
        console.error(f"Error removing product: {e}")

def remove_btn(item_id):
    console.log(f"Remove button clicked for item ID: {item_id}") 
    Promise.resolve(to_js(remove_product(item_id))).catch(lambda e: console.error(f"Error: {e}"))

def open_edit_popup(item):
    global selected_product
    selected_product = item
    
    if selected_product:
        document.querySelector("#editProductImage").src = selected_product["image"]
        document.querySelector("#editProductName").value = selected_product["name"]
        document.querySelector("#editProductDescription").value = selected_product["description"]
        document.querySelector("#editProductPrice").value = selected_product["price"]
        document.querySelector("#editProductPopup").style.display = "block"
    else:
        console.error(f"Product data not found")

def close_edit_popup(event=None):
    document.querySelector("#editProductPopup").style.display = "none"

async def save_product_changes(event=None):
    if selected_product:
        try:
            item_id = selected_product["id"]
            name = document.querySelector("#editProductName").value
            description = document.querySelector("#editProductDescription").value
            price = document.querySelector("#editProductPrice").value
            
            updated_product = {
                "item_name": name,
                "item_description": description,
                "item_price": price,
                
                "item_image": selected_product["image"]
            }
            
            headers = [["Content-Type", "application/json"]]
            response = await fetch(f"/edit-item/{item_id}", 
                                  method="PUT", 
                                  body=json.dumps(updated_product), 
                                  headers=headers, 
                                  credentials="include")
            
            if response.status == 200:
                console.log("Product updated successfully")
                close_edit_popup()
                window.location.reload()
            else:
                data = await response.json()
                console.error(f"Failed to update product: {data.get('detail', 'Unknown error')}")
                
        except Exception as e:
            console.error(f"Error updating product: {e}")
    else:
        console.error("No product selected for editing")


def setup_image_selection():
    try:
        
        file_input = document.querySelector("#addProductImage")
        if file_input:
            file_input.addEventListener("change", create_proxy(handle_image_selection))
            console.log("Image selection handler set up")
    except Exception as e:
        console.error(f"Error setting up image selection: {e}")

def handle_image_selection(event):
    try:
        files = event.target.files
        if files and files.length > 0:
            file = files.item(0)
            preview = document.querySelector("#addProductImagePreview")
            placeholder = document.querySelector(".image-placeholder")
            
            if preview and placeholder:
                reader = window.FileReader.new()
                
                def on_load(e):
                    preview.src = e.target.result
                    preview.style.display = "block"
                    placeholder.style.display = "none"  
                
                reader.onload = create_proxy(on_load)
                reader.readAsDataURL(file)
        else:
            
            preview = document.querySelector("#addProductImagePreview")
            placeholder = document.querySelector(".image-placeholder")
            
            if preview:
                preview.style.display = "none"
                preview.src = ""
            
            if placeholder:
                placeholder.style.display = "flex"  
    except Exception as e:
        console.error(f"Error handling image selection: {e}")


def select_file():
    document.querySelector("#addProductImage").click()


console.log("Initializing product grid and event handlers...")
update_product_grid()
setup_image_selection()


save_edit_btn = document.querySelector("#saveEditBtn")
if save_edit_btn:
    save_edit_btn.addEventListener("click", create_proxy(lambda e: run_async(save_product_changes)))

close_edit_btn = document.querySelector("#closeEditBtn")
if close_edit_btn:
    close_edit_btn.addEventListener("click", create_proxy(close_edit_popup))