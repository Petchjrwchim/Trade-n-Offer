from js import document, console, window, localStorage, setTimeout, fetch, Promise
from pyodide.ffi import create_proxy, to_js

# ข้อมูลโปรไฟล์ตัวอย่าง
PROFILES = [
    {"id": "1", "name": "John Smith", "image": "/static/image_test/profile_default.jpg", "title": "User"},
    # {"id": "2", "name": "Mariasdasdasdaa Garcia", "image": "/static/image_test/profile_default.jpg", "title": "User"},
    # {"id": "3", "name": "David Wang", "image": "/static/image_test/piano.jpg", "title": "User"}
]

# เก็บ Proxy ทั้งหมดไว้ใน Dictionary
proxies = {}

def log(message):
    """ฟังก์ชันสำหรับแสดง log"""
    console.log(message)

def show_profile_popup(event=None):
    """แสดง Popup เลือกโปรไฟล์"""
    popup = document.getElementById("profilePopup")
    if popup:
        popup.style.display = "block"
        popup.classList.add("visible")
        Promise.resolve(to_js(create_item_profile())).catch(lambda e: console.error(f"Error: {e}"))

def close_profile_popup(event=None):
    """ปิด Popup เลือกโปรไฟล์"""
    popup = document.getElementById("profilePopup")
    if popup:
        popup.classList.remove("visible")
        
        # ใช้ Persistent Proxy สำหรับ Callback
        if "hide_popup" not in proxies:
            def hide_popup():
                popup.style.display = "none"
            proxies["hide_popup"] = create_proxy(hide_popup)
        
        setTimeout(proxies["hide_popup"], 300)

def select_profile(profile):
    """เลือกโปรไฟล์และอัปเดตการแสดงผล"""
    try:
        document.getElementById("profileImage").src = profile["image"]
        document.getElementById("profileName").textContent = profile["name"]
        document.getElementById("profileTitle").textContent = profile["title"]
        
        localStorage.setItem("selectedProfileId", profile["id"])
        localStorage.setItem("selectedProfileName", profile["name"])
        localStorage.setItem("selectedProfileTitle", profile["title"])
        
        close_profile_popup()
    except Exception as e:
        log(f"Error: {e}")

async def fetch_userItem():
    try:
        console.log("Fethcing user items")

        response = await fetch(
            "/my-items",
            to_js({
                "method": "GET",
                "header": {"Content-Type": "application/json"},
                "credentials": "include"
            })
        )

        console.log(f"Status {response.status}")

        if response.status == 200:
            items = await response.json()
            console.log("User Item from userItems.py:", items)
            return items
        
        else:
            console.error(f"Failed to fetch posts. Status: {response.status}")
            return []
    
    except Exception as e:
        console.error(f"Error fetching posts: {e}")
        return []

async def create_item_profile():
    userItems = await fetch_userItem()

    product_grid = document.getElementById("productGrid")
    if not product_grid:
        console.error("Product profile grid element not found!")
        return
    else:
        product_grid.innerHTML = ""
        render_profile(userItems)
        console.log("Product grid update")

def render_profile(userItems):
    try:
        for item in userItems:

            product_grid = document.getElementById("productGrid")
            if not product_grid:
                return

            current_id = localStorage.getItem("selectedProfileId") or "1"

            # สร้าง Element สำหรับโปรไฟล์ที่ได้จาก userItems
            profile_item = document.createElement("div")
            profile_item.className = "product-item"

            # ทำให้โปรไฟล์ที่ถูกเลือกมีลักษณะพิเศษ
            if item["id"] == current_id:
                profile_item.classList.add("active")

            profile_item.setAttribute("data-profile-id", item["id"])

            # สร้างรูปภาพ
            img = document.createElement("img")
            img.src = item["image"]
            img.className = "product-image"

            # สร้างชื่อและตำแหน่ง
            name = document.createElement("div")
            name.className = "product-name"
            name.textContent = item["name"]

            title = document.createElement("div")
            title.className = "product-status"
            title.textContent = item["title"]

            # เพิ่ม Element ลงใน Item
            profile_item.appendChild(img)
            profile_item.appendChild(name)
            profile_item.appendChild(title)

            # สร้าง Event Handler สำหรับคลิกเท่านั้น
            def make_handler(profile_id):
                def handler(event):
                    selected_profile = next((p for p in userItems if p["id"] == profile_id), None)
                    if selected_profile:
                        select_profile(selected_profile)
                return handler

            click_proxy = create_proxy(make_handler(item["id"]))
            proxies[f"click_{item['id']}"] = click_proxy
            profile_item.addEventListener("click", click_proxy)

            product_grid.appendChild(profile_item)

    except Exception as e:
        log(f"Error rendering profiles: {e}")

def load_saved_profile():
    """โหลดโปรไฟล์ที่บันทึกไว้"""
    try:
        saved_id = localStorage.getItem("selectedProfileId")
        if saved_id:
            profile = next((p for p in PROFILES if p["id"] == saved_id), None)
            if profile:
                document.getElementById("profileImage").src = profile["image"]
                document.getElementById("profileName").textContent = profile["name"]
                document.getElementById("profileTitle").textContent = profile["title"]
    except Exception as e:
        log(f"Error loading profile: {e}")

def go_to_my_items(event=None):
    """Redirect to /MyItem"""
    window.location.href = "/MyItem"

def initialize():
    """เริ่มต้นการทำงาน"""
    # สร้าง Proxies หลัก
    proxies["show_popup"] = create_proxy(show_profile_popup)
    proxies["close_popup"] = create_proxy(close_profile_popup)
    
    # ตั้งค่า Event Listeners
    document.getElementById("profileIconTrigger").addEventListener("click", proxies["show_popup"])
    document.getElementById("closeProfileBtn").addEventListener("click", proxies["close_popup"])
    
    # โหลดโปรไฟล์ที่บันทึกไว้
    load_saved_profile()

# เริ่มต้นการทำงานเมื่อหน้าเว็บโหลดเสร็จ
initialize()