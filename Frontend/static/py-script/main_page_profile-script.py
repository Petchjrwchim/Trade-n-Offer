from js import document, console, window, localStorage, setTimeout, fetch, Promise
from pyodide.ffi import create_proxy, to_js
import json


proxies = {}

def log(message):
    """Log function for consistent logging"""
    console.log(message)

def generate_profiles_from_items(items):
    """Convert database items to profile-like objects"""
    profiles = []
    for item in items:
        profile = {
            'id': str(item['id']),
            'name': item['name'],
            'description': item['description'],
            'image': item.get('image', "/static/image_test/placeholder.jpg")  
        }
        profiles.append(profile)
    return profiles

def select_profile(profile):
    """Select and update profile in UI"""
    try:
        default_image = "/static/image_test/placeholder.jpg"
        image = profile.get('image', default_image)
        name = profile.get('name', 'User Item')
        item_id = str(profile.get('id', ''))

        document.getElementById("profileImage").src = image
        document.getElementById("profileName").textContent = name
        
        localStorage.setItem("selectedProfileId", item_id)
        localStorage.setItem("selectedProfileName", name)
        localStorage.setItem("selectedProfileImage", image)
        
        
        Promise.resolve(to_js(fetch_and_display_profile_grid())).catch(
            lambda e: console.error(f"Error refreshing profile grid: {e}")
        )
        
    except Exception as e:
        log(f"Error selecting profile: {e}")

async def fetch_and_display_profile_grid():
    """Fetch user items and display in profile grid (name and image only)"""
    try:
        
        response = await fetch(
            "/my-items", 
            to_js({
                "method": "GET",
                "headers": {"Content-Type": "application/json"},
                "credentials": "include"
            })
        )
        
        
        if not response.ok:
            console.error(f"Failed to fetch items. Status: {response.status}")
            return []
        
        
        raw_items = await response.json()
        
        
        items = []
        if hasattr(raw_items, 'to_py'):
            items = raw_items.to_py()
        else:
            for i in range(len(raw_items)):
                item = raw_items[i]
                items.append({
                    'id': item['id'],
                    'name': item['name'],
                    'description': item.get('description', ''),
                    'image': item.get('image', "/static/image_test/placeholder.jpg")
                })
        
        
        profiles = generate_profiles_from_items(items)
        
        
        product_grid = document.getElementById("productGrid")
        if not product_grid:
            console.error("Product grid element not found!")
            return []
        
        
        product_grid.innerHTML = ""
        
        
        current_id = localStorage.getItem("selectedProfileId") or ""
        
        
        if len(profiles) == 0:
            
            no_profiles_div = document.createElement("div")
            no_profiles_div.className = "no-profiles"
            no_profiles_div.textContent = "NO PROFILE"
            product_grid.appendChild(no_profiles_div)
            return []
        
        
        for profile in profiles:
            
            profile_item = document.createElement("div")
            profile_item.className = "product-item"
            
            
            if profile['id'] == current_id:
                profile_item.classList.add("active")
                
            profile_item.setAttribute("data-profile-id", profile['id'])
            
            
            img = document.createElement("img")
            img.src = profile['image']
            img.className = "product-image"
            img.alt = profile['name']
            
            
            name = document.createElement("div")
            name.className = "product-name"
            name.textContent = profile['name']
            
            
            profile_item.appendChild(img)
            profile_item.appendChild(name)
            
            
            def make_handler(prof):
                def handler(event):
                    select_profile(prof)
                return handler
            
            click_proxy = create_proxy(make_handler(profile))
            
            proxy_key = f"click_{profile['id']}"
            proxies[proxy_key] = click_proxy
            profile_item.addEventListener("click", click_proxy)
            
            
            product_grid.appendChild(profile_item)
        
        console.log("Profile grid updated successfully")
        return profiles
    
    except Exception as e:
        console.error(f"Error in fetch_and_display_profile_grid: {e}")
        
        product_grid = document.getElementById("productGrid")
        if product_grid:
            product_grid.innerHTML = ""
            error_div = document.createElement("div")
            error_div.className = "no-profiles"
            error_div.textContent = "Error loading profiles"
            product_grid.appendChild(error_div)
        return []

def load_saved_profile():
    """Load saved profile from localStorage"""
    try:
        saved_id = localStorage.getItem("selectedProfileId")
        saved_name = localStorage.getItem("selectedProfileName")
        saved_image = localStorage.getItem("selectedProfileImage")

        if saved_id and saved_name:
            document.getElementById("profileImage").src = saved_image or "/static/image_test/placeholder.jpg"
            document.getElementById("profileName").textContent = saved_name
    except Exception as e:
        log(f"Error loading profile: {e}")

def go_to_my_items(event=None):
    """Redirect to My Items page"""
    window.location.href = "/MyItem"

def initialize():
    """Initialize the profile component"""
    
    proxies["go_to_my_items"] = create_proxy(go_to_my_items)
    
    
    add_item_btn = document.getElementById("addItemBtn")
    
    if add_item_btn:
        add_item_btn.addEventListener("click", proxies["go_to_my_items"])
    else:
        console.error("Add item button not found")
    
    
    load_saved_profile()
    Promise.resolve(to_js(fetch_and_display_profile_grid())).catch(
        lambda e: console.error(f"Error initializing profile grid: {e}")
    )


initialize()