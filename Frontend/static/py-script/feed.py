from pyscript import when
import pyodide.http
import json
from pyodide.ffi import create_proxy, to_js
from js import document, console, fetch, window, Promise
import asyncio

async def fetch_posts():
    try:
        console.log("Fetching posts from backend...")

        response = await fetch(
            "/get-all-posts",  # Ensure this is correct
            to_js({
                "method": "GET",
                "headers": {"Content-Type": "application/json"},
                "credentials": "include"  # Important for handling session cookies
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

async def check_wishlist_status(item_id, heart_icon):
    try:

        headers = [["Content-Type", "application/json"]]
        response = await fetch(f"/status_wishlist/{item_id}",
                               method="GET",
                               headers=headers,
                               credentials="include")
        if not response.ok:
            print("Failed to fetch wishlist status")
            return
        
        data = await response.json()  # Convert response to JSON

        if data:
            heart_icon.className = 'fas fa-heart'
            heart_icon.style.color = '#ed4956'  # Red for liked
        else:
            heart_icon.className = 'far fa-heart'
            heart_icon.style.color = '#000'  # Black for not liked

    except Exception as e:
        print(f"Error checking wishlist status: {e}")

def create_post_element(post):
    try:
        post = post.to_py()
        
        post_div = document.createElement('div')
        post_div.className = 'instagram-post'
        post_div.id = f"post-{post['zodb_id']}"
        
        # 1. Post image
        post_image = document.createElement('div')
        post_image.className = 'post-image'
        image = document.createElement('img')
        image.src = post['image']  # Use the base64 image string from the ZODB data
        image.alt = 'Item for trade'
        post_image.appendChild(image)
        
        # 2. Action buttons container - heart and bookmark icons
        actions_container = document.createElement('div')
        actions_container.className = 'post-actions-container'
        
        # Heart button container
        action_buttons = document.createElement('div')
        action_buttons.className = 'action-buttons'
        
        # Heart icon
        heart_icon = document.createElement('i')
        heart_icon.className = 'far fa-heart'
        heart_icon.title = 'Interested in trading'
        heart_icon.setAttribute('data-post-id', str(post['ID']))
        heart_icon.onclick = create_proxy(lambda event: toggle_like(event))
        action_buttons.appendChild(heart_icon)
        
        Promise.resolve(check_wishlist_status(post['ID'], heart_icon))
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
        
        # 3. Content section
        content_div = document.createElement('div')
        content_div.className = 'post-content'
        
        # Item price
        price_div = document.createElement('div')
        price_div.className = 'item-price'
        price_div.textContent = f"Price: {post['price']}"  # Adding "Price:" for clarity
        content_div.appendChild(price_div)
        
        # Category and description

        user_caption = document.createElement('div')
        user_caption.className = 'user-caption'
        username = document.createElement('div')
        username.className = 'item_name'
        username.textContent = post['name']
        user_caption.appendChild(username)
        
        content_div.appendChild(user_caption)

        
        description_div = document.createElement('div')
        description_div.className = 'item-description'
        description_div.textContent = f"{post['description']}"
        content_div.appendChild(description_div)
        
        post_div.appendChild(post_image)
        post_div.appendChild(actions_container)
        post_div.appendChild(content_div)
        
        return post_div
    except Exception as e:
        console.error(f"Error creating post element: {e}")
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
        # payload = {"item_id": item_id}
        response = await fetch(f"/add_wishlist/{item_id}",
                               method="POST",
                            #    body=json.dumps(payload),
                               headers=headers,
                               credentials="include")

        # try:
        #     response_json = await response.json()
        #     console.log(response_json.get("message", "Item added to wishlist"))
        # except Exception as e:
        #     console.error(f"Error parsing response as JSON: {e}")
    
    except Exception as e:
        console.error(f"Error adding item to wishlist: {e}")

async def remove_from_wishlist(item_id):
    try:

        headers = [["Content-Type", "application/json"]]
        response = await fetch(f"/remove_wishlist/{item_id}",
                               method="DELETE",
                               headers=headers,
                               credentials="include")

        # url = f'/wishlist/{item_id}'
        # response = await fetch(url, {
        #     "method": 'DELETE',
        #     "headers": {"Content-Type": "application/json"}
        # })
        # Try to parse the response as JSON
        # try:
        #     response_json = await response.json()
        #     console.log(response_json.get("message", "Item removed from wishlist"))
        # except Exception as e:
        #     console.error(f"Error parsing response as JSON: {e}")
    
    except Exception as e:
        console.error(f"Error removing item from wishlist: {e}")
    
def toggle_bookmark(event):
    """Toggle bookmark icon between outline and solid"""
    try:
        icon = event.target
        
        if 'far' in icon.className:
            # Save - switch to solid yellow bookmark
            icon.className = 'fas fa-bookmark'
            icon.style.color = '#ffcc00'  # Bright yellow
        else:
            # Unsave - switch to outline bookmark
            icon.className = 'far fa-bookmark'
            icon.style.color = '#000'  # Black color
    except Exception as e:
        console.error(f"Error toggling bookmark: {e}")

async def load_posts():
    try:
        posts = await fetch_posts()
        
        # Get the container element
        container = document.getElementById('instagram-feed-container')
        
        # Clear existing content
        if container:
            container.innerHTML = ''
            
            # Add each post to the container
            for post in posts:
                post_element = create_post_element(post)
                container.appendChild(post_element)
        else:
            console.error("Container element not found")
            
    except Exception as e:
        console.error(f"Error loading posts: {e}")

# Properly handle the asynchronous function
# Function to run async function properly
def run_async(async_func):
    Promise.resolve(to_js(async_func())).catch(lambda e: console.error(f"Error: {e}"))

# Initialize when the page loads
def setup():
    """Initialize the trading feed"""
    console.log("Setting up trading feed...")
    # Properly await the async function
    run_async(load_posts)
    
    # Add scroll to top button
    add_scroll_to_top_button()

def add_scroll_to_top_button():
    """Add a button to scroll back to top of feed"""
    try:
        container = document.getElementById('instagram-feed-container')
        if not container:
            return
            
        # Create scroll to top button
        button = document.createElement('button')
        button.id = 'scroll-to-top'
        button.innerHTML = '&#8679;' # Up arrow
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
        
        # Add click event
        button.onclick = create_proxy(lambda event: container.scrollTo({
            'top': 0,
            'behavior': 'smooth'
        }))
        
        # Show/hide based on scroll position
        def check_scroll_position(event):
            if container.scrollTop > 300:
                button.style.display = 'block'
            else:
                button.style.display = 'none'
        
        container.addEventListener('scroll', create_proxy(check_scroll_position))
        
        # Add button to document
        document.body.appendChild(button)
    except Exception as e:
        console.error(f"Error adding scroll button: {e}")

# Run setup when the script is loaded
setup()