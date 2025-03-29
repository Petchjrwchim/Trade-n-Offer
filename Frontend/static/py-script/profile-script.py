from js import document, console, FileReader
from pyodide.ffi import create_proxy

# Sidebar toggle
menu_toggle = document.querySelector('.menu-toggle')
sidebar = document.querySelector('.sidebar')

def toggle_sidebar(event):
    if sidebar and menu_toggle:
        sidebar.classList.toggle('active')
        menu_toggle.classList.toggle('active')

if menu_toggle:
    menu_toggle.addEventListener('click', create_proxy(toggle_sidebar))

# Tab switching
def show_tab(tab_name, event=None):
    console.log(f"Switching to {tab_name} tab")
    
    tabs = document.querySelectorAll('.tab-content')
    buttons = document.querySelectorAll('.tab-button')

    # Remove active class from all tabs and buttons
    for tab in tabs:
        tab.classList.remove('active')
    for button in buttons:
        button.classList.remove('active')

    # Add active class to selected tab and button
    tab_content = document.getElementById(f"{tab_name}-tab")
    tab_button = document.getElementById(f"{tab_name}Tab")
    
    if tab_content:
        tab_content.classList.add('active')
    else:
        console.error(f"Tab content #{tab_name}-tab not found")
        
    if tab_button:
        tab_button.classList.add('active')
    else:
        console.error(f"Tab button #{tab_name}Tab not found")

    # Render content for the selected tab
    if tab_name == 'products':
        render_products()
    elif tab_name == 'saved':
        render_saved()
    elif tab_name == 'liked':
        render_liked()
    else:
        console.error(f"Unknown tab: {tab_name}")

# Functions for handling profile popup
def open_edit_profile(event=None):
    popup = document.getElementById('editProfilePopup')
    if popup:
        popup.style.display = 'flex'
    else:
        console.error("Edit profile popup not found")

def close_edit_profile(event=None):
    popup = document.getElementById('editProfilePopup')
    if popup:
        popup.style.display = 'none'
    else:
        console.error("Edit profile popup not found")

def save_profile_changes(event=None):
    name_input = document.getElementById('editProfileName')
    desc_input = document.getElementById('editProfileDescription')
    
    if not name_input or not desc_input:
        console.error("Profile form elements not found")
        return
        
    name = name_input.value
    description = desc_input.value

    if name and description:
        name_element = document.querySelector('.profile-name')
        desc_element = document.querySelector('.profile-description')
        
        if name_element:
            name_element.textContent = name
        if desc_element:
            desc_element.textContent = description
            
        close_edit_profile()
    else:
        console.error('Please fill in all fields')

# Simulated product data
product_data = [
    {"id": 1, "name": "Laptop", "description": "Powerful laptop for gaming and work", "price": "999.99", "image": "/static/image_test/laptop.jpg"},
    {"id": 2, "name": "Fashion", "description": "Stylish outfit for everyday wear", "price": "199.99", "image": "/static/image_test/fashion.jpg"},
    {"id": 3, "name": "Sofa", "description": "Comfortable modern sofa for living room", "price": "599.99", "image": "/static/image_test/sofa.jpg"},
    {"id": 4, "name": "Lamp", "description": "Elegant floor lamp for home decor", "price": "89.99", "image": "/static/image_test/lamp.jpg"},
    {"id": 5, "name": "Sports Gear", "description": "Complete set of sports equipment", "price": "299.99", "image": "/static/image_test/sports_gear.jpg"},
    {"id": 6, "name": "Books", "description": "Collection of classic literature books", "price": "149.99", "image": "/static/image_test/books.jpg"}
]

# Simulated saved collections data
saved_data = [
    {"id": 1, "name": "Beads", "description": "Colorful beads for crafting", "price": "49.99", "image": "/static/image_test/beads.jpg"},
    {"id": 2, "name": "Fashion", "description": "Trendy jacket for all seasons", "price": "129.99", "image": "/static/image_test/fashion2.jpg"},
    {"id": 3, "name": "Books", "description": "Set of educational books", "price": "89.99", "image": "/static/image_test/books2.jpg"}
]

# Simulated liked items data
liked_data = [
    {"id": 1, "name": "Camera", "description": "High-quality digital camera for photography", "price": "499.99", "image": "/static/image_test/camera.jpg"},
    {"id": 2, "name": "Guitar", "description": "Acoustic guitar for beginners and professionals", "price": "299.99", "image": "/static/image_test/guitar.jpg"},
    {"id": 3, "name": "Piano", "description": "Digital piano with 88 keys and weighted action", "price": "799.99", "image": "/static/image_test/piano.jpg"}
]

# แก้ไขฟังก์ชันเพื่อรับ event parameter แต่ไม่ใช้
def render_products(event=None):
    product_grid = document.getElementById('productsGrid')
    if not product_grid:
        console.error("Product grid element (#productsGrid) not found!")
        return
    product_grid.innerHTML = ''
    for product in product_data:
        product_div = document.createElement('div')
        product_div.classList.add('product-card')

        img = document.createElement('img')
        img.src = product['image']
        img.alt = product['name']
        img.classList.add('product-image')

        name = document.createElement('div')
        name.classList.add('product-name')
        name.textContent = product['name']

        description = document.createElement('div')
        description.classList.add('product-description')
        description.textContent = product['description']

        price = document.createElement('div')
        price.classList.add('product-price')
        price.textContent = f"${product['price']}"

        product_div.appendChild(img)
        product_div.appendChild(name)
        product_div.appendChild(description)
        product_div.appendChild(price)
        product_grid.appendChild(product_div)
    console.log("Products rendered successfully")

# แก้ไขฟังก์ชันเพื่อรับ event parameter แต่ไม่ใช้
def render_saved(event=None):
    saved_grid = document.getElementById('savedGrid')
    if not saved_grid:
        console.error("Saved grid element (#savedGrid) not found!")
        return
    saved_grid.innerHTML = ''
    for item in saved_data:
        saved_div = document.createElement('div')
        saved_div.classList.add('saved-card')

        img = document.createElement('img')
        img.src = item['image']
        img.alt = item['name']
        img.classList.add('saved-image')

        name = document.createElement('div')
        name.classList.add('saved-name')
        name.textContent = item['name']

        description = document.createElement('div')
        description.classList.add('saved-description')
        description.textContent = item['description']

        price = document.createElement('div')
        price.classList.add('saved-price')
        price.textContent = f"${item['price']}"

        saved_div.appendChild(img)
        saved_div.appendChild(name)
        saved_div.appendChild(description)
        saved_div.appendChild(price)
        saved_grid.appendChild(saved_div)
    console.log("Saved collections rendered successfully")

# แก้ไขฟังก์ชันเพื่อรับ event parameter แต่ไม่ใช้
def render_liked(event=None):
    liked_grid = document.getElementById('likedGrid')
    if not liked_grid:
        console.error("Liked grid element (#likedGrid) not found!")
        return
    liked_grid.innerHTML = ''
    for item in liked_data:
        liked_div = document.createElement('div')
        liked_div.classList.add('liked-card')

        img = document.createElement('img')
        img.src = item['image']
        img.alt = item['name']
        img.classList.add('liked-image')

        name_container = document.createElement('div')
        name_container.classList.add('liked-name')
        
        # Add heart icon
        heart_icon = document.createElement('i')
        heart_icon.classList.add('fas', 'fa-heart', 'heart-icon')
        name_container.appendChild(heart_icon)
        
        # Add name text
        name_text = document.createTextNode(item['name'])
        name_container.appendChild(name_text)

        description = document.createElement('div')
        description.classList.add('liked-description')
        description.textContent = item['description']

        price = document.createElement('div')
        price.classList.add('liked-price')
        price.textContent = f"${item['price']}"

        liked_div.appendChild(img)
        liked_div.appendChild(name_container)
        liked_div.appendChild(description)
        liked_div.appendChild(price)
        liked_grid.appendChild(liked_div)
    console.log("Liked items rendered successfully")

# Event listeners for tab switching
productsTab = document.getElementById("productsTab")
likedTab = document.getElementById("likedTab")
savedTab = document.getElementById("savedTab")

if productsTab:
    productsTab.addEventListener("click", create_proxy(lambda e: show_tab("products", e)))
else:
    console.error("Products tab not found")
    
if likedTab:
    likedTab.addEventListener("click", create_proxy(lambda e: show_tab("liked", e)))
else:
    console.error("Liked tab not found")
    
if savedTab:
    savedTab.addEventListener("click", create_proxy(lambda e: show_tab("saved", e)))
else:
    console.error("Saved tab not found")
    
# Event listeners for profile editing
editProfileBtn = document.getElementById("editProfileBtn")
closeEditProfileBtn = document.getElementById("closeEditProfileBtn")
saveProfileBtn = document.getElementById("saveProfileBtn")

if editProfileBtn:
    editProfileBtn.addEventListener("click", create_proxy(open_edit_profile))
if closeEditProfileBtn:
    closeEditProfileBtn.addEventListener("click", create_proxy(close_edit_profile))
if saveProfileBtn:
    saveProfileBtn.addEventListener("click", create_proxy(save_profile_changes))

# Initialize with Saved Collections tab active (default)
render_saved()  # Render default tab on load