from pyscript import when
import pyodide.http
import json
from pyodide.ffi import create_proxy, to_js
from js import document, console, fetch, window, Promise
import asyncio

# ฟังก์ชันเดิมสำหรับดึงข้อมูลโพสต์ทั่วไป
async def fetch_posts():
    try:
        console.log("Fetching posts from backend...")

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

# ฟังก์ชันใหม่สำหรับดึงข้อมูล trade offers จากฐานข้อมูล
async def fetch_trade_offers():
    try:
        console.log("Fetching trade offers...")

        response = await fetch(
            "/get-trade-offers",  # สร้าง API endpoint นี้ในฝั่ง backend
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
            heart_icon.style.color = '#ed4956'  # Red for liked
        else:
            heart_icon.className = 'far fa-heart'
            heart_icon.style.color = '#000'  # Black for not liked

    except Exception as e:
        console.error(f"Error checking wishlist status: {e}")

# ฟังก์ชันเดิมสำหรับสร้าง post element
def create_post_element(post):
    try:
        if hasattr(post, 'to_py'):
            post = post.to_py()
        
        post_div = document.createElement('div')
        post_div.className = 'instagram-post'
        post_div.id = f"post-{post['zodb_id']}"
        post_div.setAttribute('data-username', post['username'])
        
        # 1. Post header with username
        post_header = document.createElement('div')
        post_header.className = 'post-header'
        
        # Profile picture
        profile_picture = document.createElement('img')
        profile_picture.className = 'profile-picture'
        profile_picture.src = "/static/image_test/profile_default.jpg"
        profile_picture.alt = post['username']
        
        # Username
        post_username = document.createElement('div')
        post_username.className = 'post-username'
        post_username.textContent = post['username']
        
        # Add elements to header
        post_header.appendChild(profile_picture)
        post_header.appendChild(post_username)
        
        # 2. Post image
        post_image = document.createElement('div')
        post_image.className = 'post-image'
        image = document.createElement('img')
        image.src = post['image']
        image.alt = 'Item for trade'
        post_image.appendChild(image)
        
        # 3. Action buttons container - heart and bookmark icons
        actions_container = document.createElement('div')
        actions_container.className = 'post-actions-container'
        
        # Heart button container
        action_buttons = document.createElement('div')
        action_buttons.className = 'action-buttons'
        
        # Heart icon
        heart_icon = document.createElement('i')
        heart_icon.className = 'far fa-heart'
        heart_icon.title = 'Interested in trading'
        heart_icon.setAttribute('data-post-id', str(post['zodb_id']))
        heart_icon.onclick = create_proxy(lambda event: toggle_like(event))
        action_buttons.appendChild(heart_icon)
        
        Promise.resolve(check_wishlist_status(post['zodb_id'], heart_icon))
        
        # Bookmark container
        bookmark = document.createElement('div')
        bookmark.className = 'bookmark'
        
        # Bookmark icon
        bookmark_icon = document.createElement('i')
        bookmark_icon.className = 'far fa-bookmark'
        bookmark_icon.title = 'Save for later'
        bookmark_icon.onclick = create_proxy(lambda event: toggle_bookmark(event))
        bookmark.appendChild(bookmark_icon)
        
        # Add buttons to container
        actions_container.appendChild(action_buttons)
        actions_container.appendChild(bookmark)
        
        # 4. Content section
        content_div = document.createElement('div')
        content_div.className = 'post-content'
        
        # Item price
        price_div = document.createElement('div')
        price_div.className = 'item-price'
        price_div.textContent = f"Price: {post['price']}"
        content_div.appendChild(price_div)
        
        # Item name and description
        user_caption = document.createElement('div')
        user_caption.className = 'user-caption'
        
        # Username with item name (similar to Instagram caption format)
        caption_container = document.createElement('div')
        caption_container.className = 'caption'
        
        username_span = document.createElement('span')
        username_span.className = 'username'
        username_span.textContent = post['username'] + " "
        
        item_name = document.createElement('span')
        item_name.textContent = post['name']
        
        caption_container.appendChild(username_span)
        caption_container.appendChild(item_name)
        user_caption.appendChild(caption_container)
        content_div.appendChild(user_caption)
        
        description_div = document.createElement('div')
        description_div.className = 'item-description'
        description_div.textContent = post['description']
        content_div.appendChild(description_div)
        
        # Assemble the post
        post_div.appendChild(post_header)
        post_div.appendChild(post_image)
        post_div.appendChild(actions_container)
        post_div.appendChild(content_div)
        
        return post_div
    except Exception as e:
        console.error(f"Error creating post element: {e}")
        return document.createElement('div')

# ฟังก์ชันใหม่สำหรับสร้าง trade offer element
def create_offer_element(offer, offer_index, total_offers):
    try:
        # แปลง offer เป็น dictionary ถ้ามันเป็น PyProxy
        if hasattr(offer, 'to_py'):
            offer = offer.to_py()
        
        # ตรวจสอบว่า offer เป็น dictionary ที่ถูกต้อง
        if not isinstance(offer, dict):
            console.error(f"Invalid offer data: {offer}")
            return document.createElement('div')
        
        # สร้าง container หลัก
        offer_div = document.createElement('div')
        offer_div.className = 'instagram-post offer-post'
        offer_div.id = f"offer-{offer.get('ID', 'unknown')}"
        offer_div.setAttribute('data-offer-index', str(offer_index))
        offer_div.setAttribute('data-total-offers', str(total_offers))
        
        # ส่วนที่เหลือของฟังก์ชันเหมือนเดิม...
        # เพิ่มป้าย Offer
        offer_badge = document.createElement('div')
        offer_badge.className = 'offer-badge'
        offer_badge.innerHTML = '<i class="fas fa-tag"></i> Offer'
        offer_div.appendChild(offer_badge)
        
        # ส่วนหัวของโพสต์แสดงชื่อผู้ส่ง offer
        post_header = document.createElement('div')
        post_header.className = 'post-header'
        
        profile_picture = document.createElement('img')
        profile_picture.className = 'profile-picture'
        profile_picture.src = "/static/image_test/profile_default.jpg"
        profile_picture.alt = offer.get('sender_username', 'User')
        
        username = document.createElement('div')
        username.className = 'post-username'
        username.textContent = offer.get('sender_username', 'User')
        
        post_header.appendChild(profile_picture)
        post_header.appendChild(username)
        
        # ส่วนรูปภาพสินค้าที่เสนอให้แลกเปลี่ยน
        image_container = document.createElement('div')
        image_container.className = 'post-image'
        
        image = document.createElement('img')
        image.src = offer.get('sender_item_image', '/static/image_test/default-item.jpg')
        image.alt = 'Item offered'
        
        image_container.appendChild(image)
        
        # ส่วนปุ่มแอ็คชั่น
        actions_container = document.createElement('div')
        actions_container.className = 'post-actions-container'
        
        action_buttons = document.createElement('div')
        action_buttons.className = 'action-buttons'
        
        heart_icon = document.createElement('i')
        heart_icon.className = 'far fa-heart'
        heart_icon.title = 'Like this offer'
        action_buttons.appendChild(heart_icon)
        
        bookmark = document.createElement('div')
        bookmark.className = 'bookmark'
        
        bookmark_icon = document.createElement('i')
        bookmark_icon.className = 'far fa-bookmark'
        bookmark_icon.title = 'Save this offer'
        bookmark.appendChild(bookmark_icon)
        
        actions_container.appendChild(action_buttons)
        actions_container.appendChild(bookmark)
        
        # ส่วนเนื้อหาของ offer
        content_div = document.createElement('div')
        content_div.className = 'post-content'
        
        # รายละเอียด offer
        offer_details = document.createElement('div')
        offer_details.className = 'item-price'
        offer_details.textContent = "Trade Offer"
        content_div.appendChild(offer_details)
        
        # รายละเอียดของสินค้าที่เสนอ
        sender_item_name = document.createElement('div')
        sender_item_name.className = 'username'
        sender_item_name.textContent = offer.get('sender_item_name', 'Item for trade')
        content_div.appendChild(sender_item_name)
        
        # สิ่งที่ต้องการแลกเปลี่ยน
        wants_to_trade = document.createElement('div')
        wants_to_trade.className = 'caption'
        wants_to_trade.innerHTML = '<b>Wants to trade for:</b> ' + offer.get('receiver_item_name', 'Your item')
        content_div.appendChild(wants_to_trade)
        
        # เวลาที่สร้าง offer
        time_div = document.createElement('div')
        time_div.className = 'post-time'
        time_div.textContent = offer.get('created_at', 'Recently')
        content_div.appendChild(time_div)
        
        # ส่วนปุ่มสำหรับตอบรับหรือปฏิเสธ offer
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
        
        # ประกอบส่วนต่างๆ เข้าด้วยกัน
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
    
def toggle_bookmark(event):
    try:
        icon = event.target
        
        if 'far' in icon.className:
            icon.className = 'fas fa-bookmark'
            icon.style.color = '#ffcc00'
        else:
            icon.className = 'far fa-bookmark'
            icon.style.color = '#000'
    except Exception as e:
        console.error(f"Error toggling bookmark: {e}")

def handle_offer_response(offer_id, response):
    try:
        console.log(f"Handling offer response: {response} for offer ID: {offer_id}")
        
        offer_element = document.getElementById(f"offer-{offer_id}")
        if not offer_element:
            console.error(f"Offer element with ID {offer_id} not found")
            return
            
        # ดึงข้อมูล index และจำนวน offers ทั้งหมด
        offer_index = int(offer_element.getAttribute('data-offer-index'))
        total_offers = int(offer_element.getAttribute('data-total-offers'))
        
        console.log(f"Offer index: {offer_index}, Total offers: {total_offers}")
        
        # ลบปุ่มที่ใช้ตอบรับหรือปฏิเสธ offer
        offer_actions = offer_element.querySelector('.offer-actions')
        if offer_actions:
            offer_actions.remove()
            console.log("Removed offer action buttons")
        
        # ส่งคำขอ API ไปยัง backend
        if response == 'accept':
            console.log("Accepting offer...")
            # ส่งคำขอยอมรับ offer
            Promise.resolve(accept_trade_offer(offer_id))
            
            # แสดงข้อความยอมรับ
            status_div = document.createElement('div')
            status_div.className = 'offer-status'
            status_div.textContent = "Offer accepted! Processing trade..."
            status_div.style.color = '#4caf50'
            offer_element.style.borderColor = '#4caf50'
            offer_element.appendChild(status_div)
        else:
            console.log("Rejecting offer...")
            # ส่งคำขอปฏิเสธ offer
            Promise.resolve(reject_trade_offer(offer_id))
            
            # แสดงการปฏิเสธด้วย animation
            offer_element.style.opacity = '0.5'
            offer_element.style.transition = 'opacity 0.5s ease, transform 0.5s ease'
            offer_element.style.transform = 'translateX(100px)'
        
        # โหลด offer ถัดไป (ถ้ามี) หลังจากดำเนินการ
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
        
        # ลบ offer ปัจจุบัน
        container = document.getElementById('instagram-feed-container')
        current_offer = container.querySelector(f'[data-offer-index="{current_index}"]')
        if current_offer:
            current_offer.remove()
            console.log("Removed current offer")
        else:
            console.log("Could not find current offer to remove")
            
        # ตรวจสอบว่า window.remainingOffers มีอยู่จริงและเป็น list
        if not hasattr(window, 'remainingOffers'):
            console.error("window.remainingOffers is not defined")
            window.remainingOffers = []
            
        # แสดงข้อมูลการดีบัก
        console.log(f"Remaining offers count: {len(window.remainingOffers) if hasattr(window.remainingOffers, '__len__') else 'unknown'}")
            
        # ตรวจสอบว่ามี offer เพิ่มเติมหรือไม่
        if window.remainingOffers and len(window.remainingOffers) > 0:
            console.log("Found remaining offers, processing next one")
            
            # ดึง offer ถัดไป
            next_offer = window.remainingOffers.pop(0)
            next_index = current_index + 1
            
            console.log(f"Creating next offer element with index {next_index}")
            
            # สร้างและเพิ่ม offer ถัดไป
            next_offer_element = create_offer_element(next_offer, next_index, total_offers)
            
            # ค้นหาตำแหน่งที่จะแทรก (หลังจาก offer-counter)
            counter = container.querySelector('.offer-counter')
            if counter:
                # แทรกหลัง counter ไม่ว่ามี element ถัดไปหรือไม่
                container.insertBefore(next_offer_element, counter.nextSibling)
                console.log("Inserted next offer after counter")
            else:
                console.log("No counter found, appending to container")
                container.appendChild(next_offer_element)
                
            # อัพเดตตัวนับจำนวน offer
            offers_left = len(window.remainingOffers)
            update_offer_counter(offers_left + 1)  # +1 เพราะกำลังแสดงอีก 1 รายการ
            console.log(f"Updated counter toasdasdad {offers_left + 1} offers")
        else:
            console.log("No more offers remaining")
            # ไม่มี offer เพิ่มเติม อัพเดตตัวนับเป็น 0
            update_offer_counter(0)
    except Exception as e:
        console.error(f"Error loading next offer: {e}")
        # พยายามอัพเดตตัวนับให้เป็น 0 เพื่อความปลอดภัย
        try:
            update_offer_counter(0)
        except:
            pass

def update_offer_counter(count):
    try:
        counter = document.querySelector('.offer-counter')
        if counter:
            if count > 0:
                counter.textContent = f"{count} offer{'s' if count > 1 else ''} available"
                counter.style.backgroundColor = 'rgba(255, 215, 0, 0.9)'
                counter.style.color = '#000'
            else:
                # แสดง "0 offer available" แทน "No more offers available"
                counter.textContent = "0 offer available"
                counter.style.backgroundColor = 'rgba(128, 128, 128, 0.2)'
                counter.style.color = '#555'
    except Exception as e:
        console.error(f"Error updating offer counter: {e}")

async def load_posts_with_offers():
    try:
        # ดึงข้อมูลทั้ง posts และ offers
        posts_promise = fetch_posts()
        offers_promise = fetch_trade_offers()
        
        # รอให้ทั้งสองคำขอเสร็จสิ้น
        posts, offers = await asyncio.gather(posts_promise, offers_promise)
        
        # แปลง offers เป็น list ถ้าจำเป็น
        if offers and hasattr(offers, 'to_py'):
            offers = offers.to_py()
        
        # ดึง container
        container = document.getElementById('instagram-feed-container')
        
        # ล้างเนื้อหาเดิม
        if container:
            container.innerHTML = ''
            
            # สร้างตัวนับจำนวน offer (แสดงทุกกรณี)
            offer_counter = document.createElement('div')
            offer_counter.className = 'offer-counter'
            
            # ตรวจสอบว่ามี offers หรือไม่
            if offers and len(offers) > 0:
                # แปลง offers เป็น list ถ้ายังไม่ได้ทำ
                if not isinstance(offers, list):
                    offers = list(offers)
                
                offer_counter.textContent = f"{len(offers)} offer{'s' if len(offers) > 1 else ''} available"
                offer_counter.style.backgroundColor = 'rgba(255, 215, 0, 0.9)'
                offer_counter.style.color = '#000'
                
                # แสดง offer แรก
                first_offer = offers[0]
                first_offer_element = create_offer_element(first_offer, 0, len(offers))
                
                # เก็บ offers ที่เหลือไว้ใน window
                window.remainingOffers = offers[1:] if len(offers) > 1 else []
                
                # เพิ่มตัวนับ offer ไปที่ container
                container.appendChild(offer_counter)
                
                # เพิ่ม offer แรก
                container.appendChild(first_offer_element)
            else:
                # แสดง "0 offer" เมื่อไม่มี offer
                offer_counter.textContent = "0 offer available"
                offer_counter.style.backgroundColor = 'rgba(128, 128, 128, 0.2)'
                offer_counter.style.color = '#555'
                container.appendChild(offer_counter)
            
            # เพิ่ม posts
            if posts:
                if hasattr(posts, 'to_py'):
                    posts = posts.to_py()
                
                for post in posts:
                    post_element = create_post_element(post)
                    container.appendChild(post_element)
            
            if not posts and not offers:
                container.innerHTML += '<div class="no-results">No posts or offers available</div>'
        else:
            console.error("Container element not found")
            
    except Exception as e:
        console.error(f"Error loading posts and offers: {e}")

# Function to run async function properly
def run_async(async_func):
    Promise.resolve(to_js(async_func())).catch(lambda e: console.error(f"Error: {e}"))

def add_scroll_to_top_button():
    try:
        container = document.getElementById('instagram-feed-container')
        if not container:
            return
            
        # Create scroll to top button
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

# Initialize when the page loads
def setup():
    console.log("Setting up trading feed with offers...")
    # ตรวจสอบว่ามี FontAwesome หรือไม่ ถ้าไม่มีให้เพิ่ม
    if not document.querySelector('link[href*="font-awesome"]'):
        link = document.createElement('link')
        link.rel = 'stylesheet'
        link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css'
        document.head.appendChild(link)
    
    # โหลด posts และ offers
    run_async(load_posts_with_offers)
    
    # เพิ่มปุ่ม scroll to top
    add_scroll_to_top_button()

# Run setup when the script is loaded
setup()