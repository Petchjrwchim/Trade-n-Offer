from js import document, window, console
from pyodide.ffi import create_proxy

images = ["/static/image_test/camera.jpg", "/static/image_test/guitar.jpg", "/static/image_test/piano.jpg"]
product_details = [
    {"name": "Camera", "description": "High-quality digital camera for photography", "price": "$499.99"},
    {"name": "Guitar", "description": "Acoustic guitar for beginners and professionals", "price": "$299.99"},
    {"name": "Piano", "description": "Digital piano with 88 keys and weighted action", "price": "$799.99"}
]
current_index = 0
start_x = 0
start_y = 0

def show_next_image():
    global current_index
    current_index = (current_index + 1) % len(images)
    document.getElementById("productImage").src = images[current_index]
    document.getElementById("innerCard").setAttribute("data-flipped", "false")
    update_product_description()

def update_product_description():
    details = product_details[current_index]
    description_text = f"{details['name']}\n{details['description']}\nPrice: {details['price']}"
    document.getElementById("productDescription").innerText = description_text

def reset_card():
    document.getElementById("swipeCard").style.transform = "translate(0px, 0px) rotate(0deg)"
    show_next_image()

def on_drag_start(event):
    global start_x, start_y
    start_x = event.clientX
    start_y = event.clientY
    document.getElementById("swipeCard").classList.add("dragging")

def on_drag_end(event):
    offset_x = event.clientX - start_x
    offset_y = event.clientY - start_y
    document.getElementById("swipeCard").classList.remove("dragging")
    if offset_x > 100:
        handle_swipe("right")
    elif offset_x < -100:
        handle_swipe("left")
    elif offset_y > 100:
        handle_swipe("down")
    elif offset_y < -100:
        handle_swipe("up")
    else:
        reset_card()

def handle_swipe(direction):
    card = document.getElementById("swipeCard")
    transforms = {
        "left": "translateX(-300px) rotate(-20deg)",
        "right": "translateX(300px) rotate(20deg)",
        "up": "translateY(-300px)",
        "down": "translateY(300px)"
    }
    card.style.transform = transforms[direction]
    feedback = document.createElement("div")
    feedback.className = "swipe-feedback"
    if direction == "right":
        feedback.classList.add("loader")  # Add loader class for swipe-right
    else:
        feedback.innerText = "Disliked"  # Default text for other directions
    card.appendChild(feedback)
    feedback.classList.add("show")
    window.setTimeout(create_proxy(lambda: feedback.remove()), 500)  # Remove after animation
    window.setTimeout(create_proxy(reset_card), 500)

def toggle_flip(event):
    inner_card = document.getElementById("innerCard")
    is_flipped = inner_card.getAttribute("data-flipped") == "true"
    inner_card.setAttribute("data-flipped", "false" if is_flipped else "true")

def on_key_press(event):
    if event.key == "Enter":
        toggle_flip(event)
    elif event.key == "ArrowRight":
        handle_swipe("right")
    elif event.key == "ArrowLeft":
        handle_swipe("left")
    elif event.key == "ArrowUp":
        handle_swipe("up")
    elif event.key == "ArrowDown":
        handle_swipe("down")

def hide_tutorial():
    tutorial_overlay = document.getElementById("tutorialOverlay")
    if tutorial_overlay:
        tutorial_overlay.style.display = 'none'

# Initial setup
try:
    image = document.getElementById("productImage")
    back_content = document.getElementById("backContent")
    inner_card = document.getElementById("innerCard")
    swipe_card = document.getElementById("swipeCard")

    image.addEventListener("dragstart", create_proxy(on_drag_start))
    image.addEventListener("dragend", create_proxy(on_drag_end))
    back_content.addEventListener("dragstart", create_proxy(on_drag_start))
    back_content.addEventListener("dragend", create_proxy(on_drag_end))
    inner_card.addEventListener("dblclick", create_proxy(toggle_flip))
    swipe_card.addEventListener("keydown", create_proxy(on_key_press))

    # Hide tutorial overlay after first interaction or on button click
    tutorial_overlay = document.getElementById("tutorialOverlay")
    if tutorial_overlay:
        window.setTimeout(create_proxy(hide_tutorial), 5000)  # Auto-hide after 5 seconds

    # Initialize with the first product
    update_product_description()
except Exception as e:
    console.error(f"Error initializing card: {e}")