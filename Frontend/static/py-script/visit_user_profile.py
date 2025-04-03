from js import document, console, window, fetch, Promise
from pyodide.ffi import create_proxy, to_js
import json
import asyncio

# Get the user ID from the URL
path = window.location.pathname
console.log("Current path:", path)
user_id = path.split('/')[-1]
console.log("Extracted user ID:", user_id)

# Sample user items data for testing if API is not available
sample_items = [
    {
        "id": 1,
        "name": "Camera",
        "description": "High-quality digital camera for photography",
        "price": "$499.99",
        "image": "/static/image_test/camera.jpg"
    }
]

def create_post_popup(item):
    # Create popup container
    popup = document.createElement('div')
    popup.style.position = 'fixed'
    popup.style.top = '0'
    popup.style.left = '0'
    popup.style.width = '100%'
    popup.style.height = '100%'
    popup.style.backgroundColor = 'rgba(0,0,0,0.8)'
    popup.style.display = 'flex'
    popup.style.justifyContent = 'center'
    popup.style.alignItems = 'center'
    popup.style.zIndex = '1000'
    
    # Create popup content
    popup_content = document.createElement('div')
    popup_content.style.width = '375px'
    popup_content.style.backgroundColor = 'white'
    popup_content.style.borderRadius = '15px'
    popup_content.style.overflow = 'hidden'
    popup_content.style.position = 'relative'
    
    # Get username from profile name
    username = document.getElementById('profileName').textContent
    
    # Create the popup content
    profile_pic = "/static/image_test/profile_default.jpg"
    image_url = item.get('image', '')
    
    popup_content.innerHTML = f'''
        <div style="display:flex; align-items:center; padding:10px;color:black">
            <img src="{profile_pic}" 
                    style="width:32px; height:32px; border-radius:50%; margin-right:10px;">
            <div style="font-weight:bold;">{username}</div>
        </div>
        
        <div style="width:100%; height:375px;">
            <img src="{image_url}" 
                    style="width:100%; height:100%; object-fit:cover;">
        </div>
        
        <div style="display:flex; justify-content:space-between; padding:10px;color:black">
            <div style="display:flex; gap:15px;">
                <i class="far fa-heart" id="likeIcon" style="font-size:24px; cursor:pointer;"></i>
            </div>
            <div>
                <i class="far fa-bookmark" id="bookmarkIcon" style="font-size:24px; cursor:pointer;"></i>
            </div>
        </div>
        
        <div style="padding:10px;">
            <div style="color:#0095f6; font-weight:bold;">
                {item.get('price', '')}
            </div>
            <div style="margin-top:5px;color:black">
                <span style="font-weight:bold; margin-right:5px; color:black">{username}</span>
                {item.get('description', '')}
            </div>
        </div>
    '''
    
    # Add close button
    close_btn = document.createElement('button')
    close_btn.textContent = '×'
    close_btn.style.position = 'absolute'
    close_btn.style.top = '10px'
    close_btn.style.right = '10px'
    close_btn.style.background = 'none'
    close_btn.style.border = 'none'
    close_btn.style.fontSize = '30px'
    close_btn.style.cursor = 'pointer'
    close_btn.style.zIndex = '1001'
    close_btn.style.color = 'white'
    
    # Functions for like and bookmark buttons
    def toggle_like(event):
        like_icon = document.getElementById('likeIcon')
        if 'far' in like_icon.className:
            like_icon.className = 'fas fa-heart'
            like_icon.style.color = 'red'
            Promise.resolve(to_js(add_to_wishlist(item.get('zodb_id')))).catch(
                lambda e: console.error(f"Error adding to wishlist: {e}")
            )
        else:
            like_icon.className = 'far fa-heart'
            like_icon.style.color = 'black'
            Promise.resolve(to_js(remove_from_wishlist(item.get('zodb_id')))).catch(
                lambda e: console.error(f"Error removing from wishlist: {e}")
            )
    
    def toggle_bookmark(event):
        bookmark_icon = document.getElementById('bookmarkIcon')
        if 'far' in bookmark_icon.className:
            bookmark_icon.className = 'fas fa-bookmark'
            bookmark_icon.style.color = 'black'
        else:
            bookmark_icon.className = 'far fa-bookmark'
            bookmark_icon.style.color = 'black'
    
    # Add content to popup
    popup_content.appendChild(close_btn)
    popup.appendChild(popup_content)
    
    # Close popup event
    def close_popup(event):
        document.body.removeChild(popup)
    
    close_btn.addEventListener('click', create_proxy(close_popup))
    popup.addEventListener('click', create_proxy(lambda e: close_popup(e) if e.target == popup else None))
    
    # Add popup to body
    document.body.appendChild(popup)
    
    # Add event listeners for like and bookmark
    like_icon = document.getElementById('likeIcon')
    bookmark_icon = document.getElementById('bookmarkIcon')
    
    like_icon.addEventListener('click', create_proxy(toggle_like))
    bookmark_icon.addEventListener('click', create_proxy(toggle_bookmark))

async def add_to_wishlist(item_id):
    try:
        if not item_id:
            console.error("No item ID provided")
            return
            
        headers = [["Content-Type", "application/json"]]
        response = await fetch(f"/add_wishlist/{item_id}",
                                method="POST",
                                headers=headers,
                                credentials="include")
        
        if response.ok:
            console.log(f"Item {item_id} added to wishlist")
        else:
            error_text = await response.text()
            console.error(f"Error adding to wishlist: {error_text}")
    except Exception as e:
        console.error(f"Error adding item to wishlist: {e}")

async def remove_from_wishlist(item_id):
    try:
        if not item_id:
            console.error("No item ID provided")
            return
            
        headers = [["Content-Type", "application/json"]]
        response = await fetch(f"/remove_wishlist/{item_id}",
                                method="DELETE",
                                headers=headers,
                                credentials="include")
        
        if response.ok:
            console.log(f"Item {item_id} removed from wishlist")
        else:
            error_text = await response.text()
            console.error(f"Error removing from wishlist: {error_text}")
    except Exception as e:
        console.error(f"Error removing item from wishlist: {e}")


async def fetch_user_profile():
        try:
            console.log(f"Fetching profile for user ID: {user_id}")
            

            headers = [["Content-Type", "application/json"]]
            response = await fetch(f"/user/{user_id}",
                               method="GET",
                               headers=headers,
                               credentials="include")
            
            console.log(f"API response status: {response.status}")
            
            if response.status == 200:
                profile_data = await response.json()
                return profile_data
            else:
                error_text = await response.text()
                console.error(f"Failed to load profile. Status: {response.status}, Error: {error_text}")
                document.getElementById("profileName").textContent = "User not found"
                
                # Create debug message for error
                debug_div = document.createElement('div')
                debug_div.style.backgroundColor = '#ff6b6b'
                debug_div.style.color = 'white'
                debug_div.style.padding = '10px'
                debug_div.style.margin = '10px'
                debug_div.style.borderRadius = '5px'
                debug_div.innerHTML = f'''
                    <h3>API Error</h3>
                    <p>Status: {response.status}</p>
                    <p>Error: {error_text}</p>
                '''
                
                productsGrid = document.getElementById("productsGrid")
                productsGrid.innerHTML = ''
                productsGrid.appendChild(debug_div)
                return None
        except Exception as e:
            console.error(f"Error loading profile: {e}")
            document.getElementById("profileName").textContent = "Error"
            
            # Create debug message for exception
            debug_div = document.createElement('div')
            debug_div.style.backgroundColor = '#ff6b6b'
            debug_div.style.color = 'white'
            debug_div.style.padding = '10px'
            debug_div.style.margin = '10px'
            debug_div.style.borderRadius = '5px'
            debug_div.innerHTML = f'''
                <h3>Exception</h3>
                <p>Error: {str(e)}</p>
            '''
            
            productsGrid = document.getElementById("productsGrid")
            productsGrid.innerHTML = ''
            productsGrid.appendChild(debug_div)
            return None
async def load_user_profile():
    try:
        profile_data = await fetch_user_profile()
        if not profile_data:
            return
        document.getElementById("profileName").textContent = profile_data.username
        userItems = profile_data.items
        render_user_items(userItems)
        console.log(userItems)
    except Exception as e:
        console.error(f"Error in load_user_profile: {e}")



def render_user_items(items):
        try:
            productsGrid = document.getElementById("productsGrid")
            
            # Debug: สร้าง Element แสดงข้อมูลสรุป
            debug_summary = document.createElement('div')
            debug_summary.style.backgroundColor = '#4b7bec'
            debug_summary.style.color = 'white'
            debug_summary.style.padding = '10px'
            debug_summary.style.margin = '10px'
            debug_summary.style.borderRadius = '5px'
            debug_summary.innerHTML = f'''
                <h3>Items Summary (Debug)</h3>
                <p>Total items: {len(items) if items else 0}</p>
                <p>Data type: {type(items).__name__}</p>
            '''
            
            productsGrid.appendChild(debug_summary)
            
            if not items or len(items) == 0:
                no_items = document.createElement('div')
                no_items.style.color = 'white'
                no_items.style.textAlign = 'center'
                no_items.style.padding = '20px'
                no_items.textContent = 'This user has no items to display'
                productsGrid.appendChild(no_items)
                return
            
            for index, item in enumerate(items):
                # Convert item if it's a JS object
                if hasattr(item, 'to_py'):
                    item = item.to_py()
                
                # Create debug card first
                debug_card = document.createElement('div')
                debug_card.style.backgroundColor = '#26de81'
                debug_card.style.color = 'white'
                debug_card.style.padding = '10px'
                debug_card.style.margin = '10px 0'
                debug_card.style.borderRadius = '5px'
                
                # Show all properties in item
                property_list = ""
                for key, value in item.items():
                    property_list += f"<li><strong>{key}:</strong> {value}</li>"
                
                debug_card.innerHTML = f'''
                    <h4>Item #{index+1} Debug</h4>
                    <ul style="list-style-type: none; padding-left: 10px;">
                        {property_list}
                    </ul>
                '''
                
                productsGrid.appendChild(debug_card)
                
                # Create item card (normal display)
                item_div = document.createElement("div")
                item_div.className = "product-card"
                item_div.style.cursor = "pointer"
                
                # Item image
                img = document.createElement("img")
                img.src = item.get("image", "")
                img.alt = item.get("name", "Item")
                img.className = "product-image"
                
                # Item name
                name = document.createElement("div")
                name.className = "product-name"
                name.textContent = item.get("name", "Item")
                
                # Item description
                description = document.createElement("div")
                description.className = "product-description"
                description.textContent = item.get("description", "")
                
                # Item price
                price = document.createElement("div")
                price.className = "product-price"
                price.textContent = item.get("price", "$0")
                
                # Add elements to card
                item_div.appendChild(img)
                item_div.appendChild(name)
                item_div.appendChild(description)
                item_div.appendChild(price)
                
                # Add click event to show item details
                def create_click_handler(selected_item):
                    def handler(event):
                        create_post_popup(selected_item)
                    return handler
                
                click_proxy = create_proxy(create_click_handler(item))
                item_div.addEventListener('click', click_proxy)
                
                # Add card to grid
                productsGrid.appendChild(item_div)
            
            console.log(f"Rendered {len(items)} user items")
        except Exception as e:
            console.error(f"Error rendering user items: {e}")
            
            # Create debug message for render exception
            debug_div = document.createElement('div')
            debug_div.style.backgroundColor = '#ff6b6b'
            debug_div.style.color = 'white'
            debug_div.style.padding = '10px'
            debug_div.style.margin = '10px'
            debug_div.style.borderRadius = '5px'
            debug_div.innerHTML = f'''
                <h3>Render Error</h3>
                <p>Error: {str(e)}</p>
            '''
            
            productsGrid = document.getElementById("productsGrid")
            productsGrid.innerHTML = ''
            productsGrid.appendChild(debug_div)

async def initialize():
    try:
        console.log("Initializing user profile page")
        await load_user_profile()
    except Exception as e:
        console.error(f"Error during initialization: {e}")

# Start the application
Promise.resolve(to_js(initialize())).catch(lambda e: console.error(f"Error: {e}"))