from js import document, window
from pyodide.ffi import create_proxy

# Define product data for each category with prices as numbers for comparison
products = {
    "category1": [
        {"name": "Camera", "description": "High-quality digital camera for photography", "price": 499.99, "image": "https://via.placeholder.com/280x260"},
        {"name": "Guitar", "description": "Acoustic guitar for beginners", "price": 299.99, "image": "https://via.placeholder.com/280x260"},
        {"name": "Headphones", "description": "Noise-canceling headphones with premium sound", "price": 199.99, "image": "https://via.placeholder.com/280x260"},
        {"name": "Watch", "description": "Luxury smartwatch with fitness tracking", "price": 349.99, "image": "https://via.placeholder.com/280x260"},
        {"name": "Microphone", "description": "Studio-quality microphone for recording", "price": 149.99, "image": "https://via.placeholder.com/280x260"},
        {"name": "Tablet", "description": "High-resolution tablet for entertainment", "price": 399.99, "image": "https://via.placeholder.com/280x260"}
    ],
    "category2": [
        {"name": "Piano", "description": "Digital piano with 88 keys and weighted action", "price": 799.99, "image": "https://via.placeholder.com/280x260"},
        {"name": "Laptop", "description": "High-performance laptop for work and gaming", "price": 1299.99, "image": "https://via.placeholder.com/280x260"},
        {"name": "Smartphone", "description": "Latest model smartphone with advanced features", "price": 699.99, "image": "https://via.placeholder.com/280x260"},
        {"name": "Drone", "description": "High-tech drone for aerial photography", "price": 899.99, "image": "https://via.placeholder.com/280x260"},
        {"name": "Speaker", "description": "Portable Bluetooth speaker with deep bass", "price": 129.99, "image": "https://via.placeholder.com/280x260"},
        {"name": "Camera Lens", "description": "Professional camera lens for photography", "price": 599.99, "image": "https://via.placeholder.com/280x260"},
        {"name": "Keyboard", "description": "Mechanical keyboard for gaming", "price": 89.99, "image": "https://via.placeholder.com/280x260"},
        {"name": "Monitor", "description": "4K monitor for design and gaming", "price": 299.99, "image": "https://via.placeholder.com/280x260"}
    ],
    "all": [
        {"name": "Camera", "description": "High-quality digital camera for photography", "price": 499.99, "image": "https://via.placeholder.com/280x260"},
        {"name": "Guitar", "description": "Acoustic guitar for beginners", "price": 299.99, "image": "https://via.placeholder.com/280x260"},
        {"name": "Piano", "description": "Digital piano with 88 keys and weighted action", "price": 799.99, "image": "https://via.placeholder.com/280x260"},
        {"name": "Laptop", "description": "High-performance laptop for work and gaming", "price": 1299.99, "image": "https://via.placeholder.com/280x260"},
        {"name": "Headphones", "description": "Noise-canceling headphones with premium sound", "price": 199.99, "image": "https://via.placeholder.com/280x260"},
        {"name": "Smartphone", "description": "Latest model smartphone with advanced features", "price": 699.99, "image": "https://via.placeholder.com/280x260"},
        {"name": "Watch", "description": "Luxury smartwatch with fitness tracking", "price": 349.99, "image": "https://via.placeholder.com/280x260"},
        {"name": "Tablet", "description": "High-resolution tablet for entertainment", "price": 399.99, "image": "https://via.placeholder.com/280x260"},
        {"name": "Drone", "description": "High-tech drone for aerial photography", "price": 899.99, "image": "https://via.placeholder.com/280x260"},
        {"name": "Speaker", "description": "Portable Bluetooth speaker with deep bass", "price": 129.99, "image": "https://via.placeholder.com/280x260"},
        {"name": "Camera Lens", "description": "Professional camera lens for photography", "price": 599.99, "image": "https://via.placeholder.com/280x260"},
        {"name": "Microphone", "description": "Studio-quality microphone for recording", "price": 149.99, "image": "https://via.placeholder.com/280x260"}
    ]
}

def update_product_grid(products_list=None, message=None):
    """ Update product grid based on products list or display message if no results """
    product_grid = document.getElementById("productGrid")
    product_grid.innerHTML = ""  # Clear current products

    if message:
        no_results = document.createElement("div")
        no_results.classList.add("no-results")
        no_results.textContent = message
        no_results.style.color = "#161616"
        no_results.style.textAlign = "center"
        no_results.style.padding = "20px"
        product_grid.appendChild(no_results)
    elif products_list:
        for product in products_list:
            product_div = document.createElement("div")
            product_div.classList.add("product-item")

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
            price.textContent = f"${product['price']:.2f}"

            # Add new SVG flag implementation (starting unchecked)
            flag_container = document.createElement("label")
            flag_container.classList.add("container")
            flag_container.innerHTML = """
                <input type="checkbox" />
                <svg class="save-regular" xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 384 512">
                    <path d="M0 48C0 21.5 21.5 0 48 0l0 48V441.4l130.1-92.9c8.3-6 19.6-6 27.9 0L336 441.4V48H48V0H336c26.5 0 48 21.5 48 48V488c0 9-5 17.2-13 21.3s-17.6 3.4-24.9-1.8L192 397.5 37.9 507.5c-7.3 5.2-16.9 5.9-24.9 1.8S0 497 0 488V48z"></path>
                </svg>
                <svg class="save-solid" xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 384 512">
                    <path d="M0 48V487.7C0 501.1 10.9 512 24.3 512c5 0 9.9-1.5 14-4.4L192 400 345.7 507.6c4.1 2.9 9 4.4 14 4.4c13.4 0 24.3-10.9 24.3-24.3V48c0-26.5-21.5-48-48-48H48C21.5 0 0 21.5 0 48z"></path>
                </svg>
            """
            flag_container.querySelector("input").addEventListener("change", create_proxy(lambda event: toggle_flag(event, flag_container)))

            product_div.appendChild(img)
            product_div.appendChild(name)
            product_div.appendChild(description)
            product_div.appendChild(price)
            product_div.appendChild(flag_container)
            product_grid.appendChild(product_div)

def search_products(search_term):
    """ Search products by name in the 'all' category """
    if not search_term or search_term.strip() == "":
        update_product_grid(products["all"])
        return
    
    search_term = search_term.lower()
    matching_products = [p for p in products["all"] if search_term in p["name"].lower()]
    
    if matching_products:
        update_product_grid(matching_products)
    else:
        update_product_grid(None, "No results found or product not available")

def on_search(event):
    """ Handle search input or button click """
    search_term = document.getElementById("searchInput").value
    search_products(search_term)

def update_price_display(event):
    """ Update the displayed price value as the slider moves """
    slider = document.getElementById("priceSlider")
    price_value = document.getElementById("priceValue")
    # Convert slider.value (string) to float
    slider_value = float(slider.value)
    price = (slider_value / 100) * 1000  # Map 0-100 to 0-1000
    price_value.textContent = f"${price:.2f}"

def filter_products(event):
    """ Filter products based on category and price range """
    category_select = document.getElementById("categorySelect")
    price_slider = document.getElementById("priceSlider")
    
    category = category_select.value
    # Convert slider.value (string) to float
    max_price = (float(price_slider.value) / 100) * 1000  # Map 0-100 to 0-1000
    
    if category == "all":
        filtered_products = [p for p in products["all"] if p["price"] <= max_price]
    elif category == "category1":
        filtered_products = [p for p in products["category1"] if p["price"] <= max_price]
    else:  # category2
        filtered_products = [p for p in products["category2"] if p["price"] <= max_price]
    
    if filtered_products:
        update_product_grid(filtered_products)
    else:
        update_product_grid(None, "No products match your filter criteria")

def on_category_change(event):
    """ Handle category selection change (only update UI, not filter yet) """
    # This will now only update the UI but not filter until the button is clicked
    category = event.target.value
    if category == "all":
        update_product_grid(products["all"])
    elif category == "category1":
        update_product_grid(products["category1"][:6])  # Limit to 6 products
    elif category == "category2":
        update_product_grid(products["category2"][:8])  # Limit to 8 products

def toggle_flag(event, container):
    """ Toggle flag icon animation """
    # Use js.console.log to log to the JavaScript console
    window.console.log("Flag toggled")

# Initial setup
try:
    search_input = document.getElementById("searchInput")
    search_button = document.getElementById("searchButton")
    category_select = document.getElementById("categorySelect")
    price_slider = document.getElementById("priceSlider")
    filter_button = document.getElementById("filterButton")
    
    # Show all products initially
    update_product_grid(products["all"])

    # Add event listeners
    search_input.addEventListener("input", create_proxy(on_search))
    search_button.addEventListener("click", create_proxy(on_search))
    category_select.addEventListener("change", create_proxy(on_category_change))
    price_slider.addEventListener("input", create_proxy(update_price_display))  # Update price display on slider move
    filter_button.addEventListener("click", create_proxy(filter_products))  # Filter on button click
except Exception as e:
    console.error(f"Error initializing: {e}")