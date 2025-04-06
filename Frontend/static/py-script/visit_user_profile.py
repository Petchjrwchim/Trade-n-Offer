from js import document, console, window, fetch, Promise, localStorage
from pyodide.ffi import create_proxy, to_js
import json
import asyncio


path = window.location.pathname
console.log("Current path:", path)
user_id = path.split('/')[-1]
console.log("Extracted user ID:", user_id)

# Helper function to show notifications
def show_notification(message, type="info"):
    notification = document.createElement('div')
    notification.className = f'notification {type}'
    notification.textContent = message
    notification.style.position = 'fixed'
    notification.style.bottom = '20px'
    notification.style.right = '20px'
    notification.style.padding = '10px 20px'
    notification.style.borderRadius = '5px'
    notification.style.zIndex = '1000'
    
    if type == "success":
        notification.style.backgroundColor = '#4CAF50'
        notification.style.color = 'white'
    elif type == "error":
        notification.style.backgroundColor = '#f44336'
        notification.style.color = 'white'
    else:
        notification.style.backgroundColor = '#2196F3'
        notification.style.color = 'white'
    
    document.body.appendChild(notification)
    
    # Remove notification after 3 seconds
    def remove_notification():
        document.body.removeChild(notification)
    window.setTimeout(create_proxy(remove_notification), 3000)

# Helper function to run async functions
def run_async(async_func):
    Promise.resolve(to_js(async_func())).catch(lambda e: console.error(f"Error: {e}"))

async def fetch_my_items():
    try:
        console.log("Fetching my items...")

        response = await fetch(
            "/my-items",  
            to_js({
                "method": "GET",
                "headers": {"Content-Type": "application/json"},
                "credentials": "include"
            })
        )

        if response.status == 200:
            items = await response.json()
            console.log("Fetched my items:", items)
            return items
        else:
            console.error(f"Failed to fetch my items. Status: {response.status}")
            return []

    except Exception as e:
        console.error(f"Error fetching my items: {e}")
        return []

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
    
    # Get current profile name
    username = document.getElementById('profileName').textContent
    
    # Use default images if not provided
    profile_pic = "/static/image_test/profile_avatar.png"
    image_url = item.get('image', '')
    
    # Populate popup content
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
                <!-- Add trade offer icon -->
                <i class="fas fa-handshake" id="offerIcon" style="font-size:24px; cursor:pointer;"></i>
            </div>
            <div style="display:flex; gap:15px;">
                <!-- Add purchase icon -->
                <i class="fas fa-shopping-cart" id="purchaseIcon" style="font-size:24px; cursor:pointer;"></i>
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
    
    # Create close button
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
    
    # Like icon click handler
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
    
            
    # Trade offer click handler
    def handle_trade_offer(event):
        offer_icon = document.getElementById('offerIcon')
        offer_icon.className = 'fas fa-spinner fa-pulse'
        
        # Create a fake event object with necessary attributes
        trade_event = type('obj', (object,), {
            'target': type('obj', (object,), {
                'getAttribute': lambda attr: 
                    item.get('ID') if attr == 'data-post-id' else
                    item.get('userID') if attr == 'data-user-id' else
                    item.get('name') if attr == 'data-item-name' else None,
                'className': offer_icon.className
            })
        })
        
        # Run the trade offer function
        run_async(lambda: create_direct_trade_offer(trade_event))
        
        # Close the popup
        close_popup(None)
    
    # Purchase offer click handler
    def handle_purchase_offer(event):
        purchase_icon = document.getElementById('purchaseIcon')
        purchase_icon.className = 'fas fa-spinner fa-pulse'
        
        # Create a fake event object with necessary attributes
        purchase_event = type('obj', (object,), {
            'target': type('obj', (object,), {
                'getAttribute': lambda attr: 
                    item.get('ID') if attr == 'data-post-id' else
                    item.get('userID') if attr == 'data-user-id' else
                    item.get('name') if attr == 'data-item-name' else None,
                'className': purchase_icon.className
            })
        })
        
        # Run the purchase offer function
        run_async(lambda: create_direct_purchase_offer(purchase_event))
        
        # Close the popup
        close_popup(None)
    
    # Add popup content and close button
    popup_content.appendChild(close_btn)
    popup.appendChild(popup_content)
    
    # Close popup handler
    def close_popup(event):
        document.body.removeChild(popup)
    
    # Add event listeners
    close_btn.addEventListener('click', create_proxy(close_popup))
    popup.addEventListener('click', create_proxy(lambda e: close_popup(e) if e.target == popup else None))
    
    # Add the popup to the document
    document.body.appendChild(popup)
    
    # Add event listeners for the icons
    like_icon = document.getElementById('likeIcon')
    offer_icon = document.getElementById('offerIcon')
    purchase_icon = document.getElementById('purchaseIcon')
    
    like_icon.addEventListener('click', create_proxy(toggle_like))
    offer_icon.addEventListener('click', create_proxy(handle_trade_offer))
    purchase_icon.addEventListener('click', create_proxy(handle_purchase_offer))

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
                
                # Debug information
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
            
            # Debug information
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
        productsGrid.innerHTML = ''  # Clear existing content
        
        # Handle empty items
        if not items or len(items) == 0:
            no_items = document.createElement('div')
            no_items.style.color = 'white'
            no_items.style.textAlign = 'center'
            no_items.style.padding = '20px'
            no_items.textContent = 'This user has no items to display'
            productsGrid.appendChild(no_items)
            return
        
        for item in items:
            if hasattr(item, 'to_py'):
                item = item.to_py()
            
            # Create item card
            item_div = document.createElement("div")
            item_div.className = "product-card"
            item_div.style.cursor = "pointer"
            
            # Create image
            img = document.createElement("img")
            img.src = item.get("image", "/static/image_test/default_product.png")  
            img.alt = item.get("name", "Item")
            img.className = "product-image"
            img.style.width = "100%"
            img.style.height = "300px"
            img.style.objectFit = "cover"
            
            # Create text container
            text_div = document.createElement("div")
            text_div.style.padding = "10px"
            
            # Create item name
            name = document.createElement("div")
            name.className = "product-name"
            name.textContent = item.get("name", "Item Name")
            name.style.color = "white"
            name.style.marginBottom = "5px"
            
            # Create price
            price = document.createElement("div")
            price.className = "product-price"
            price.textContent = item.get("price", "฿0")
            price.style.color = "#FFD700"  # Gold color
            
            # Create action buttons
            actions_div = document.createElement("div")
            actions_div.className = "product-actions"
            actions_div.style.display = "flex"
            actions_div.style.justifyContent = "space-between"
            actions_div.style.marginTop = "10px"
            
            # Create trade offer button
            trade_btn = document.createElement("i")
            trade_btn.className = "fas fa-handshake"
            trade_btn.style.cursor = "pointer"
            trade_btn.style.color = "#4CAF50"
            trade_btn.title = "Create trade offer"
            trade_btn.setAttribute('data-post-id', str(item.get('ID')))
            trade_btn.setAttribute('data-user-id', str(item.get('userID')))
            trade_btn.setAttribute('data-item-name', item.get('name'))
            
            # Create purchase button
            purchase_btn = document.createElement("i")
            purchase_btn.className = "fas fa-shopping-cart"
            purchase_btn.style.cursor = "pointer"
            purchase_btn.style.color = "#2196F3"
            purchase_btn.title = "Purchase this item"
            purchase_btn.setAttribute('data-post-id', str(item.get('ID')))
            purchase_btn.setAttribute('data-user-id', str(item.get('userID')))
            purchase_btn.setAttribute('data-item-name', item.get('name'))
            
            # Add event listeners
            trade_btn.addEventListener('click', create_proxy(lambda e, i=item: run_async(lambda: create_direct_trade_offer(e))))
            purchase_btn.addEventListener('click', create_proxy(lambda e, i=item: run_async(lambda: create_direct_purchase_offer(e))))
            
            # Assemble the item card
            actions_div.appendChild(trade_btn)
            actions_div.appendChild(purchase_btn)
            
            text_div.appendChild(name)
            text_div.appendChild(price)
            text_div.appendChild(actions_div)
            
            item_div.appendChild(img)
            item_div.appendChild(text_div)
            
            # Add click event to open the item popup
            def create_click_handler(selected_item):
                def handler(event):
                    # Only open popup if click is not on the action buttons
                    if event.target.tagName.lower() != 'i':
                        create_post_popup(selected_item)
                return handler
            
            click_proxy = create_proxy(create_click_handler(item))
            item_div.addEventListener('click', click_proxy)
            
            productsGrid.appendChild(item_div)
        
        console.log(f"Rendered {len(items)} user items")
    except Exception as e:
        console.error(f"Error rendering user items: {e}")
        
        error_div = document.createElement('div')
        error_div.textContent = "Error loading items. Please try again later."
        error_div.style.color = "white"
        error_div.style.textAlign = "center"
        error_div.style.padding = "20px"
        productsGrid.appendChild(error_div)

async def create_direct_trade_offer(event):
    try:
        # Get data from the clicked icon
        icon = event.target
        receiver_item_id = icon.getAttribute('data-post-id')
        receiver_id = icon.getAttribute('data-user-id')
        item_name = icon.getAttribute('data-item-name')
        
        if not receiver_item_id or not receiver_id:
            console.error("Missing required data for creating trade offer")
            window.alert("Unable to create trade offer: Missing data")
            return
        
        console.log(f"Creating trade offer for item: {item_name} (ID: {receiver_item_id})")
        
        # Show loading state
        icon.className = 'fas fa-spinner fa-pulse'
        
        # Get the current user's profile ID
        current_profile_id = localStorage.getItem("selectedProfileId")
        
        # This is the item that will be offered in exchange
        sender_item_id = current_profile_id
        
        # Fetch details about the user's item
        response = await fetch(
            f"/get-item/{sender_item_id}",
            to_js({
                "method": "GET",
                "headers": {"Content-Type": "application/json"},
                "credentials": "include"
            })
        )
        
        # Parse the response
        sender_item = await response.json()
        sender_item = sender_item.to_py()  
        
        # Get the sender's user ID
        sender_id = sender_item['userID']
        
        if not current_profile_id:
            window.alert("Please select a profile before making a trade offer.")
            icon.className = 'fas fa-handshake'
            return
            
        # Check if the user has items to trade
        my_items = await fetch_my_items()
        
        if not my_items or len(my_items) == 0:
            window.alert("You don't have any items to trade. Please add items first.")
            icon.className = 'fas fa-handshake'
            return
            
        # Create the trade offer data
        trade_offer_data = {
            "sender_id": sender_id,  
            "receiver_id": receiver_id,
            "sender_item_id": sender_item_id,
            "receiver_item_id": receiver_item_id
        }
        
        console.log("Sending trade offer data:", json.dumps(trade_offer_data))
        await call_backend(trade_offer_data)
        
    except Exception as e:
        console.error(f"Error in create_direct_trade_offer: {e}")
        window.alert("An unexpected error occurred while creating the trade offer.")
    finally:
        # Reset icon state
        icon.className = 'fas fa-handshake'

async def create_direct_purchase_offer(event):
    try:
        # Get data from the clicked icon
        icon = event.target
        item_id = icon.getAttribute('data-post-id')
        item_owner_id = icon.getAttribute('data-user-id')
        item_name = icon.getAttribute('data-item-name')
        
        if not item_id or not item_owner_id:
            console.error("Missing required data for creating purchase offer")
            window.alert("Unable to create purchase offer: Missing data")
            return
        
        console.log(f"Creating purchase offer for item: {item_name} (ID: {item_id})")
        
        # Show loading state
        icon.className = 'fas fa-spinner fa-pulse'
        
        # Check if the item is available for purchase
        headers = [["Content-Type", "application/json"]]
        status_response = await fetch(
            f"/purchase-offers/check-item/{item_id}",
            method="GET",
            headers=headers,
            credentials="include"
        )
        
        status_data = await status_response.json()
        
        # If item is not available for purchase, show an error
        if not status_data.available:
            window.alert(f"Item {item_name} is not available for purchase")
            icon.className = 'fas fa-shopping-cart'
            return
        
        # Create purchase offer data
        purchase_offer_data = {
            "item_id": int(item_id)
        }
        
        # Send purchase offer request
        headers = [["Content-Type", "application/json"]]
        response = await fetch("/purchase-offers/create",
                               method="POST",
                               body=json.dumps(purchase_offer_data),
                               headers=headers,
                               credentials="include")
        
        # Parse response
        data = await response.json()
        
        # Show notification based on response
        if response.ok:
            show_notification(f"Purchase offer created for {item_name}", "success")
        else:
            show_notification(data.get('detail', 'Failed to create purchase offer'), "error")
        
    except Exception as e:
        console.error(f"Error in create_direct_purchase_offer: {e}")
        window.alert("An unexpected error occurred while creating the purchase offer.")
    finally:
        # Reset icon state
        icon.className = 'fas fa-shopping-cart'

async def call_backend(offer):
    # Show loading notification
    show_notification("Processing your trade offer...", "info")
    
    # Send the offer to the backend
    headers = [["Content-Type", "application/json"]]
    response = await fetch("/create-offers",
                            method="POST",
                            body=json.dumps(offer),
                            headers=headers,
                            credentials="include")
    
    # Parse the response
    data = await response.json()
    console.log("Response:", data)
    
    # Show appropriate notification
    if response.ok:
        show_notification("Trade offer created successfully!", "success")
    else:
        show_notification("Failed to create trade offer", "error")
    
    return data

async def initialize():
    try:
        console.log("Initializing user profile page")
        await load_user_profile()
    except Exception as e:
        console.error(f"Error during initialization: {e}")


# Start the initialization process
Promise.resolve(to_js(initialize())).catch(lambda e: console.error(f"Error: {e}"))