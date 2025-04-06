from js import document, console


saved_data = [
    {"id": 1, "name": "Beads", "description": "Colorful beads for crafting", "price": "49.99", "image": "/static/image_test/beads.jpg"},
    {"id": 2, "name": "Fashion", "description": "Trendy jacket for all seasons", "price": "129.99", "image": "/static/image_test/fashion2.jpg"},
    {"id": 3, "name": "Books", "description": "Set of educational books", "price": "89.99", "image": "/static/image_test/books2.jpg"}
]

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


render_saved()