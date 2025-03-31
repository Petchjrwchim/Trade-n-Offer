import json
from pyodide.ffi import create_proxy,to_js
from js import document, console, fetch, window, Promise

# Sample data with trading items and offers (adding profile pics and usernames)
SAMPLE_POSTS = [
    {
        "id": 1,
        "username": "camera_lover",
        "profile_pic": "/static/image_test/guitar.jpg",
        "image_url": "/static/image_test/guitar.jpg",
        "caption": "Vintage camera in excellent condition. Looking to trade for audio equipment.",
        "price": "$120 or trade",
        "location": "Bangkok",
        "posted_time": "2d",
        "is_offer": False
    },
    {
        "id": 2,
        "username": "music_shop",
        "profile_pic": "/static/image_test/guitar.jpg",
        "image_url": "/static/image_test/guitar.jpg",
        "caption": "Acoustic guitar with case. Great sound, barely used. Open to trades for other instruments.",
        "price": "$250 or trade",
        "location": "Chiang Mai",
        "posted_time": "5h",
        "is_offer": False
    },
    {
        "id": 3,
        "username": "instrument_trader",
        "profile_pic": "/static/image_test/profile3.jpg",
        "image_url": "/static/image_test/piano.jpg",
        "caption": "Digital piano with weighted keys. Perfect condition. Would trade for guitar equipment.",
        "price": "$350 or trade",
        "location": "Phuket",
        "posted_time": "1d",
        "is_offer": True
    },
    {
        "id": 4,
        "username": "camera_pro",
        "profile_pic": "/static/image_test/profile4.jpg",
        "image_url": "/static/image_test/camera.jpg",
        "caption": "Professional DSLR camera with multiple lenses. Perfect for photography enthusiasts.",
        "price": "$750 or trade",
        "location": "Bangkok",
        "posted_time": "1h",
        "is_offer": True
    },
    {
        "id": 5,
        "username": "gadget_trader",
        "profile_pic": "/static/image_test/profile5.jpg",
        "image_url": "/static/image_test/camera.jpg",
        "caption": "High-end laptop, barely used. Looking to trade for camera equipment or musical instruments.",
        "price": "$900 or trade",
        "location": "Pattaya",
        "posted_time": "3h",
        "is_offer": False
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
        if post.get('is_offer', False):
            post_div.classList.add('offer-post')  # Add offer-post class if it's an offer
        
        post_div.id = f"post-{post['id']}"
        post_div.setAttribute('data-username', post['username'].lower())
        
        # Add offer badge if it's an offer
        if post.get('is_offer', False):
            offer_badge = document.createElement('div')
            offer_badge.className = 'offer-badge'
            offer_badge.innerHTML = '<i class="fas fa-tag"></i> Offer'
            post_div.appendChild(offer_badge)
        
        # Post header with profile info
        post_header = document.createElement('div')
        post_header.className = 'post-header'
        
        # Profile picture
        profile_pic = document.createElement('img')
        profile_pic.className = 'profile-picture'
        profile_pic.src = post.get('profile_pic', '/static/image_test/default-profile.jpg')
        profile_pic.alt = f"{post['username']}'s profile"
        
        # Username
        username_elem = document.createElement('div')
        username_elem.className = 'post-username'
        username_elem.textContent = post['username']
        
        # Append profile pic and username to header
        post_header.appendChild(profile_pic)
        post_header.appendChild(username_elem)
        
        # Add header to post
        post_div.appendChild(post_header)
        
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
        
        caption = document.createElement('div')
        caption.className = 'caption'
        caption.textContent = post['caption']
        
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
        
        # Add offer actions if it's an offer post
        if post.get('is_offer', False):
            offer_actions = document.createElement('div')
            offer_actions.className = 'offer-actions'
            
            reject_button = document.createElement('button')
            reject_button.className = 'offer-button reject-button'
            reject_button.innerHTML = '<i class="fas fa-times"></i> Reject'
            reject_button.onclick = create_proxy(lambda e: handle_offer_response(post['id'], 'reject'))
            
            accept_button = document.createElement('button')
            accept_button.className = 'offer-button accept-button'
            accept_button.innerHTML = '<i class="fas fa-check"></i> Accept'
            accept_button.onclick = create_proxy(lambda e: handle_offer_response(post['id'], 'accept'))
            
            offer_actions.appendChild(reject_button)
            offer_actions.appendChild(accept_button)
            
            post_div.appendChild(offer_actions)
        
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

def handle_offer_response(post_id, response):
    """Handle user response to an offer (accept/reject)"""
    try:
        post_element = document.getElementById(f"post-{post_id}")
        if not post_element:
            console.error(f"Post element with ID {post_id} not found")
            return
            
        # Get offer index and total offers
        offer_index = int(post_element.getAttribute('data-offer-index'))
        total_offers = int(post_element.getAttribute('data-total-offers'))
        
        # Remove the offer actions
        offer_actions = post_element.querySelector('.offer-actions')
        if offer_actions:
            offer_actions.remove()
            
        if response == 'accept':
            # Show acceptance message
            status_div = document.createElement('div')
            status_div.className = 'offer-status'
            status_div.textContent = "Offer accepted! The user will be notified."
            status_div.style.color = '#4caf50'
            post_element.style.borderColor = '#4caf50'  # Change border to green
            post_element.appendChild(status_div)
            
            # Wait a moment before showing next offer or removing current offer
            window.setTimeout(create_proxy(lambda: load_next_offer(offer_index, total_offers)), 2000)
        else:
            # For rejection, animate and then remove
            post_element.style.opacity = '0.5'
            post_element.style.transition = 'opacity 0.5s ease, transform 0.5s ease'
            post_element.style.transform = 'translateX(100px)'
            
            # Show next offer after animation
            window.setTimeout(create_proxy(lambda: load_next_offer(offer_index, total_offers)), 500)
    except Exception as e:
        console.error(f"Error handling offer response: {e}")
        
def load_next_offer(current_index, total_offers):
    """Load the next offer in sequence after handling current offer"""
    try:
        # Remove the current offer
        container = document.getElementById('instagram-feed-container')
        current_offer = container.querySelector(f'[data-offer-index="{current_index}"]')
        if current_offer:
            current_offer.remove()
            
        # Check if we have more offers to show
        if hasattr(window, 'remainingOffers') and len(window.remainingOffers) > 0:
            # Get the next offer
            next_offer = window.remainingOffers.pop(0)
            next_index = current_index + 1
            
            # Create and add the next offer
            next_offer_element = create_post_element(next_offer)
            next_offer_element.setAttribute('data-offer-index', str(next_index))
            next_offer_element.setAttribute('data-total-offers', str(total_offers))
            
            # Insert at the top
            if container.firstChild:
                container.insertBefore(next_offer_element, container.firstChild)
            else:
                container.appendChild(next_offer_element)
                
            # Update the offer counter if needed
            offers_left = total_offers - next_index - 1
            update_offer_counter(offers_left + 1)  # +1 because we're showing one now
        else:
            # No more offers, update counter to 0
            update_offer_counter(0)
    except Exception as e:
        console.error(f"Error loading next offer: {e}")
        
def update_offer_counter(count):
    """Update the offer counter display"""
    try:
        counter = document.querySelector('.offer-counter')
        if counter:
            if count > 0:
                counter.textContent = f"{count} offer{'s' if count > 1 else ''} available"
            else:
                counter.textContent = "No more offers available"
                counter.style.backgroundColor = 'rgba(128, 128, 128, 0.2)'
                counter.style.color = '#CCCCCC'
    except Exception as e:
        console.error(f"Error updating offer counter: {e}")

async def load_posts():
    """Load posts and add them to the DOM"""
    try:
        # Get posts (either from API or sample data)
        posts = await fetch_posts()
        
        # Separate offers and regular posts
        offer_posts = [post for post in posts if post.get('is_offer', False)]
        regular_posts = [post for post in posts if not post.get('is_offer', False)]
        
        # Get the container element
        container = document.getElementById('instagram-feed-container')
        
        # Clear existing content (except loading indicator)
        if container:
            loading_indicator = container.querySelector('.loading-indicator')
            container.innerHTML = ''
            
            # Calculate and show offer count at the TOP of the container
            offer_count = len(offer_posts)
            offer_counter = document.createElement('div')
            offer_counter.className = 'offer-counter'
            
            if offer_count > 0:
                offer_counter.textContent = f"{offer_count} offer{'s' if offer_count > 1 else ''} available"
                offer_counter.style.backgroundColor = 'rgba(255, 215, 0, 0.2)'
                offer_counter.style.color = '#FFD700'
            else:
                offer_counter.textContent = "No offers available"
                offer_counter.style.backgroundColor = 'rgba(128, 128, 128, 0.2)'
                offer_counter.style.color = '#CCCCCC'
                
            offer_counter.style.padding = '5px 10px'
            offer_counter.style.borderRadius = '20px'
            offer_counter.style.fontWeight = 'bold'
            offer_counter.style.textAlign = 'center'
            offer_counter.style.margin = '0 auto 15px auto'
            offer_counter.style.maxWidth = '200px'
            container.appendChild(offer_counter)
            
            # Show only the first offer if there are any offers
            if offer_count > 0:
                first_offer = offer_posts[0]
                first_offer_element = create_post_element(first_offer)
                first_offer_element.setAttribute('data-offer-index', '0')
                first_offer_element.setAttribute('data-total-offers', str(offer_count))
                container.appendChild(first_offer_element)
                
                # Store remaining offers in global variable for later access
                window.remainingOffers = offer_posts[1:]
            
            # Add regular posts
            for post in regular_posts:
                post_element = create_post_element(post)
                container.appendChild(post_element)
        else:
            console.error("Container element not found")
            
    except Exception as e:
        console.error(f"Error loading posts: {e}")


# Function to run async function properly
def run_async(async_func):
    Promise.resolve(to_js(async_func())).catch(lambda e: console.error(f"Error: {e}"))

# Initialize when the page loads
def setup():
    """Initialize the trading feed"""
    console.log("Setting up trading feed with offers...")
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