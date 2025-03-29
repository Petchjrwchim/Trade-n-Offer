# instagram_feed-script.py (modified version)
import json
from pyodide.ffi import create_proxy
from js import document, console, fetch, window

# Sample data with trading items
SAMPLE_POSTS = [
    {
        "id": 1,
        "username": "camera_lover",
        "image_url": "/static/image_test/camera.jpg",
        "caption": "Vintage camera in excellent condition. Looking to trade for audio equipment.",
        "price": "$120 or trade",
        "location": "Bangkok",
        "posted_time": "2d",
        "liked": False,
        "bookmarked": False
    },
    {
        "id": 2,
        "username": "music_shop",
        "image_url": "/static/image_test/guitar.jpg",
        "caption": "Acoustic guitar with case. Great sound, barely used. Open to trades for other instruments.",
        "price": "$250 or trade",
        "location": "Chiang Mai",
        "posted_time": "5h",
        "liked": False,
        "bookmarked": False
    },
    {
        "id": 3,
        "username": "instrument_trader",
        "image_url": "/static/image_test/piano.jpg",
        "caption": "Digital piano with weighted keys. Perfect condition. Would trade for guitar equipment.",
        "price": "$350 or trade",
        "location": "Phuket",
        "posted_time": "1d",
        "liked": False,
        "bookmarked": False
    }
]

# Dictionary to store proxies
proxies = {}

async def fetch_posts():
    """
    Fetch posts from an API endpoint or use sample data
    In a real app, you might make an API call here
    """
    try:
        # For now, use sample data
        return SAMPLE_POSTS
    except Exception as e:
        console.error(f"Error fetching posts: {e}")
        return []

def toggle_like(event):
    """Toggle heart icon between outline and solid"""
    try:
        icon = event.target
        post_id = int(icon.getAttribute("data-post-id"))
        
        # Find the post and toggle its liked status
        post = next((p for p in SAMPLE_POSTS if p["id"] == post_id), None)
        if post:
            post["liked"] = not post["liked"]
            
            if post["liked"]:
                # Like - switch to solid red heart
                icon.className = "fas fa-heart"
                icon.style.color = "#ed4956"  # Instagram red
            else:
                # Unlike - switch to outline heart
                icon.className = "far fa-heart"
                icon.style.color = "#000"  # Black color
    except Exception as e:
        console.error(f"Error toggling like: {e}")

def toggle_bookmark(event):
    """Toggle bookmark icon between outline and solid"""
    try:
        icon = event.target
        post_id = int(icon.getAttribute("data-post-id"))
        
        # Find the post and toggle its bookmarked status
        post = next((p for p in SAMPLE_POSTS if p["id"] == post_id), None)
        if post:
            post["bookmarked"] = not post["bookmarked"]
            
            if post["bookmarked"]:
                # Save - switch to solid yellow bookmark
                icon.className = "fas fa-bookmark"
                icon.style.color = "#ffcc00"  # Bright yellow
            else:
                # Unsave - switch to outline bookmark
                icon.className = "far fa-bookmark"
                icon.style.color = "#000"  # Black color
    except Exception as e:
        console.error(f"Error toggling bookmark: {e}")

def handle_double_click(event):
    """Handle double-click on post image to toggle like/unlike"""
    try:
        # Get the post-image container
        post_image = event.currentTarget
        post_id = int(post_image.getAttribute("data-post-id"))
        
        # Find the post
        post = next((p for p in SAMPLE_POSTS if p["id"] == post_id), None)
        if not post:
            return
        
        # Find the heart icon in the actions
        heart_icon = document.querySelector(f'.action-buttons i[data-post-id="{post_id}"]')
        if not heart_icon:
            return
        
        # TOGGLE the liked status (unlike if already liked)
        post["liked"] = not post["liked"]
        
        # Show heart animation only when liking (not when unliking)
        if post["liked"]:
            # Update UI to liked state
            heart_icon.className = "fas fa-heart"
            heart_icon.style.color = "#ed4956"  # Instagram red
            
            # Show heart animation
            heart_animation = post_image.querySelector(".heart-animation")
            if heart_animation:
                # Reset animation by removing and adding the class
                heart_animation.classList.remove("animate")
                # Force reflow
                void(heart_animation.offsetWidth)
                # Start animation again
                heart_animation.classList.add("animate")
        else:
            # Update UI to unliked state
            heart_icon.className = "far fa-heart"
            heart_icon.style.color = "#000"  # Black color
    except Exception as e:
        console.error(f"Error handling double click: {e}")

def create_post_element(post):
    """Create a DOM element for a post with improved layout"""
    try:
        # Create post container
        post_div = document.createElement('div')
        post_div.className = 'instagram-post'
        post_div.id = f"post-{post['id']}"
        
        # 1. Post image
        post_image = document.createElement('div')
        post_image.className = 'post-image'
        post_image.setAttribute("data-post-id", str(post["id"]))
        
        image = document.createElement('img')
        image.src = post['image_url']
        image.alt = 'Item for trade'
        
        # Add heart animation element for double-click
        heart_animation = document.createElement('i')
        heart_animation.className = 'fas fa-heart heart-animation'
        
        post_image.appendChild(image)
        post_image.appendChild(heart_animation)
        
        # Add double-click handler
        dbl_click_proxy = create_proxy(handle_double_click)
        proxies[f"dbl_click_{post['id']}"] = dbl_click_proxy
        post_image.addEventListener("dblclick", dbl_click_proxy)
        
        # 2. Action buttons container - heart and bookmark icons
        actions_container = document.createElement('div')
        actions_container.className = 'post-actions-container'
        
        # Heart button container
        action_buttons = document.createElement('div')
        action_buttons.className = 'action-buttons'
        
        # Heart icon
        heart_icon = document.createElement('i')
        heart_icon.className = 'far fa-heart' if not post.get('liked') else 'fas fa-heart'
        heart_icon.style.color = '#ed4956' if post.get('liked') else '#000'
        heart_icon.title = 'Interested in trading'
        heart_icon.setAttribute('data-post-id', str(post['id']))
        
        # Add click handler for heart icon
        toggle_like_proxy = create_proxy(toggle_like)
        proxies[f"toggle_like_{post['id']}"] = toggle_like_proxy
        heart_icon.addEventListener("click", toggle_like_proxy)
        
        action_buttons.appendChild(heart_icon)
        
        # Bookmark container
        bookmark = document.createElement('div')
        bookmark.className = 'bookmark'
        
        # Bookmark icon
        bookmark_icon = document.createElement('i')
        bookmark_icon.className = 'fas fa-bookmark' if post.get('bookmarked') else 'far fa-bookmark'
        bookmark_icon.style.color = '#ffcc00' if post.get('bookmarked') else '#000'
        bookmark_icon.title = 'Save for later'
        bookmark_icon.setAttribute('data-post-id', str(post['id']))
        
        # Add click handler for bookmark
        toggle_bookmark_proxy = create_proxy(toggle_bookmark)
        proxies[f"toggle_bookmark_{post['id']}"] = toggle_bookmark_proxy
        bookmark_icon.addEventListener("click", toggle_bookmark_proxy)
        
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
        price_div.textContent = post['price']
        content_div.appendChild(price_div)
        
        # Username and caption
        user_caption = document.createElement('div')
        user_caption.className = 'user-caption'
        
        username = document.createElement('div')
        username.className = 'username'
        username.textContent = post['username']
        
        caption = document.createElement('div')
        caption.className = 'caption'
        caption.textContent = post['caption']
        
        user_caption.appendChild(username)
        user_caption.appendChild(caption)
        content_div.appendChild(user_caption)
        
        # Location info
        if 'location' in post:
            location = document.createElement('div')
            location.className = 'location-info'
            location.textContent = f"Location: {post['location']}"
            content_div.appendChild(location)
        
        # Posted time
        time = document.createElement('div')
        time.className = 'post-time'
        time.textContent = post['posted_time']
        content_div.appendChild(time)
        
        # Add all sections to post
        post_div.appendChild(post_image)
        post_div.appendChild(actions_container)
        post_div.appendChild(content_div)
        
        return post_div
    except Exception as e:
        console.error(f"Error creating post element: {e}")
        return document.createElement('div')

async def load_posts():
    """Load posts and add them to the DOM"""
    try:
        # Get posts (either from API or sample data)
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
from pyodide.ffi import to_js
from js import Promise

# Function to run async function properly
def run_async(async_func):
    Promise.resolve(to_js(async_func())).catch(lambda e: console.error(f"Error: {e}"))

# Initialize when the page loads
def setup():
    """Initialize the trading feed"""
    console.log("Setting up trading feed...")
    # Properly await the async function
    run_async(load_posts)
    
    # Add CSS for heart animation to the document
    add_heart_animation_css()

def add_heart_animation_css():
    """Add CSS for heart animation to the document"""
    try:
        style = document.createElement("style")
        style.textContent = """
        /* Double-click heart animation styles */
        .post-image {
            cursor: pointer;
            user-select: none;
            position: relative;
        }
        
        .heart-animation {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0);
            color: #ffffff;
            font-size: 100px;
            opacity: 0;
            z-index: 10;
            filter: drop-shadow(0 0 10px rgba(0, 0, 0, 0.5));
            pointer-events: none;
        }
        
        .heart-animation.animate {
            animation: heart-burst 0.8s ease-out forwards;
        }
        
        @keyframes heart-burst {
            0% {
                opacity: 0;
                transform: translate(-50%, -50%) scale(0);
            }
            15% {
                opacity: 1;
                transform: translate(-50%, -50%) scale(1.2);
            }
            30% {
                transform: translate(-50%, -50%) scale(0.9);
            }
            45% {
                transform: translate(-50%, -50%) scale(1.1);
            }
            60% {
                transform: translate(-50%, -50%) scale(0.95);
            }
            75% {
                transform: translate(-50%, -50%) scale(1);
            }
            100% {
                opacity: 0;
                transform: translate(-50%, -50%) scale(0);
            }
        }
        
        /* Heart icon animation */
        .action-buttons i.fa-heart:active {
            transform: scale(1.2);
        }
        """
        document.head.appendChild(style)
    except Exception as e:
        console.error(f"Error adding CSS: {e}")

# Run setup when the script is loaded
setup()