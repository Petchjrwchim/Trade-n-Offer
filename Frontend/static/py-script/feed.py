from pyscript import when
import pyodide.http
import json
from pyodide.ffi import create_proxy, to_js
from js import document, console, fetch, window, Promise, localStorage, setTimeout
import asyncio

async def fetch_posts():
    try:
        console.log("Fetching posts from backend.asdasdasdasd..")

        response = await fetch(
            "/get-all-posts",
            to_js({
                "method": "GET",
                "headers": {"Content-Type": "application/json"},
                "credentials": "include"
            })
        )

        console.log(f"Response status: {response.status}")

        if response.status == 200:
            posts = await response.json()
            console.log("Fetched posts:", posts)
            return posts
        else:
            console.error(f"Failed to fetch posts. Status: {response.status}")
            return []

    except Exception as e:
        console.error(f"Error fetching posts: {e}")
        return []


async def fetch_trade_offers():
    try:
        console.log("Fetching trade offers...")

        response = await fetch(
            "/get-trade-offers",  
            to_js({
                "method": "GET",
                "headers": {"Content-Type": "application/json"},
                "credentials": "include"
            })
        )

        console.log(f"Trade offers response status: {response.status}")

        if response.status == 200:
            offers = await response.json()
            console.log("Fetched trade offers:", offers)
            return offers
        else:
            console.error(f"Failed to fetch trade offers. Status: {response.status}")
            return []

    except Exception as e:
        console.error(f"Error fetching trade offers: {e}")
        return []

async def check_wishlist_status(item_id, heart_icon):
    try:
        headers = [["Content-Type", "application/json"]]
        response = await fetch(f"/status_wishlist/{item_id}",
                               method="GET",
                               headers=headers,
                               credentials="include")
        if not response.ok:
            console.log("Failed to fetch wishlist status")
            return
        
        data = await response.json()

        if data:
            heart_icon.className = 'fas fa-heart'
            heart_icon.style.color = '#ed4956'  
        else:
            heart_icon.className = 'far fa-heart'
            heart_icon.style.color = '#000'  

    except Exception as e:
        console.error(f"Error checking wishlist status: {e}")

def navigate_to_user_profile(user_id, username):
    try:
        if not user_id:
            console.error("No user ID provided for profile navigation")
            return
            
        console.log(f"Navigating to profile of user: {username} (ID: {user_id})")
        
        window.location.href = f"/user-profile/{user_id}"
    except Exception as e:
        console.error(f"Error navigating to user profile: {e}")





def create_post_element(post):
    try:
        if hasattr(post, 'to_py'):
            post = post.to_py()
        
        post_div = document.createElement('div')
        post_div.className = 'instagram-post'
        post_div.id = f"post-{post['zodb_id']}"
        post_div.setAttribute('data-username', post['username'])
        
        
        post_header = document.createElement('div')
        post_header.className = 'post-header'
        
        
        profile_picture = document.createElement('img')
        profile_picture.className = 'profile-picture'
        profile_picture.src = "/static/image_test/profile_avatar.png"
        profile_picture.alt = post['username']
        
        
        post_username = document.createElement('div')
        post_username.className = 'post-username'
        post_username.textContent = post['username']
        post_username.style.cursor = 'pointer'
        post_username.setAttribute('data-user-id', str(post['userID']))

        
        post_username.onclick = create_proxy(lambda event: navigate_to_user_profile(event.target.getAttribute('data-user-id'), post['username']))
        
        
        post_header.appendChild(profile_picture)
        post_header.appendChild(post_username)
        
        
        post_image = document.createElement('div')
        post_image.className = 'post-image'
        image = document.createElement('img')
        image.src = post['image']
        image.alt = 'Item for trade'
        post_image.appendChild(image)
        
        
        actions_container = document.createElement('div')
        actions_container.className = 'post-actions-container'
 
        action_buttons = document.createElement('div')
        action_buttons.className = 'action-buttons'

        heart_icon = document.createElement('i')
        heart_icon.className = 'far fa-heart'
        heart_icon.title = 'Interested in trading'
        heart_icon.setAttribute('data-post-id', str(post['zodb_id']))
        heart_icon.onclick = create_proxy(lambda event: toggle_like(event))
        action_buttons.appendChild(heart_icon)
        
        Promise.resolve(check_wishlist_status(post['zodb_id'], heart_icon))
        
        offer_container = document.createElement('div')
        offer_container.className = 'bookmark'
        
        
        offer_icon = document.createElement('i')
        offer_icon.className = 'fas fa-handshake'
        offer_icon.title = 'Create trade offer'
        offer_icon.style.color = '#000'
        
        
        offer_icon.setAttribute('data-post-id', str(post['ID']))
        offer_icon.setAttribute('data-user-id', str(post['userID']))
        offer_icon.setAttribute('data-item-name', post['name'])
        
        
        offer_icon.onclick = create_proxy(lambda event: run_async(lambda: create_direct_trade_offer(event)))
        offer_container.appendChild(offer_icon)

        
        purchase_icon = document.createElement('i')
        purchase_icon.className = 'fas fa-shopping-cart'
        purchase_icon.title = 'Create purchase offer'
        purchase_icon.style.color = '#000'
        
        
        purchase_icon.setAttribute('data-post-id', str(post['ID']))
        purchase_icon.setAttribute('data-user-id', str(post['userID']))
        purchase_icon.setAttribute('data-item-name', post['name'])
        
        
        purchase_icon.onclick = create_proxy(lambda event: run_async(lambda: create_direct_purchase_offer(event)))
        
        offer_container.appendChild(purchase_icon)
        actions_container.appendChild(action_buttons)
        actions_container.appendChild(offer_container)

        content_div = document.createElement('div')
        content_div.className = 'post-content'

        price_div = document.createElement('div')
        price_div.className = 'item-price'
        price_div.textContent = f"Price: {post['price']}"
        content_div.appendChild(price_div)
        
        user_caption = document.createElement('div')
        user_caption.className = 'user-caption'
        
        caption_container = document.createElement('div')
        caption_container.className = 'caption'
        
        
        
        
        item_name = document.createElement('span')
        item_name.className = 'itemName'
        item_name.textContent = post['name']
        
        
        caption_container.appendChild(item_name)
        user_caption.appendChild(caption_container)
        content_div.appendChild(user_caption)
        
        description_div = document.createElement('div')
        description_div.className = 'item-description'
        description_div.textContent = post['description']
        content_div.appendChild(description_div)
        
        
        post_div.appendChild(post_header)
        post_div.appendChild(post_image)
        post_div.appendChild(actions_container)
        post_div.appendChild(content_div)
        
        return post_div
    except Exception as e:
        console.error(f"Error creating post element: {e}")
        return document.createElement('div')
    
async def fetch_my_items():
    try:
        console.log("Fetching user's items...")

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
    
def create_active_profile_indicator():
    """Create a floating indicator showing the active profile"""
    try:
        
        profile_id = localStorage.getItem("selectedProfileId")
        profile_name = localStorage.getItem("selectedProfileName")
        profile_image = localStorage.getItem("selectedProfileImage") or "/static/image_test/placeholder.jpg"
        
        
        if not profile_id or not profile_name:
            indicator_text = "No profile selected"
            profile_image = "/static/image_test/placeholder.jpg"
        else:
            indicator_text = "Trading as: " + profile_name
        
        
        indicator = document.createElement('div')
        indicator.id = 'activeProfileIndicator'
        indicator.className = 'active-profile-indicator'
        
        
        img = document.createElement('img')
        img.src = profile_image
        img.alt = "Active Profile"
        
        
        text = document.createElement('span')
        text.textContent = indicator_text
        
        
        indicator.appendChild(img)
        indicator.appendChild(text)
        
        
        document.body.appendChild(indicator)
        
        
        def handle_storage_change(event):
            if event.key == "selectedProfileId" or event.key == "selectedProfileName" or event.key == "selectedProfileImage":
                
                old_indicator = document.getElementById('activeProfileIndicator')
                if old_indicator:
                    document.body.removeChild(old_indicator)
                
                create_active_profile_indicator()
        
        
        window.addEventListener('storage', create_proxy(handle_storage_change))
        
        console.log("Active profile indicator created")
    except Exception as e:
        console.error(f"Error creating active profile indicator: {e}")

def update_active_profile_indicator():
    """Update the active profile indicator with current profile info"""
    try:
        indicator = document.getElementById('activeProfileIndicator')
        if not indicator:
            create_active_profile_indicator()
            return
            
        
        profile_id = localStorage.getItem("selectedProfileId")
        profile_name = localStorage.getItem("selectedProfileName")
        profile_image = localStorage.getItem("selectedProfileImage") or "/static/image_test/placeholder.jpg"
        
        
        if not profile_id or not profile_name:
            indicator_text = "No profile selected"
            profile_image = "/static/image_test/placeholder.jpg"
        else:
            indicator_text = "Trading as: " + profile_name
        
        
        img = indicator.querySelector('img')
        if img:
            img.src = profile_image
            
        text = indicator.querySelector('span')
        if text:
            text.textContent = indicator_text
            
        console.log("Active profile indicator updated")
    except Exception as e:
        console.error(f"Error updating active profile indicator: {e}")
    
async def create_direct_trade_offer(event):
    try:
        
        icon = event.target
        receiver_item_id = icon.getAttribute('data-post-id')
        receiver_id = icon.getAttribute('data-user-id')
        item_name = icon.getAttribute('data-item-name')
        
        if not receiver_item_id or not receiver_id:
            console.error("Missing required data for creating trade offer")
            window.alert("Unable to create trade offer: Missing data")
            return
        
        console.log(f"Creating trade offer for item: {item_name} (ID: {receiver_item_id})")
        
        
        icon.className = 'fas fa-spinner fa-pulse'
        
        
        current_profile_id = localStorage.getItem("selectedProfileId")
        
        
        sender_item_id = current_profile_id
        
        
        response = await fetch(
            f"/get-item/{sender_item_id}",
            to_js({
                "method": "GET",
                "headers": {"Content-Type": "application/json"},
                "credentials": "include"
            })
        )
        
        
        sender_item = await response.json()
        sender_item = sender_item.to_py()  
        
        
        sender_id = sender_item['userID']
        
        if not current_profile_id:
            window.alert("Please select a profile before making a trade offer.")
            icon.className = 'fas fa-handshake'
            return
            
        
        my_items = await fetch_my_items()
        
        if not my_items or len(my_items) == 0:
            window.alert("You don't have any items to trade. Please add items first.")
            icon.className = 'fas fa-handshake'
            return
            
        trade_offer_data = {
            "sender_id": sender_id,  
            "receiver_id": receiver_id,
            "sender_item_id": sender_item_id,
            "receiver_item_id": receiver_item_id
        }
        
        console.log("Sending trade offer data:", json.dumps(trade_offer_data))
        Promise.resolve(to_js(call_backend(trade_offer_data))).catch(lambda e: console.error(f"Error: {e}"))
        console.log("kuy")
    except Exception as e:
        console.error(f"Error in create_direct_trade_offer: {e}")
        window.alert("An unexpected error occurred while creating the trade offer.")
    finally:
        
        icon.className = 'fas fa-handshake'
    

proxies = {}

async def call_backend(offer):
    
    show_notification("Processing your trade offer...", "info")
    
    headers = [["Content-Type", "application/json"]]
    response = await fetch("/create-offers",
                            method="POST",
                            body=json.dumps(offer),
                            headers=headers,
                            credentials="include")
    
    data = await response.json()
    console.log("Response:", data)
    console.log("kusy")
    
    if response.ok:
        show_notification("Trade offer created successfully!", "success")
    else:
        show_notification("Failed to create trade offer", "error")
    
    return data


def show_notification(message, type="info"):
    
    existing_notification = document.getElementById("trade-notification")
    if existing_notification:
        existing_notification.remove()
    
    
    notification = document.createElement("div")
    notification.id = "trade-notification"
    notification.className = f"notification {type}"
    
    
    icon = ""
    if type == "success":
        icon = '<i class="fas fa-check-circle"></i>'
    elif type == "error":
        icon = '<i class="fas fa-exclamation-circle"></i>'
    else:  
        icon = '<i class="fas fa-info-circle"></i>'
    
    
    notification.innerHTML = f"""
        <div class="notification-content">
            <div class="notification-icon">{icon}</div>
            <div class="notification-message">{message}</div>
            <div class="notification-close">×</div>
        </div>
    """
    
    
    notification.style.position = "fixed"
    notification.style.top = "20px"
    notification.style.right = "20px"
    notification.style.zIndex = "9999"
    notification.style.width = "300px"
    notification.style.padding = "15px"
    notification.style.borderRadius = "8px"
    notification.style.boxShadow = "0 4px 12px rgba(0, 0, 0, 0.15)"
    notification.style.animation = "slideIn 0.3s forwards"
    
    
    if type == "success":
        notification.style.backgroundColor = "#4CAF50"
    elif type == "error":
        notification.style.backgroundColor = "#F44336"
    else:
        notification.style.backgroundColor = "#2196F3"
    
    
    content = notification.querySelector(".notification-content")
    content.style.display = "flex"
    content.style.alignItems = "center"
    content.style.color = "white"
    
    
    icon_element = notification.querySelector(".notification-icon")
    icon_element.style.marginRight = "12px"
    icon_element.style.fontSize = "24px"
    
    
    message_element = notification.querySelector(".notification-message")
    message_element.style.flexGrow = "1"
    
    
    close_button = notification.querySelector(".notification-close")
    close_button.style.cursor = "pointer"
    close_button.style.fontSize = "20px"
    close_button.style.marginLeft = "12px"
    close_button.style.opacity = "0.7"
    close_button.style.transition = "opacity 0.2s"
    
    
    notification_id = f"notification_{id(notification)}"
    
    
    def on_close_hover(event):
        close_button.style.opacity = "1"
    
    def on_close_out(event):
        close_button.style.opacity = "0.7"
    
    def close_notification(event):
        notification.style.animation = "slideOut 0.3s forwards"
        
        
        add_slide_out_style()
        
        
        def remove_notification():
            notification.remove()
            
            for key in list(proxies.keys()):
                if key.startswith(notification_id):
                    del proxies[key]
        
        proxies[f"{notification_id}_remove"] = create_proxy(remove_notification)
        setTimeout(proxies[f"{notification_id}_remove"], 300)
    
    
    proxies[f"{notification_id}_hover"] = create_proxy(on_close_hover)
    proxies[f"{notification_id}_out"] = create_proxy(on_close_out)
    proxies[f"{notification_id}_close"] = create_proxy(close_notification)
    
    
    close_button.addEventListener("mouseover", proxies[f"{notification_id}_hover"])
    close_button.addEventListener("mouseout", proxies[f"{notification_id}_out"])
    close_button.addEventListener("click", proxies[f"{notification_id}_close"])
    
    
    document.body.appendChild(notification)
    
    
    add_slide_in_style()
    
    
    if type != "error":
        
        def auto_close():
            if document.getElementById("trade-notification") == notification:
                notification.style.animation = "slideOut 0.3s forwards"
                add_slide_out_style()
                
                
                def delayed_remove():
                    if document.body.contains(notification):
                        notification.remove()
                    
                    for key in list(proxies.keys()):
                        if key.startswith(notification_id):
                            del proxies[key]
                
                proxies[f"{notification_id}_delayed_remove"] = create_proxy(delayed_remove)
                setTimeout(proxies[f"{notification_id}_delayed_remove"], 300)
        
        proxies[f"{notification_id}_auto_close"] = create_proxy(auto_close)
        setTimeout(proxies[f"{notification_id}_auto_close"], 5000)

def add_slide_in_style():
    
    if not document.getElementById("notification-slide-in-style"):
        style = document.createElement("style")
        style.id = "notification-slide-in-style"
        style.textContent = """
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        """
        document.head.appendChild(style)

def add_slide_out_style():
    
    if not document.getElementById("notification-slide-out-style"):
        style = document.createElement("style")
        style.id = "notification-slide-out-style"
        style.textContent = """
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }
        """
        document.head.appendChild(style)

def auto_close_notification(notification):
    notification.style.animation = "slideOut 0.3s forwards"
    
    
    add_slide_out_style()
    
    
    setTimeout(lambda: notification.remove(), 300) 

async def create_direct_purchase_offer(event):
    try:
        
        icon = event.target
        item_id = icon.getAttribute('data-post-id')
        item_owner_id = icon.getAttribute('data-user-id')
        item_name = icon.getAttribute('data-item-name')
        
        if not item_id or not item_owner_id:
            console.error("Missing required data for creating purchase offer")
            window.alert("Unable to create purchase offer: Missing data")
            return
        
        console.log(f"Creating purchase offer forasdasd item: {item_name} (ID: {item_id})")
        
        
        icon.className = 'fas fa-spinner fa-pulse'
        
        
        headers = [["Content-Type", "application/json"]]
        status_response = await fetch(
            f"/purchase-offers/check-item/{item_id}",
            method="GET",
            headers=headers,
            credentials="include"
        )
        
        status_data = await status_response.json()
        
        
        if not status_data.available:
            window.alert(f"Item {item_name} is not available for purchase")
            icon.className = 'fas fa-shopping-cart'
            return
        
        
        purchase_offer_data = {
            "item_id": int(item_id)
        }
        
        
        headers = [["Content-Type", "application/json"]]
        response = await fetch("/purchase-offers/create",
                               method="POST",
                               body=json.dumps(purchase_offer_data),
                               headers=headers,
                               credentials="include")
        
        
        data = await response.json()
        
        
        if response.ok:
            show_notification(f"Purchase offer created for {item_name}", "success")
        else:
            show_notification(data.get('detail', 'Failed to create purchase offer'), "error")
        
    except Exception as e:
        console.error(f"Error in create_direct_purchase_offer: {e}")
        window.alert("An unexpected error occurred while creating the purchase offer.")
    finally:
        
        icon.className = 'fas fa-shopping-cart'


def create_offer_element(offer, offer_index, total_offers):
    try:
        
        if hasattr(offer, 'to_py'):
            offer = offer.to_py()
        
        
        if not isinstance(offer, dict):
            console.error(f"Invalid offer data: {offer}")
            return document.createElement('div')
        
        
        offer_div = document.createElement('div')
        offer_div.className = 'instagram-post offer-post'
        offer_div.id = f"offer-{offer.get('ID', 'unknown')}"
        offer_div.setAttribute('data-offer-index', str(offer_index))
        offer_div.setAttribute('data-total-offers', str(total_offers))
        
        
        
        offer_badge = document.createElement('div')
        offer_badge.className = 'offer-badge'
        offer_badge.innerHTML = '<i class="fas fa-tag"></i> Offer'
        offer_div.appendChild(offer_badge)
        
        
        post_header = document.createElement('div')
        post_header.className = 'post-header'
        
        profile_picture = document.createElement('img')
        profile_picture.className = 'profile-picture'
        profile_picture.src = "/static/image_test/profile_avatar.png"
        profile_picture.alt = offer.get('sender_username', 'User')
        
        username = document.createElement('div')
        username.className = 'post-username'
        username.textContent = offer.get('sender_username', 'User')
        
        post_header.appendChild(profile_picture)
        post_header.appendChild(username)
        
        
        image_container = document.createElement('div')
        image_container.className = 'post-image'
        
        image = document.createElement('img')
        image.src = offer.get('sender_item_image', '/static/image_test/default-item.jpg')
        image.alt = 'Item offered'
        
        image_container.appendChild(image)
        
        
        actions_container = document.createElement('div')
        actions_container.className = 'post-actions-container'
        
        action_buttons = document.createElement('div')
        action_buttons.className = 'action-buttons'
        
        heart_icon = document.createElement('i')
        heart_icon.className = 'far fa-heart'
        heart_icon.title = 'Like this offer'
        action_buttons.appendChild(heart_icon)
        
        
        actions_container.appendChild(action_buttons)
        
        
        
        content_div = document.createElement('div')
        content_div.className = 'post-content'
        
        
        offer_details = document.createElement('div')
        offer_details.className = 'item-price'
        offer_details.textContent = "Trade Offer"
        content_div.appendChild(offer_details)
        
        
        sender_item_name = document.createElement('div')
        sender_item_name.className = 'username'
        sender_item_name.textContent = offer.get('sender_item_name', 'Item for trade')
        content_div.appendChild(sender_item_name)
        
        
        wants_to_trade = document.createElement('div')
        wants_to_trade.className = 'caption'
        wants_to_trade.innerHTML = '<b>Wants to trade for:</b> ' + offer.get('receiver_item_name', 'Your item')
        content_div.appendChild(wants_to_trade)
        
        
        time_div = document.createElement('div')
        time_div.className = 'post-time'
        time_div.textContent = offer.get('created_at', 'Recently')
        content_div.appendChild(time_div)
        
        
        offer_actions = document.createElement('div')
        offer_actions.className = 'offer-actions'
        
        reject_button = document.createElement('button')
        reject_button.className = 'offer-button reject-button'
        reject_button.innerHTML = '<i class="fas fa-times"></i> Reject'
        reject_button.onclick = create_proxy(lambda e: handle_offer_response(offer['ID'], 'reject'))
        
        accept_button = document.createElement('button')
        accept_button.className = 'offer-button accept-button'
        accept_button.innerHTML = '<i class="fas fa-check"></i> Accept'
        accept_button.onclick = create_proxy(lambda e: handle_offer_response(offer['ID'], 'accept'))
        
        offer_actions.appendChild(reject_button)
        offer_actions.appendChild(accept_button)
        
        
        offer_div.appendChild(post_header)
        offer_div.appendChild(image_container)
        offer_div.appendChild(actions_container)
        offer_div.appendChild(content_div)
        offer_div.appendChild(offer_actions)
        
        return offer_div
    except Exception as e:
        console.error(f"Error creating offer element: {e}")
        return document.createElement('div')

def toggle_like(event):
    try:
        icon = event.target
        item_id = icon.getAttribute('data-post-id')

        if 'far' in icon.className:
            icon.className = 'fas fa-heart'
            icon.style.color = '#ed4956'
            console.log(f"Item ID: {item_id} liked")
            Promise.resolve(add_to_wishlist(item_id))
        else:
            icon.className = 'far fa-heart'
            icon.style.color = '#000'
            console.log(f"Item ID: {item_id} removed from like")
            Promise.resolve(remove_from_wishlist(item_id))
        
    except Exception as e:
        console.error(f"Error toggling like: {e}")

async def add_to_wishlist(item_id):
    try:
        headers = [["Content-Type", "application/json"]]
        response = await fetch(f"/add_wishlist/{item_id}",
                               method="POST",
                               headers=headers,
                               credentials="include")
    
    except Exception as e:
        console.error(f"Error adding item to wishlist: {e}")

async def remove_from_wishlist(item_id):
    try:
        headers = [["Content-Type", "application/json"]]
        response = await fetch(f"/remove_wishlist/{item_id}",
                               method="DELETE",
                               headers=headers,
                               credentials="include")
    
    except Exception as e:
        console.error(f"Error removing item from wishlist: {e}")
    


def handle_offer_response(offer_id, response):
    try:
        console.log(f"Handling offer response: {response} for offer ID: {offer_id}")
        
        offer_element = document.getElementById(f"offer-{offer_id}")
        if not offer_element:
            console.error(f"Offer element with ID {offer_id} not found")
            return
            
        
        offer_index = int(offer_element.getAttribute('data-offer-index'))
        total_offers = int(offer_element.getAttribute('data-total-offers'))
        
        console.log(f"Offer index: {offer_index}, Total offers: {total_offers}")
        
        
        offer_actions = offer_element.querySelector('.offer-actions')
        if offer_actions:
            offer_actions.remove()
            console.log("Removed offer action buttons")
        
        
        if response == 'accept':
            console.log("Accepting offer...")
            
            Promise.resolve(accept_trade_offer(offer_id))
            
            
            status_div = document.createElement('div')
            status_div.className = 'offer-status'
            status_div.textContent = "Offer accepted! Processing trade..."
            status_div.style.color = '#4caf50'
            offer_element.style.borderColor = '#4caf50'
            offer_element.appendChild(status_div)
        else:
            console.log("Rejecting offer...")
            
            Promise.resolve(reject_trade_offer(offer_id))
            
            
            offer_element.style.opacity = '0.5'
            offer_element.style.transition = 'opacity 0.5s ease, transform 0.5s ease'
            offer_element.style.transform = 'translateX(100px)'
        
        
        console.log("Setting timeout to load next offer...")
        window.setTimeout(create_proxy(lambda: load_next_offer(offer_index, total_offers)), 1000)
        
    except Exception as e:
        console.error(f"Error handling offer response: {e}")

async def accept_trade_offer(offer_id):
    try:
        headers = [["Content-Type", "application/json"]]
        response = await fetch(f"/trade-offers/{offer_id}/accept",
                              method="PUT",
                              headers=headers,
                              credentials="include")
        
        if response.ok:
            console.log(f"Successfully accepted offer {offer_id}")
        else:
            console.error(f"Failed to accept offer {offer_id}")
    except Exception as e:
        console.error(f"Error accepting offer: {e}")

async def reject_trade_offer(offer_id):
    try:
        headers = [["Content-Type", "application/json"]]
        response = await fetch(f"/trade-offers/{offer_id}/reject",
                              method="DELETE",
                              headers=headers,
                              credentials="include")
        
        if response.ok:
            console.log(f"Successfully rejected offer {offer_id}")
        else:
            console.error(f"Failed to reject offer {offer_id}")
    except Exception as e:
        console.error(f"Error rejecting offer: {e}")

def load_next_offer(current_index, total_offers):
    try:
        console.log(f"Loading next offer after index {current_index}. Total offers: {total_offers}")
        
        
        container = document.getElementById('instagram-feed-container')
        current_offer = container.querySelector(f'[data-offer-index="{current_index}"]')
        if current_offer:
            current_offer.remove()
            console.log("Removed current offer")
        else:
            console.log("Could not find current offer to remove")
            
        
        if not hasattr(window, 'remainingOffers'):
            console.error("window.remainingOffers is not defined")
            window.remainingOffers = []
            
        
        console.log(f"Remaining offers count: {len(window.remainingOffers) if hasattr(window.remainingOffers, '__len__') else 'unknown'}")
            
        
        if window.remainingOffers and len(window.remainingOffers) > 0:
            console.log("Found remaining offers, processing next one")
            
            
            next_offer = window.remainingOffers.pop(0)
            next_index = current_index + 1
            
            console.log(f"Creating next offer element with index {next_index}")
            
            
            next_offer_element = create_offer_element(next_offer, next_index, total_offers)
            
            
            counter = container.querySelector('.offer-counter')
            if counter:
                
                container.insertBefore(next_offer_element, counter.nextSibling)
                console.log("Inserted next offer after counter")
            else:
                console.log("No counter found, appending to container")
                container.appendChild(next_offer_element)
                
            
            offers_left = len(window.remainingOffers)
            
            console.log(f"Updated counter toasdasdad {offers_left + 1} offers")
        else:
            console.log("No more offers remaining")
            
            
    except Exception as e:
        console.error(f"Error loading next offer: {e}")




async def load_posts_with_offers():
    try:
        # Fetch both posts and offers concurrently
        posts_promise = fetch_posts()
        offers_promise = fetch_trade_offers()
        
        # Wait for both requests to complete
        posts, offers = await asyncio.gather(posts_promise, offers_promise)
        
        # Convert objects if needed
        if offers and hasattr(offers, 'to_py'):
            offers = offers.to_py()
        
        # Get the container element
        container = document.getElementById('instagram-feed-container')
        
        # Process the data if container exists
        if container:
            container.innerHTML = ''
            
            # Create the offer counter
            offer_counter = document.createElement('div')
            offer_counter.className = 'offer-counter'
            offer_counter.style.color = None
            # Process offers if they exist
            if offers and len(offers) > 0:
                # Convert to list if not already
                if not isinstance(offers, list):
                    offers = list(offers)
                
                # Update counter text

                
                
                # Add counter to container first
                container.appendChild(offer_counter)
                
                # Add only the first offer
                first_offer = offers[0]
                first_offer_element = create_offer_element(first_offer, 0, len(offers))
                container.appendChild(first_offer_element)
                
                # Save remaining offers for later
                window.remainingOffers = offers[1:] if len(offers) > 1 else []
                
            else:
                # No offers available

                container.appendChild(offer_counter)
            
            # Now add all posts AFTER the offers section
            if posts:
                if hasattr(posts, 'to_py'):
                    posts = posts.to_py()
                
                for post in posts:
                    post_element = create_post_element(post)
                    container.appendChild(post_element)
            
            # Show a message if no content is available
            if not posts and not offers:
                container.innerHTML += '<div class="no-results">No posts or offers available</div>'
        else:
            console.error("Container element not found")
            
    except Exception as e:
        console.error(f"Error loading posts and offers: {e}")


def run_async(async_func):
    Promise.resolve(to_js(async_func())).catch(lambda e: console.error(f"Error: {e}"))

def add_scroll_to_top_button():
    try:
        container = document.getElementById('instagram-feed-container')
        if not container:
            return
            
        
        button = document.createElement('button')
        button.id = 'scroll-to-top'
        button.innerHTML = '&#8679;'
        button.style.position = 'fixed'
        button.style.bottom = '20px'
        button.style.right = '20px'
        button.style.zIndex = '1000'
        button.style.display = 'none'
        button.style.padding = '10px 15px'
        button.style.backgroundColor = '#0095f6'
        button.style.color = 'white'
        button.style.border = 'none'
        button.style.borderRadius = '50%'
        button.style.cursor = 'pointer'
        button.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)'
        
        button.onclick = create_proxy(lambda event: container.scrollTo({
            'top': 0,
            'behavior': 'smooth'
        }))
        
        def check_scroll_position(event):
            if container.scrollTop > 300:
                button.style.display = 'block'
            else:
                button.style.display = 'none'
        
        container.addEventListener('scroll', create_proxy(check_scroll_position))
        
        document.body.appendChild(button)
    except Exception as e:
        console.error(f"Error adding scroll button: {e}")


def setup():
    console.log("Setting up trading feed with offers...")
    
    if not document.querySelector('link[href*="font-awesome"]'):
        link = document.createElement('link')
        link.rel = 'stylesheet'
        link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css'
        document.head.appendChild(link)
    
    
    run_async(load_posts_with_offers)
    
    
    add_scroll_to_top_button()


setup()