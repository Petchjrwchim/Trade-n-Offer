from js import document, console
from pyodide.ffi import create_proxy

def search_posts(event=None):
    """Filter posts based on item name search input"""
    try:
        search_term = document.getElementById('searchInput').value.lower().strip()
        posts = document.querySelectorAll('.instagram-post')
        container = document.getElementById('instagram-feed-container')
        
        
        no_results = document.getElementById('no-results-message')
        if no_results:
            no_results.remove()
        
        console.log(f"Searching for: '{search_term}'")
        visible_count = 0
        
        
        if not search_term:
            for post in posts:
                post.style.display = 'block'
                post.classList.remove('search-match')
                visible_count += 1
                console.log("kuy")
        else:
            
            for post in posts:
                
                post_name = None
                
                
                post_name = post.getAttribute('data-name')
                
                
                if not post_name:
                    name_element = post.querySelector('.item_name')
                    if name_element:
                        post_name = name_element.textContent
                
                
                if not post_name:
                    desc_element = post.querySelector('.item-description')
                    if desc_element:
                        post_name = desc_element.textContent
                
                
                console.log(f"Post: {post.id}, Name found: {post_name}")
                
                
                if post_name and search_term.lower() in post_name.lower():
                    post.style.display = 'block'
                    post.classList.add('search-match')  
                    visible_count += 1
                    console.log(f"Match found: {post_name}")
                else:
                    post.style.display = 'none'
                    post.classList.remove('search-match')
        
        
        if visible_count == 0:
            no_results_div = document.createElement('div')
            no_results_div.id = 'no-results-message'
            no_results_div.className = 'no-results'
            no_results_div.textContent = f'No results found for "{search_term}"'
            container.appendChild(no_results_div)
            
        console.log(f"Search complete: {visible_count} posts visiasdasdasdble")
    except Exception as e:
        console.error(f"Error during search: {e}")

def initialize_search():
    """Set up search box event listeners"""
    try:
        search_input = document.getElementById('searchInput')
        search_button = document.getElementById('searchButton')
        console.log("kusady")
        if search_input and search_button:
            
            search_button.addEventListener('click', create_proxy(search_posts))
            console.log("kuys")
            
            def on_key_press(event):
                if event.key == 'Enter':
                    search_posts()
                    
            search_input.addEventListener('keypress', create_proxy(on_key_press))
            console.log("Search bar component initialized")
        else:
            console.error("Search elements not found")
    except Exception as e:
        console.error(f"Error initializing search bar: {e}")


initialize_search()