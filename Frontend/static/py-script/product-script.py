from js import document, console

# Simulated product data
product_data = [
    {"id": 1, "name": "Laptop", "description": "Powerful laptop for gaming and work", "price": "999.99", "image": "/static/image_test/laptop.jpg"},
    {"id": 2, "name": "Fashion", "description": "Stylish outfit for everyday wear", "price": "199.99", "image": "/static/image_test/fashion.jpg"},
    {"id": 3, "name": "Sofa", "description": "Comfortable modern sofa for living room", "price": "599.99", "image": "/static/image_test/sofa.jpg"},
    {"id": 4, "name": "Lamp", "description": "Elegant floor lamp for home decor", "price": "89.99", "image": "/static/image_test/lamp.jpg"},
    {"id": 5, "name": "Sports Gear", "description": "Complete set of sports equipment", "price": "299.99", "image": "/static/image_test/sports_gear.jpg"},
    {"id": 6, "name": "Books", "description": "Collection of classic literature books", "price": "149.99", "image": "/static/image_test/books.jpg"}
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

# Render products when the page loads or when the tab is shown
render_products()