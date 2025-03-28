from js import document, setTimeout, window, localStorage

total_items = 5

# ข้อมูลโปรไฟล์ตัวอย่าง (ในแอปจริงอาจดึงจากฐานข้อมูล)
PROFILES = [
    {"id": 1, "name": "Profile 1", "image": "/static/image_test/camera.jpg"},
    {"id": 2, "name": "Profile 2", "image": "/static/image_test/guitar.jpg"},
    {"id": 3, "name": "Profile 3", "image": "/static/image_test/piano.jpg"},
    {"id": 4, "name": "Profile 4", "image": "/static/image_test/camera.jpg"},
    {"id": 5, "name": "Profile 5", "image": "/static/image_test/guitar.jpg"}
]

def show_profile_popup(event=None):
    """ Show popup and load product list """
    popup = document.querySelector("#profilePopup")
    if popup:
        popup.style.display = "block"
        popup.classList.add("visible")
        update_product_grid()
    else:
        print("Error: Profile popup not found")

def hide_popup():
    """ Helper function to hide popup and reset overlay completely """
    popup = document.querySelector("#profilePopup")
    if popup:
        popup.style.display = "none"
        popup.classList.remove("visible")
        popup.style.opacity = "0"
        popup.style.pointerEvents = "none"
        popup.style.backgroundColor = "transparent"
        
        # Ensure the body or other elements regain focus/interactivity
        document.body.style.pointerEvents = "auto"
    else:
        print("Error: Profile popup not found")

def close_profile_popup(event=None):
    """ Close popup """
    try:
        popup = document.querySelector("#profilePopup")
        if popup:
            popup.style.display = "none"
            popup.classList.remove("visible")
        else:
            print("Error: Profile popup not found")
    except Exception as e:
        print(f"Error closing popup: {e}")

def update_product_grid():
    """Update product list in Grid"""
    productGrid = document.querySelector("#productGrid")
    productGrid.innerHTML = ""

    for i, profile in enumerate(PROFILES, 1):
        productDiv = document.createElement("div")
        productDiv.classList.add("product-item")
        
        # ใช้รูปที่แตกต่างกันตามข้อมูลในอาร์เรย์ PROFILES
        img = document.createElement("img")
        img.src = profile["image"]
        img.alt = profile["name"]
        img.classList.add("product-image")
        
        name = document.createElement("div")
        name.classList.add("product-name")
        name.textContent = profile["name"]
        
        # สร้าง JavaScript onclick โดยตรง
        onclick_js = f"""
        (function() {{
            localStorage.setItem('selectedProfileId', '{profile["id"]}');
            localStorage.setItem('selectedProfileName', '{profile["name"]}');
            localStorage.setItem('selectedProfileImage', '{profile["image"]}');
            
            // อัปเดตชื่อและรูปโปรไฟล์
            document.querySelector('.profile-name').textContent = '{profile["name"]}';
            document.getElementById('profileImage').src = '{profile["image"]}';
            
            // ปิดป๊อปอัป
            document.querySelector('#profilePopup').style.display = 'none';
            document.querySelector('#profilePopup').classList.remove('visible');
            
            console.log('Selected profile: {profile["name"]}');
        }})();
        """
        productDiv.setAttribute("onclick", onclick_js)
        
        productDiv.appendChild(img)
        productDiv.appendChild(name)
        productGrid.appendChild(productDiv)

def select_profile(profile_id, profile_name, profile_image):
    """ เลือกโปรไฟล์และอัปเดตไอคอนหน้าหลัก """
    try:
        # บันทึกข้อมูลใน localStorage เพื่อใช้ในครั้งต่อไปหรือหน้าอื่น
        localStorage.setItem("selectedProfileId", profile_id)
        localStorage.setItem("selectedProfileName", profile_name)
        localStorage.setItem("selectedProfileImage", profile_image)
        
        # อัปเดตรูปภาพและชื่อในการ์ดโปรไฟล์
        update_profile_card(profile_id, profile_name, profile_image)
        
        # ปิดป๊อปอัป
        close_profile_popup()
        
        # เพิ่มการ debug
        print(f"Profile selected: ID={profile_id}, Name={profile_name}, Image={profile_image}")
    except Exception as e:
        print(f"Error selecting profile: {e}")

def update_profile_card(profile_id, profile_name, profile_image):
    """ อัปเดตการ์ดโปรไฟล์หลัก """
    try:
        # อัปเดตชื่อโปรไฟล์
        name_element = document.querySelector(".profile-name")
        if name_element:
            name_element.textContent = profile_name
            
        # อัปเดตรูปภาพโปรไฟล์
        image_element = document.getElementById("profileImage")
        if image_element:
            image_element.src = profile_image
    except Exception as e:
        print(f"Error updating profile card: {e}")

def load_saved_profile():
    """ โหลดโปรไฟล์ที่บันทึกไว้เมื่อเริ่มต้น """
    try:
        profile_id = localStorage.getItem("selectedProfileId")
        if profile_id:
            profile_name = localStorage.getItem("selectedProfileName")
            profile_image = localStorage.getItem("selectedProfileImage")
            
            if profile_name and profile_image:
                update_profile_card(profile_id, profile_name, profile_image)
    except Exception as e:
        print(f"Error loading saved profile: {e}")

def go_to_my_items(event=None):
    """ Redirect to /MyItem """
    window.location.href = "/MyItem"

# โหลดโปรไฟล์ที่บันทึกไว้เมื่อเริ่มต้นหน้า
load_saved_profile()