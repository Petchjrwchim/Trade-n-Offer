from js import document, console, window, localStorage, setTimeout
from pyodide.ffi import create_proxy

# ข้อมูลโปรไฟล์ตัวอย่าง
PROFILES = [
    {"id": "1", "name": "John Smith", "image": "/static/image_test/profile_default.jpg", "title": "User"},
    {"id": "2", "name": "Mariasdasdasdaa Garcia", "image": "/static/image_test/profile_default.jpg", "title": "User"},
    {"id": "3", "name": "David Wang", "image": "/static/image_test/piano.jpg", "title": "User"}
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
        render_profiles()

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

def render_profiles():
    """แสดงรายการโปรไฟล์ใน Grid"""
    try:
        product_grid = document.getElementById("productGrid")
        if not product_grid:
            return
            
        product_grid.innerHTML = ""
        current_id = localStorage.getItem("selectedProfileId") or "1"
        
        for i, profile in enumerate(PROFILES):
            # สร้าง Element สำหรับแต่ละโปรไฟล์
            item = document.createElement("div")
            item.className = "product-item"
            if profile["id"] == current_id:
                item.classList.add("active")
            item.setAttribute("data-profile-id", profile["id"])
            
            # สร้างรูปภาพ (ไม่มีการเปลี่ยนเมื่อ hover)
            img = document.createElement("img")
            img.src = profile["image"]
            img.className = "product-image"
            
            # สร้างชื่อและตำแหน่ง
            name = document.createElement("div")
            name.className = "product-name"
            name.textContent = profile["name"]
            
            title = document.createElement("div")
            title.className = "product-status"
            title.textContent = profile["title"]
            
            # เพิ่ม Element ลงใน Item
            item.appendChild(img)
            item.appendChild(name)
            item.appendChild(title)
            
            # สร้าง Event Handler สำหรับคลิกเท่านั้น
            def make_handler(pid):
                def handler(event):
                    profile = next(p for p in PROFILES if p["id"] == pid)
                    select_profile(profile)
                return handler
            
            click_proxy = create_proxy(make_handler(profile["id"]))
            proxies[f"click_{i}"] = click_proxy
            item.addEventListener("click", click_proxy)
            
            product_grid.appendChild(item)
            
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