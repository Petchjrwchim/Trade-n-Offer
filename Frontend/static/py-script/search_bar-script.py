from js import document, console
from pyodide.ffi import create_proxy

def search_posts(event=None):
    """Filter posts based on search input"""
    try:
        search_term = document.getElementById('searchInput').value.lower().strip()
        posts = document.querySelectorAll('.instagram-post')
        container = document.getElementById('instagram-feed-container')
        
        # If there's a no-results message, remove it first
        no_results = document.getElementById('no-results-message')
        if no_results:
            no_results.remove()
        
        visible_count = 0
        
        # If search term is empty, show all posts
        if not search_term:
            for post in posts:
                post.style.display = 'block'
                post.classList.remove('search-match')
                visible_count += 1
        else:
            # Otherwise, filter posts by username
            for post in posts:
                username = post.getAttribute('data-username')
                if username and search_term in username:
                    post.style.display = 'block'
                    post.classList.add('search-match')  # Add highlight class
                    visible_count += 1
                else:
                    post.style.display = 'none'
                    post.classList.remove('search-match')
        
        # If no posts are visible, show "no results" message
        if visible_count == 0:
            no_results_div = document.createElement('div')
            no_results_div.id = 'no-results-message'
            no_results_div.className = 'no-results'
            no_results_div.textContent = f'No results found for "{search_term}"'
            container.appendChild(no_results_div)
            
        console.log(f"Search complete: {visible_count} posts visible")
    except Exception as e:
        console.error(f"Error during search: {e}")

def initialize_search():
    """Set up search box event listeners"""
    try:
        search_input = document.getElementById('searchInput')
        search_button = document.getElementById('searchButton')
        
        if search_input and search_button:
            # Add event listeners - only on button click or Enter key
            search_button.addEventListener('click', create_proxy(search_posts))
            
            # Add 'Enter' key support
            def on_key_press(event):
                if event.key == 'Enter':
                    search_posts()
                    
            search_input.addEventListener('keypress', create_proxy(on_key_press))
            console.log("Search bar component initialized")
        else:
            console.error("Search elements not found")
    except Exception as e:
        console.error(f"Error initializing search bar: {e}")

# Initialize the search bar when the script loads
initialize_search()