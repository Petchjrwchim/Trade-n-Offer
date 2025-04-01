from js import document, console, FileReader
from pyodide.ffi import create_proxy

# Sidebar toggle
menu_toggle = document.querySelector('.menu-toggle')
sidebar = document.querySelector('.sidebar')

def toggle_sidebar(event):
    sidebar.classList.toggle('active')
    menu_toggle.classList.toggle('active')

menu_toggle.addEventListener('click', create_proxy(toggle_sidebar))

# Tab switching
def show_tab(tab_name, event=None):  # Added event parameter to handle the event object
    tabs = document.querySelectorAll('.tab-content')
    buttons = document.querySelectorAll('.tab-button')

    for tab in tabs:
        tab.classList.remove('active')
    for button in buttons:
        button.classList.remove('active')

    document.querySelector(f'#{tab_name}-tab').classList.add('active')
    document.querySelector(f'.tab-button[id="{tab_name}Tab"]').classList.add('active')  # Updated selector to use ID

    if tab_name == 'products':
        render_products()
    elif tab_name == 'saved':
        render_saved()

# Edit Profile Popup
def open_edit_profile(event=None):
    document.querySelector('#editProfilePopup').style.display = 'flex'

def close_edit_profile(event=None):
    document.querySelector('#editProfilePopup').style.display = 'none'

def save_profile_changes(event=None):
    name = document.querySelector('#editProfileName').value
    description = document.querySelector('#editProfileDescription').value

    if name and description:
        document.querySelector('.profile-name').textContent = name
        document.querySelector('.profile-description').textContent = description
        close_edit_profile()
    else:
        console.error('Please fill in all fields')

# Event listeners
document.querySelector('#editProfileBtn').addEventListener('click', create_proxy(open_edit_profile))
document.querySelector('#closeEditProfileBtn').addEventListener('click', create_proxy(close_edit_profile))
document.querySelector('#saveProfileBtn').addEventListener('click', create_proxy(save_profile_changes))
document.querySelector('#productsTab').addEventListener('click', create_proxy(lambda event: show_tab('products', event)))
document.querySelector('#savedTab').addEventListener('click', create_proxy(lambda event: show_tab('saved', event)))

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

def render_products():
    product_grid = document.querySelector('#productsGrid')
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

def render_saved():
    saved_grid = document.querySelector('#savedGrid')
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
show_tab('saved')