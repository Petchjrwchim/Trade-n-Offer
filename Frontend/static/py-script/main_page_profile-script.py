from js import document, setTimeout, window

total_items = 5

def show_profile_popup(event=None):
    """ Show popup and load product list """
    popup = document.querySelector("#profilePopup")
    popup.style.display = "block"
    popup.classList.add("visible")
    update_product_grid()

def hide_popup():
    """ Helper function to hide popup and reset overlay completely """
    popup = document.querySelector("#profilePopup")
    popup.style.display = "none"
    popup.classList.remove("visible")
    popup.style.opacity = "0"
    popup.style.pointerEvents = "none"
    popup.style.backgroundColor = "transparent"
    
    # Ensure the body or other elements regain focus/interactivity
    document.body.style.pointerEvents = "auto"

def close_profile_popup(event=None):
    """ Close popup by refreshing the page """
    window.location.reload()  # Refresh the entire page when closing the popup

def update_product_grid():
    """ Update product list in Grid """
    productGrid = document.querySelector("#productGrid")
    productGrid.innerHTML = ""

    for i in range(1, total_items + 1):
        productDiv = document.createElement("div")
        productDiv.classList.add("product-item")

        img = document.createElement("img")
        img.src = "/static/image_test/camera.jpg"
        img.alt = f"Product {i}"
        img.classList.add("product-image")

        name = document.createElement("div")
        name.classList.add("product-name")
        name.textContent = f"Profile {i}"

        productDiv.appendChild(img)
        productDiv.appendChild(name)
        productGrid.appendChild(productDiv)

def go_to_my_items(event=None):
    """ Redirect to /MyItem """
    window.location.href = "/MyItem"