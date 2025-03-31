from js import document, console, FileReader, window
from pyodide.ffi import create_proxy

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

    # Remove active class from all tabs and buttons
    for tab in tabs:
        tab.classList.remove('active')
    for button in buttons:
        button.classList.remove('active')

    # Add active class to selected tab and button
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

    # Update URL hash
    window.location.hash = f"{tab_name}-tab"

    # Render content for the selected tab
    if tab_name == 'products':
        render_products()
    elif tab_name == 'saved':
        render_saved()
    elif tab_name == 'liked':
        render_liked()
    else:
        console.error(f"Unknown tab: {tab_name}")
# Image preview functionality for profile image
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

# Edit Profile popup functions
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

# Simulated product data
product_data = [
    {"id": 1, "name": "Laptop", "description": "Powerful laptop for gaming and work", "price": "999.99", "image": "/static/image_test/piano.jpg"},
    {"id": 2, "name": "Fashion", "description": "Stylish outfit for everyday wear", "price": "199.99", "image": "/static/image_test/guitar.jpg"},
    {"id": 3, "name": "Sofa", "description": "Comfortable modern sofa for living room", "price": "599.99", "image": "/static/image_test/camera.jpg"},
    {"id": 4, "name": "Lamp", "description": "Elegant floor lamp for home decor", "price": "89.99", "image": "/static/image_test/guitar.jpg"},
    {"id": 5, "name": "Sports Gear", "description": "Complete set of sports equipment", "price": "299.99", "image": "/static/image_test/piano.jpg"},
    {"id": 6, "name": "Books", "description": "Collection of classic literature books", "price": "149.99", "image": "/static/image_test/camera.jpg"}
]

# Simulated saved collections data
saved_data = [
    {"id": 1, "name": "Beads", "description": "Colorful beads for crafting", "price": "49.99", "image": "/static/image_test/guitar.jpg"},
    {"id": 2, "name": "Fashion", "description": "Trendy jacket for all seasons", "price": "129.99", "image": "/static/image_test/piano.jpg"},
    {"id": 3, "name": "Books", "description": "Set of educational books", "price": "89.99", "image": "/static/image_test/guitar.jpg"}
]

# Simulated liked items data
# liked_data = [
#     {"id": 1, "name": "Camerasdasda", "description": "High-quality digital camera for photography", "price": "499.99", "image": "/static/image_test/camera.jpg"},
#     {"id": 2, "name": "Guitar", "description": "Acoustic guitar for beginners and professionals", "price": "299.99", "image": "/static/image_test/guitar.jpg"},
#     {"id": 3, "name": "Piano", "description": "Digital piano with 88 keys and weighted action", "price": "799.99", "image": "/static/image_test/piano.jpg"},
#     {"id": 4, "name": "Headphones", "description": "Noise-canceling headphones with premium sound", "price": "199.99", "image": "/static/image_test/camera.jpg"},
#     {"id": 5, "name": "Watch", "description": "Luxury smartwatch with fitness tracking", "price": "349.99", "image": "/static/image_test/piano.jpg"},
#     {"id": 6, "name": "Smartphone", "description": "Latest model smartphone with advanced features", "price": "699.99", "image": "/static/image_test/guitar.jpg"}
# ]
liked_data = [
    {
        "id": 1,
        "username": "camera_lover",
        "profile_pic": "/static/image_test/guitar.jpg", 
        "image_url": "/static/image_test/camera.jpg",
        "name": "Camera", 
        "description": "High-quality digital camera for photography",
        "price": "$499.99",
        "caption": "Vintage camera in excellent condition. Looking to trade for audio equipment.",
        "location": "Bangkok",
        "posted_time": "2d",
        "is_offer": False
    },
    {
        "id": 2,
        "username": "music_enthusiast",
        "profile_pic": "/static/image_test/piano.jpg", 
        "image_url": "/static/image_test/guitar.jpg",
        "name": "Guitar", 
        "description": "Acoustic guitar for beginners and professionals",
        "price": "$299.99",
        "caption": "Beautiful acoustic guitar, barely used. Open to trades.",
        "location": "Chiang Mai",
        "posted_time": "1w",
        "is_offer": False
    }
    # เพิ่มรายการอื่นๆ ตามต้องการ
]




# Functions to render content for each tab
def render_products(event=None):
    product_grid = document.getElementById('productsGrid')
    if not product_grid:
        console.error("Product grid element (#productsGrid) not found!")
        return
    product_grid.innerHTML = ''
    for product in product_data:
        product_div = document.createElement('div')
        product_div.classList.add('product-card')

        img = document.createElement('img')
        img.src = product['image']
        img.alt = product['name']
        img.classList.add('product-image')

        name = document.createElement('div')
        name.classList.add('product-name')
        name.textContent = product['name']

        description = document.createElement('div')
        description.classList.add('product-description')
        description.textContent = product['description']

        price = document.createElement('div')
        price.classList.add('product-price')
        price.textContent = f"${product['price']}"

        product_div.appendChild(img)
        product_div.appendChild(name)
        product_div.appendChild(description)
        product_div.appendChild(price)
        product_grid.appendChild(product_div)
    console.log("Products rendered successfully")

def render_saved(event=None):
    saved_grid = document.getElementById('savedGrid')
    if not saved_grid:
        console.error("Saved grid element (#savedGrid) not found!")
        return
    saved_grid.innerHTML = ''
    for item in saved_data:
        saved_div = document.createElement('div')
        saved_div.classList.add('saved-card')

        img = document.createElement('img')
        img.src = item['image']
        img.alt = item['name']
        img.classList.add('saved-image')

        name = document.createElement('div')
        name.classList.add('saved-name')
        name.textContent = item['name']

        description = document.createElement('div')
        description.classList.add('saved-description')
        description.textContent = item['description']

        price = document.createElement('div')
        price.classList.add('saved-price')
        price.textContent = f"${item['price']}"

        saved_div.appendChild(img)
        saved_div.appendChild(name)
        saved_div.appendChild(description)
        saved_div.appendChild(price)
        saved_grid.appendChild(saved_div)
    console.log("Saved collections rendered successfully")

def create_post_popup(item):
    # สร้าง popup container
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
    
    # สร้าง popup content
    popup_content = document.createElement('div')
    popup_content.style.width = '375px'  # ขนาดเหมือนในรูป
    popup_content.style.backgroundColor = 'white'
    popup_content.style.borderRadius = '15px'
    popup_content.style.overflow = 'hidden'
    popup_content.style.position = 'relative'
    
    # สร้างเนื้อหา popup เหมือนในรูป
    popup_content.innerHTML = f'''
        <div style="display:flex; align-items:center; padding:10px;color:black">
            <img src="{item.get('profile_pic', '')}" 
                 style="width:32px; height:32px; border-radius:50%; margin-right:10px;">
            <div style="font-weight:bold;">{item.get('username', '')}</div>
        </div>
        
        <div style="width:100%; height:375px;">
            <img src="{item.get('image_url', '')}" 
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
                <span style="font-weight:bold; margin-right:5px; color:black">{item.get('username', '')}</span>
                {item.get('caption', '')}
            </div>
            <div style="color:gray; margin-top:5px;">
                Location: {item.get('location', 'Not specified')}
            </div>
            <div style="color:gray; font-size:12px; margin-top:5px;">
                {item.get('posted_time', 'Recently Added')}
            </div>
        </div>
    '''
    
    # เพิ่มปุ่มปิด
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
    
    # เพิ่มฟังก์ชันสำหรับปุ่ม like และ bookmark
    def toggle_like(event):
        like_icon = document.getElementById('likeIcon')
        if 'far' in like_icon.className:
            like_icon.className = 'fas fa-heart'
            like_icon.style.color = 'red'
        else:
            like_icon.className = 'far fa-heart'
            like_icon.style.color = 'black'
    
    def toggle_bookmark(event):
        bookmark_icon = document.getElementById('bookmarkIcon')
        if 'far' in bookmark_icon.className:
            bookmark_icon.className = 'fas fa-bookmark'
            bookmark_icon.style.color = 'black'
        else:
            bookmark_icon.className = 'far fa-bookmark'
            bookmark_icon.style.color = 'black'
    
    # สร้าง popup
    popup_content.appendChild(close_btn)
    popup.appendChild(popup_content)
    
    # เพิ่มเหตุการณ์
    def close_popup(event):
        document.body.removeChild(popup)
    
    close_btn.addEventListener('click', create_proxy(close_popup))
    popup.addEventListener('click', create_proxy(lambda e: close_popup(e) if e.target == popup else None))
    
    # เพิ่ม popup เข้าไปใน body
    document.body.appendChild(popup)
    
    # เพิ่ม event listeners สำหรับ like และ bookmark
    like_icon = document.getElementById('likeIcon')
    bookmark_icon = document.getElementById('bookmarkIcon')
    
    like_icon.addEventListener('click', create_proxy(toggle_like))
    bookmark_icon.addEventListener('click', create_proxy(toggle_bookmark))

def render_liked(event=None):
    liked_grid = document.getElementById('likedGrid')
    if not liked_grid:
        console.error("Liked grid element (#likedGrid) not found!")
        return
    liked_grid.innerHTML = ''
    for item in liked_data:
        liked_div = document.createElement('div')
        liked_div.classList.add('liked-card')
        liked_div.style.cursor = 'pointer'

        img = document.createElement('img')
        img.src = item['image_url']  # เปลี่ยนจาก 'image' เป็น 'image_url'
        img.alt = item['name']
        img.classList.add('liked-image')

        name_container = document.createElement('div')
        name_container.classList.add('liked-name')
        
        heart_icon = document.createElement('i')
        heart_icon.classList.add('fas', 'fa-heart', 'heart-icon')
        name_container.appendChild(heart_icon)
        
        name_text = document.createTextNode(item['name'])
        name_container.appendChild(name_text)

        description = document.createElement('div')
        description.classList.add('liked-description')
        description.textContent = item['description']

        price = document.createElement('div')
        price.classList.add('liked-price')
        price.textContent = item['price']

        liked_div.appendChild(img)
        liked_div.appendChild(name_container)
        liked_div.appendChild(description)
        liked_div.appendChild(price)

        # สร้าง event listener สำหรับการคลิก
        def create_click_handler(selected_item):
            def handler(event):
                create_post_popup(selected_item)
            return handler

        click_proxy = create_proxy(create_click_handler(item))
        liked_div.addEventListener('click', click_proxy)
        
        liked_grid.appendChild(liked_div)
    console.log("Liked items rendered successfully")



def initialize():
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

        
        # Initialize with Products tab active
        render_products()
        check_hash_and_show_tab()
        
    except Exception as e:
        console.error(f"Error during initialization: {e}")

# Run initialization
initialize()