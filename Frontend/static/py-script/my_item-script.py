from js import document, console, window, FileReader, fetch
from pyodide.ffi import create_proxy
import json

# Simulated product data without the category field
product_data = [
    {"id": 1, "name": "Camera", "description": "High-quality digital camera for photography", "price": "499.99", "image": "/static/image_test/camera.jpg"},
    {"id": 2, "name": "Guitar", "description": "Acoustic guitar for beginners and professionals", "price": "299.99", "image": "/static/image_test/guitar.jpg"},
    {"id": 3, "name": "Piano", "description": "Digital piano with 88 keys and weighted action", "price": "799.99", "image": "/static/image_test/piano.jpg"},
    {"id": 4, "name": "Laptop", "description": "Powerful laptop for gaming and work", "price": "999.99", "image": "/static/image_test/laptop.jpg"},
    {"id": 5, "name": "Phone", "description": "Latest smartphone with 5G and 128GB storage", "price": "699.99", "image": "/static/image_test/phone.jpg"}
]

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
        
        console.log(f"Attempting to save: name={name}, description={description}, price={price}, image_url={image_url}")
        
        if name and description and price and image_url:
            if not image_url.startswith("data:image/"):
                console.error("Invalid image URL detected")
                return
    
            new_product = {
                "item_name": name,
                "item_description": description,
                "item_price": price,
                "item_image": image_url,
                "is_available": True
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
        else:
            console.error("Please fill in all fields and select an image")
    except Exception as e:
        console.error(f"Error in save_new_product: {e}")

def update_product_grid():
    update_product_grid_with_search()

def update_product_grid_with_search():
    search_query = document.querySelector("#searchInput").value.strip().lower()
    filter_option = document.querySelector("#filterSelect").value

    filtered_data = [product for product in product_data if 
                    (search_query in product["name"].lower() or 
                        search_query in product["price"].lower())]

    if filter_option == "name_asc":
        filtered_data.sort(key=lambda x: x["name"].lower())
    elif filter_option == "name_desc":
        filtered_data.sort(key=lambda x: x["name"].lower(), reverse=True)
    elif filter_option == "price_asc":
        filtered_data.sort(key=lambda x: float(x["price"]))
    elif filter_option == "price_desc":
        filtered_data.sort(key=lambda x: float(x["price"]), reverse=True)

    productGrid = document.querySelector("#productGrid")
    if not productGrid:
        console.error("Product grid element (#productGrid) not found!")
        return
    productGrid.innerHTML = ""
    for product in filtered_data:
        add_product_element(product, False)
    console.log("Product grid updated with search and filter")

def add_product_element(product, is_new):
    productGrid = document.querySelector("#productGrid")
    productDiv = document.createElement("div")
    productDiv.classList.add("product-item")
    if is_new:
        productDiv.classList.add("new-product")

    img = document.createElement("img")
    img.src = product["image"]
    img.alt = product["name"]
    img.classList.add("product-image")

    name = document.createElement("div")
    name.classList.add("product-name")
    name.textContent = product["name"]

    description = document.createElement("div")
    description.classList.add("product-description")
    description.textContent = product["description"]

    price = document.createElement("div")
    price.classList.add("product-price")
    price.textContent = f"${product['price']}"

    buttonContainer = document.createElement("div")
    buttonContainer.classList.add("product-buttons")

    editBtn = document.createElement("div")
    editBtn.classList.add("edit-btn")
    editBtn.textContent = "Edit"
    editBtn.addEventListener("click", create_proxy(lambda e: open_edit_popup(product["id"])))

    removeBtn = document.createElement("div")
    removeBtn.classList.add("remove-btn")
    removeBtn.textContent = "Remove"

    buttonContainer.appendChild(editBtn)
    buttonContainer.appendChild(removeBtn)

    productDiv.appendChild(img)
    productDiv.appendChild(name)
    productDiv.appendChild(description)
    productDiv.appendChild(price)
    productDiv.appendChild(buttonContainer)
    productGrid.appendChild(productDiv)

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

console.log("Initializing product grid...")
update_product_grid()

window.addEventListener("load", create_proxy(lambda e: update_product_grid()))

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

document.querySelector("#searchInput").addEventListener("input", create_proxy(lambda e: update_product_grid_with_search()))
document.querySelector("#filterSelect").addEventListener("change", create_proxy(lambda e: update_product_grid_with_search()))
