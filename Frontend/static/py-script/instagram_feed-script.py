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
        "posted_time": "2d"
    },
    {
        "id": 2,
        "username": "music_shop",
        "image_url": "/static/image_test/guitar.jpg",
        "caption": "Acoustic guitar with case. Great sound, barely used. Open to trades for other instruments.",
        "price": "$250 or trade",
        "location": "Chiang Mai",
        "posted_time": "5h"
    },
    {
        "id": 3,
        "username": "instrument_trader",
        "image_url": "/static/image_test/piano.jpg",
        "caption": "Digital piano with weighted keys. Perfect condition. Would trade for guitar equipment.",
        "price": "$350 or trade",
        "location": "Phuket",
        "posted_time": "1d"
    }
]

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
        image = document.createElement('img')
        image.src = post['image_url']
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
        heart_icon.setAttribute('data-post-id', str(post['id']))
        heart_icon.onclick = create_proxy(lambda event: toggle_like(event))
        action_buttons.appendChild(heart_icon)
        
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

def toggle_like(event):
    """Toggle heart icon between outline and solid"""
    try:
        icon = event.target
        
        if 'far' in icon.className:
            # Like - switch to solid red heart
            icon.className = 'fas fa-heart'
            icon.style.color = '#ed4956'  # Instagram red
        else:
            # Unlike - switch to outline heart
            icon.className = 'far fa-heart'
            icon.style.color = '#000'  # Black color
    except Exception as e:
        console.error(f"Error toggling like: {e}")

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