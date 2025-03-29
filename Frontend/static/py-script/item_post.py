import js
import requests
from pyodide.ffi import create_proxy

# Function to fetch items from the backend
def fetch_items():
    url = "/my-items"  # Your FastAPI route
    response = requests.get(url)
    
    if response.status_code == 200:
        items = response.json()["items"]
        return items
    else:
        js.console.log(f"Failed to fetch items: {response.status_code}")
        return []

# Function to render items dynamically into the HTML
def render_items():
    items = fetch_items()
    container = js.document.getElementById('instagram-feed')  # Assuming this is the container for posts
    
    for item in items:
        post_div = js.document.createElement('div')
        post_div.classList.add('instagram-post')
        post_div.innerHTML = f'''
        <div class="post-header">
            <div class="user-info">
                <div class="profile-pic">
                    <img src="{item['image']}" alt="Profile picture">
                </div>
                <div class="username">{item['name']}</div>
            </div>
            <div class="post-options">
                <i class="fas fa-ellipsis-h"></i>
            </div>
        </div>
        <div class="post-image">
            <img src="{item['image']}" alt="Post image">
        </div>
        <div class="post-actions">
            <div class="action-buttons">
                <i class="far fa-heart"></i>
                <i class="far fa-comment"></i>
                <i class="far fa-paper-plane"></i>
            </div>
            <div class="bookmark">
                <i class="far fa-bookmark"></i>
            </div>
        </div>
        <div class="post-likes">
            <span>{item['price']} likes</span>
        </div>
        <div class="post-caption">
            <span class="username">{item['name']}</span>
            <span class="caption-text">{item['description']}</span>
        </div>
        '''
        container.appendChild(post_div)

# Once PyScript is ready, call the render_items function
def on_load():
    render_items()

# Using PyScript's event loop or invoking the render_items directly
js.setTimeout(create_proxy(on_load), 100)  # Using setTimeout to delay execution until PyScript is ready
