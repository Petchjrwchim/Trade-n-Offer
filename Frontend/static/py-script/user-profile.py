from js import document, console, FileReader, window, fetch, Promise
from pyodide.ffi import create_proxy, to_js
import json
import asyncio

# Sidebar toggle functionality
menu_toggle = document.querySelector('.menu-toggle')
sidebar = document.querySelector('.sidebar')

def toggle_sidebar(event):
    if sidebar and menu_toggle:
        sidebar.classList.toggle('active')
        menu_toggle.classList.toggle('active')

if menu_toggle:
    menu_toggle.addEventListener('click', create_proxy(toggle_sidebar))

# Tab switching functionality
def show_tab(tab_name, event=None):
    console.log(f"Switching to {tab_name} tab")
    
    tabs = document.querySelectorAll('.tab-content')
    buttons = document.querySelectorAll('.tab-button')

    for tab in tabs:
        tab.classList.remove('active')
    for button in buttons:
        button.classList.remove('active')

    tab_content = document.getElementById(f"{tab_name}-tab")
    tab_button = document.getElementById(f"{tab_name}Tab")
    
    if tab_content:
        tab_content.classList.add('active')
    else:
        console.error(f"Tab content #{tab_name}-tab not found")
        
    if tab_button:
        tab_button.classList.add('active')
    else:
        console.error(f"Tab button #{tab_name}Tab not found")

    window.location.hash = f"{tab_name}-tab"

    if tab_name == 'products':
        render_products()
    elif tab_name == 'saved':
        render_saved()
    elif tab_name == 'liked':
        # Call the function to load wishlist items instead of directly calling render_liked
        Promise.resolve(to_js(create_userWishlist())).catch(
            lambda e: console.error(f"Error loading wishlist: {e}")
        )
    else:
        console.error(f"Unknown tab: {tab_name}")

def handle_profile_image_change(event):
    try:
        files = event.target.files
        if files.length > 0:
            file = files.item(0)
            profile_preview = document.querySelector('.profile-avatar')
            reader = FileReader.new()
            
            def on_load(e):
                # Update preview image in the popup
                profile_preview.src = e.target.result
                # Store the image data in a data attribute to use when saving
                document.getElementById('editProfileImage').setAttribute('data-image', e.target.result)
                
            reader.onload = create_proxy(on_load)
            reader.readAsDataURL(file)
    except Exception as e:
        console.error(f"Error handling profile image change: {e}")

def open_edit_profile(event=None):
    try:
        # Get current values to populate the form
        current_name = document.querySelector('.profile-name').textContent
        current_description = document.querySelector('.profile-description').textContent
        current_image = document.querySelector('.profile-avatar').src
        
        # Set values in form
        document.getElementById('editProfileName').value = current_name
        document.getElementById('editProfileDescription').value = current_description
        
        # Show the custom file input and styles
        document.getElementById('profileImageSelect').style.display = 'block'
        
        # Display popup
        popup = document.getElementById('editProfilePopup')
        if popup:
            popup.style.display = 'flex'
        else:
            console.error("Edit profile popup not found")
    except Exception as e:
        console.error(f"Error opening profile popup: {e}")

def close_edit_profile(event=None):
    popup = document.getElementById('editProfilePopup')
    if popup:
        popup.style.display = 'none'
    else:
        console.error("Edit profile popup not found")

def save_profile_changes(event=None):
    try:
        name_input = document.getElementById('editProfileName')
        desc_input = document.getElementById('editProfileDescription')
        image_input = document.getElementById('editProfileImage')
        
        if not name_input or not desc_input:
            console.error("Profile form elements not found")
            return
            
        name = name_input.value
        description = desc_input.value
        image_data = image_input.getAttribute('data-image')  # Get stored image data

        if name and description:
            # Update profile name and description
            name_element = document.querySelector('.profile-name')
            desc_element = document.querySelector('.profile-description')
            avatar_element = document.querySelector('.profile-avatar')
            
            if name_element:
                name_element.textContent = name
            if desc_element:
                desc_element.textContent = description
            
            # Update profile image if a new one was selected
            if image_data and avatar_element:
                avatar_element.src = image_data
                
            close_edit_profile()
            
            # Show success feedback to user
            feedback = document.createElement("div")
            feedback.style.position = "fixed"
            feedback.style.bottom = "20px"
            feedback.style.right = "20px"
            feedback.style.backgroundColor = "#4CAF50"
            feedback.style.color = "white"
            feedback.style.padding = "10px 20px"
            feedback.style.borderRadius = "5px"
            feedback.style.zIndex = "1000"
            feedback.textContent = "Profile updated successfully!"
            document.body.appendChild(feedback)
            
            # Remove feedback after 3 seconds
            def remove_feedback():
                document.body.removeChild(feedback)
            window.setTimeout(create_proxy(remove_feedback), 3000)
        else:
            console.error('Please fill in all required fields')
    except Exception as e:
        console.error(f"Error saving profile changes: {e}")

async def fetch_user_wishlist():
    try:
        console.log("Fetching user wishlist")

        response = await fetch(
            "/user_wishlist",
            to_js({
                "method": "GET",
                "headers": {"Content-Type": "application/json"},
                "credentials": "include"
            })
        )

        console.log(f"Response status: {response.status}")

        if response.status == 200:
            posts = await response.json()
            console.log("Fetched wishlist items:", posts)
            return posts
        else:
            console.error(f"Failed to fetch wishlist. Status: {response.status}")
            # Return sample data if API call fails
            return sample_liked_data

    except Exception as e:
        console.error(f"Error fetching wishlist: {e}")
        # Return sample data if there's an exception
        return sample_liked_data

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

    popup_content = document.createElement('div')
    popup_content.style.width = '375px'
    popup_content.style.backgroundColor = 'white'
    popup_content.style.borderRadius = '15px'
    popup_content.style.overflow = 'hidden'
    popup_content.style.position = 'relative'
    
    # Create the popup content
    profile_pic = item.get('profile_pic', '') or '/static/image_test/profile_default.jpg'
    image_url = item.get('image_url', '') or item.get('image', '')
    username = item.get('username', 'User')
    
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
            </div>
            <div>
                <i class="far fa-bookmark" id="bookmarkIcon" style="font-size:24px; cursor:pointer;"></i>
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

    heart_icon = popup_content.querySelector('#likeIcon');
    Promise.resolve(check_wishlist_status(item['zodb_id'], heart_icon))

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
    
    # Functions for like and bookmark buttons
    def toggle_like(event):
        like_icon = document.getElementById('likeIcon')
        if 'far' in like_icon.className:
            like_icon.className = 'fas fa-heart'
            like_icon.style.color = '#ed4956'
        else:
            like_icon.className = 'far fa-heart'
            like_icon.style.color = '#000'
    
    def toggle_bookmark(event):
        bookmark_icon = document.getElementById('bookmarkIcon')
        if 'far' in bookmark_icon.className:
            bookmark_icon.className = 'fas fa-bookmark'
            bookmark_icon.style.color = '#000'
        else:
            bookmark_icon.className = 'far fa-bookmark'
            bookmark_icon.style.color = '#000'
    
    # Add content to popup
    popup_content.appendChild(close_btn)
    popup.appendChild(popup_content)
    
    # Close popup event
    def close_popup(event):
        document.body.removeChild(popup)
    
    close_btn.addEventListener('click', create_proxy(close_popup))
    popup.addEventListener('click', create_proxy(lambda e: close_popup(e) if e.target == popup else None))
    
    # Add popup to body
    document.body.appendChild(popup)
    
    # Add event listeners for like and bookmark
    like_icon = document.getElementById('likeIcon')
    bookmark_icon = document.getElementById('bookmarkIcon')
    
    like_icon.addEventListener('click', create_proxy(toggle_like))
    bookmark_icon.addEventListener('click', create_proxy(toggle_bookmark))

async def create_userWishlist():
    try:
        wishlist = await fetch_user_wishlist()
        liked_grid = document.getElementById('likedGrid')
        if not liked_grid:
            console.error("Liked grid element (#likedGrid) not found!")
            return
        
        # Clear existing content
        liked_grid.innerHTML = ''
        
        # Check if wishlist is empty
        if not wishlist or len(wishlist) == 0:
            empty_message = document.createElement('div')
            empty_message.style.textAlign = 'center'
            empty_message.style.padding = '20px'
            empty_message.style.color = '#FFFFFF'
            empty_message.style.fontSize = '16px'
            empty_message.textContent = 'Your wishlist is empty. Add items from the Explore tab!'
            liked_grid.appendChild(empty_message)
            console.log("Empty wishlist message displayed")
            return
            
        # Render each wishlist item
        for item in wishlist:
            render_liked(item)
        
        console.log("Wishlist items rendered successfully")
    except Exception as e:
        console.error(f"Error creating wishlist: {e}")

def render_liked(item):
    try:
        liked_grid = document.getElementById('likedGrid')
        if not liked_grid:
            console.error("Liked grid not found")
            return
            
        liked_div = document.createElement('div')
        liked_div.classList.add('liked-card')
        liked_div.style.cursor = 'pointer'

        # Convert item if it's a JS object
        if hasattr(item, 'to_py'):
            item = item.to_py()
        
        # Handle different property names coming from different APIs
        img = document.createElement('img')
        img.src = item.get('image_url', '') or item.get('image', '')
        img.alt = item.get('name', 'Item')
        img.classList.add('liked-image')
        
        name_container = document.createElement('div')
        name_container.classList.add('liked-name')
        
        heart_icon = document.createElement('i')
        heart_icon.classList.add('fas', 'fa-heart', 'heart-icon')
        name_container.appendChild(heart_icon)
        
        name_text = document.createTextNode(item.get('name', 'Item'))
        name_container.appendChild(name_text)
        
        description = document.createElement('div')
        description.classList.add('liked-description')
        description.textContent = item.get('description', '')
        
        price = document.createElement('div')
        price.classList.add('liked-price')
        price.textContent = item.get('price', '$0')
        
        liked_div.appendChild(img)
        liked_div.appendChild(name_container)
        liked_div.appendChild(description)
        liked_div.appendChild(price)
        
        # Add click event to show item details
        def create_click_handler(selected_item):
            def handler(event):
                create_post_popup(selected_item)
            return handler

        click_proxy = create_proxy(create_click_handler(item))
        liked_div.addEventListener('click', click_proxy)
        
        liked_grid.appendChild(liked_div)
    except Exception as e:
        console.error(f"Error rendering liked item: {e}")

def render_products():
    # Placeholder function in case we need it in the future
    console.log("render_products called but not implemented")

def render_saved():
    # Placeholder function in case we need it in the future
    console.log("render_saved called but not implemented")

async def initialize():
    try:
        # Create the custom file input wrapper
        file_input_container = document.createElement("div")
        file_input_container.id = "profileImageSelect"
        file_input_container.className = "custom-file-input"
        file_input_container.style.display = "none"
        file_input_container.style.marginBottom = "15px"
        file_input_container.style.textAlign = "center"
        
        # Create the label for the file input
        file_label = document.createElement("label")
        file_label.htmlFor = "editProfileImage"
        file_label.style.display = "inline-block"
        file_label.style.padding = "10px 15px"
        file_label.style.backgroundColor = "#3A3A3A"
        file_label.style.color = "#FFFFFF"
        file_label.style.borderRadius = "6px"
        file_label.style.cursor = "pointer"
        file_label.style.transition = "background-color 0.3s"
        file_label.innerHTML = '<i class="fas fa-camera"></i> Choose Profile Image'
        
        # Add hover effect
        file_label.addEventListener("mouseover", create_proxy(lambda e: 
            e.target.style.setProperty("background-color", "#4A4A4A")))
        file_label.addEventListener("mouseout", create_proxy(lambda e: 
            e.target.style.setProperty("background-color", "#3A3A3A")))
        
        # Add the file input and label to the container
        file_input_container.appendChild(file_label)
        
        # Get the edit profile popup content
        popup_content = document.querySelector("#editProfilePopup .popup-content")
        
        if popup_content:
            # Insert the file input container after the heading
            heading = popup_content.querySelector("h2")
            if heading:
                heading.insertAdjacentElement("afterend", file_input_container)
        
        # Setup event listeners for tab switching
        productsTab = document.getElementById("productsTab")
        likedTab = document.getElementById("likedTab")
        savedTab = document.getElementById("savedTab")
        
        if productsTab:
            productsTab.addEventListener("click", create_proxy(lambda e: show_tab("products", e)))
        else:
            console.error("Products tab not found")
            
        if likedTab:
            likedTab.addEventListener("click", create_proxy(lambda e: show_tab("liked", e)))
        else:
            console.error("Liked tab not found")
            
        if savedTab:
            savedTab.addEventListener("click", create_proxy(lambda e: show_tab("saved", e)))
        else:
            console.error("Saved tab not found")
            
        # Setup event listeners for profile editing
        editProfileBtn = document.getElementById("editProfileBtn")
        closeEditProfileBtn = document.getElementById("closeEditProfileBtn")
        saveProfileBtn = document.getElementById("saveProfileBtn")
        editProfileImage = document.getElementById("editProfileImage")
        
        if editProfileBtn:
            editProfileBtn.addEventListener("click", create_proxy(open_edit_profile))
        if closeEditProfileBtn:
            closeEditProfileBtn.addEventListener("click", create_proxy(close_edit_profile))
        if saveProfileBtn:
            saveProfileBtn.addEventListener("click", create_proxy(save_profile_changes))
        if editProfileImage:
            editProfileImage.addEventListener("change", create_proxy(handle_profile_image_change))
            # Make the file input visible to the label
            file_label.appendChild(editProfileImage)

        # Check URL hash to see which tab to show
        hash = window.location.hash
        if hash and hash.startswith('#') and hash.endswith('-tab'):
            tab_name = hash[1:-4]  # Remove the '#' and '-tab'
            if tab_name in ['products', 'liked', 'saved']:
                show_tab(tab_name)
            else:
                # Default to wishlist tab
                show_tab('liked')
        else:
            # Default to wishlist tab if no hash
            show_tab('liked')
        
    except Exception as e:
        console.error(f"Error during initialization: {e}")

# Initialize the application
Promise.resolve(to_js(initialize())).catch(lambda e: console.error(f"Error: {e}"))