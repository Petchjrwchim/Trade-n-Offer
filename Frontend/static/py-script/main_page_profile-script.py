# from js import document, setTimeout, window

# total_items = 5

# def show_profile_popup(event=None):
#     """ Show popup and load product list """
#     popup = document.querySelector("#profilePopup")
#     popup.style.display = "block"
#     popup.classList.add("visible")
#     update_product_grid()

# def hide_popup():
#     """ Helper function to hide popup and reset overlay completely """
#     popup = document.querySelector("#profilePopup")
#     popup.style.display = "none"
#     popup.classList.remove("visible")
#     popup.style.opacity = "0"
#     popup.style.pointerEvents = "none"
#     popup.style.backgroundColor = "transparent"
    
#     # Ensure the body or other elements regain focus/interactivity
#     document.body.style.pointerEvents = "auto"

# def close_profile_popup(event=None):
#     """ Close popup by refreshing the page """
#     window.location.reload()  # Refresh the entire page when closing the popup

# def update_product_grid():
#     """ Update product list in Grid """
#     productGrid = document.querySelector("#productGrid")
#     productGrid.innerHTML = ""

#     for i in range(1, total_items + 1):
#         productDiv = document.createElement("div")
#         productDiv.classList.add("product-item")

#         img = document.createElement("img")
#         img.src = "/static/image_test/camera.jpg"
#         img.alt = f"Product {i}"
#         img.classList.add("product-image")

#         name = document.createElement("div")
#         name.classList.add("product-name")
#         name.textContent = f"Profile {i}"

#         productDiv.appendChild(img)
#         productDiv.appendChild(name)
#         productGrid.appendChild(productDiv)

# def go_to_my_items(event=None):
#     """ Redirect to /MyItem """
#     window.location.href = "/MyItem"

from js import document, console, window, localStorage
from pyodide.ffi import create_proxy

# Profile data
PROFILES = [
    {
        "id": "1", 
        "name": "Profile 1", 
        "image": "/static/image_test/profile_hover.jpg",
        "title": "First Profile"
    },
    {
        "id": "2", 
        "name": "Profile 2", 
        "image": "/static/image_test/profile_default.jpg",
        "title": "Second Profile"
    },
    {
        "id": "3", 
        "name": "Profile 3", 
        "image": "/static/image_test/profile_default.jpg",
        "title": "Third Profile"
    },
    {
        "id": "4", 
        "name": "Profile 4", 
        "image": "/static/image_test/profile_default.jpg",
        "title": "Fourth Profile"
    },
    {
        "id": "5", 
        "name": "Profile 5", 
        "image": "/static/image_test/profile_default.jpg",
        "title": "Fifth Profile"
    }
]

# Store event handler proxies
proxies = {}

def log(message):
    """Log message to console"""
    print(message)
    try:
        console.log(message)
    except:
        pass

def show_profile_popup(event=None):
    """Show profile popup"""
    log("Attempting to show profile popup")
    popup = document.getElementById("profilePopup")
    if popup:
        popup.style.display = "block"
        # Use timeout to ensure display change takes effect before adding class
        window.setTimeout(lambda: popup.classList.add("visible"), 10)
        update_product_grid()
        log("Profile popup displayed")
    else:
        log("Error: Profile popup element not found")

def close_profile_popup(event=None):
    """Close profile popup"""
    log("Attempting to close profile popup")
    popup = document.getElementById("profilePopup")
    if popup:
        popup.classList.remove("visible")
        # Use timeout to allow animation to complete before hiding
        window.setTimeout(lambda: setattr(popup.style, "display", "none"), 300)
        log("Profile popup closed")
    else:
        log("Error: Profile popup element not found")

def update_product_grid():
    """Update product grid with profiles"""
    log("Updating product grid")
    product_grid = document.getElementById("productGrid")
    if not product_grid:
        log("Error: Product grid element not found")
        return
        
    product_grid.innerHTML = ""
    
    for profile in PROFILES:
        # Create product item
        product_div = document.createElement("div")
        product_div.className = "product-item"
        product_div.setAttribute("data-profile-id", profile["id"])
        
        # Create image
        img = document.createElement("img")
        img.src = profile["image"]
        img.alt = profile["name"]
        img.className = "product-image"
        
        # Create name
        name_div = document.createElement("div")
        name_div.className = "product-name"
        name_div.textContent = profile["name"]
        
        # Create title
        title_div = document.createElement("div")
        title_div.className = "product-status"
        title_div.textContent = profile["title"]
        
        # Add hover effect
        def create_hover_handler(profile_id):
            def hover_in(event):
                event.currentTarget.querySelector("img").src = "/static/image_test/profile_hover.jpg"
            
            def hover_out(event):
                if profile_id != "1":  # Keep first profile with hover image
                    event.currentTarget.querySelector("img").src = "/static/image_test/profile_default.jpg"
            
            return hover_in, hover_out
        
        hover_in, hover_out = create_hover_handler(profile["id"])
        proxies[f"hover_in_{profile['id']}"] = create_proxy(hover_in)
        proxies[f"hover_out_{profile['id']}"] = create_proxy(hover_out)
        
        product_div.addEventListener("mouseenter", proxies[f"hover_in_{profile['id']}"])
        product_div.addEventListener("mouseleave", proxies[f"hover_out_{profile['id']}"])
        
        # Handle click
        proxies[f"click_{profile['id']}"] = create_proxy(lambda e, pid=profile["id"]: select_profile(pid))
        product_div.addEventListener("click", proxies[f"click_{profile['id']}"])
        
        # Append elements
        product_div.appendChild(img)
        product_div.appendChild(name_div)
        product_div.appendChild(title_div)
        product_grid.appendChild(product_div)
    
    log(f"Added {len(PROFILES)} profiles to grid")

def select_profile(profile_id):
    """Select profile by ID"""
    log(f"Selecting profile: {profile_id}")
    
    # Find selected profile
    selected_profile = next((p for p in PROFILES if p["id"] == profile_id), None)
    if not selected_profile:
        log(f"Profile with ID {profile_id} not found")
        return
    
    # Update main profile display
    profile_img = document.getElementById("profileImage")
    if profile_img:
        profile_img.src = selected_profile["image"]
    
    profile_name = document.querySelector(".profile-name")
    if profile_name:
        profile_name.textContent = selected_profile["name"]
    
    profile_title = document.querySelector(".profile-title")
    if profile_title:
        profile_title.textContent = selected_profile["title"]
    
    # Save to localStorage
    try:
        localStorage.setItem("selectedProfileId", profile_id)
        localStorage.setItem("selectedProfileName", selected_profile["name"])
        localStorage.setItem("selectedProfileTitle", selected_profile["title"])
    except Exception as e:
        log(f"Error saving to localStorage: {e}")
    
    # Close popup
    close_profile_popup()
    
    log(f"Profile {profile_id} selected successfully")

def go_to_my_items(event=None):
    """Navigate to My Items page"""
    window.location.href = "/MyItem"

def setup_handlers():
    """Set up event handlers"""
    log("Setting up event handlers")
    
    # Profile icon click to open popup
    profile_icon = document.querySelector(".profile-content")
    if profile_icon:
        proxies["show_popup"] = create_proxy(show_profile_popup)
        profile_icon.addEventListener("click", proxies["show_popup"])
        log("Profile icon click handler attached")
    else:
        log("Error: Profile icon element not found")
    
    # Close button click
    close_btn = document.querySelector(".close-btn")
    if close_btn:
        proxies["close_popup"] = create_proxy(close_profile_popup)
        close_btn.addEventListener("click", proxies["close_popup"])
        log("Close button click handler attached")
    else:
        log("Error: Close button element not found")
    
    # Add item button click
    add_btn = document.querySelector(".button")
    if add_btn:
        proxies["go_to_items"] = create_proxy(go_to_my_items)
        add_btn.addEventListener("click", proxies["go_to_items"])
        log("Add item button click handler attached")
    else:
        log("Error: Add item button element not found")

def load_saved_profile():
    """Load saved profile from localStorage"""
    try:
        profile_id = localStorage.getItem("selectedProfileId")
        if profile_id:
            select_profile(profile_id)
            log("Loaded saved profile from localStorage")
        else:
            log("No saved profile found in localStorage")
    except Exception as e:
        log(f"Error loading profile from localStorage: {e}")

def initialize():
    """Initialize on page load"""
    log("Initializing profile component")
    setup_handlers()
    load_saved_profile()
    log("Initialization complete")

# Run initialization when page loads
window.addEventListener("load", create_proxy(initialize))