from js import document, console, window, fetch
from pyodide.ffi import create_proxy
import json
import asyncio

# Debug variables
debug_mode = True

def debug_log(message):
    """Logs messages to console when debug mode is on"""
    if debug_mode:
        console.log(f"[DEBUG] {message}")

async def diagnostic_test():
    """Run a series of diagnostic tests to identify issues"""
    debug_log("Starting diagnostic tests...")
    
    # 1. Check DOM elements
    check_dom_elements()
    
    # 2. Test API endpoints
    await test_api_endpoints()
    
    # 3. Display test data
    display_test_data()
    
    debug_log("Diagnostic tests completed")

def check_dom_elements():
    """Check if critical DOM elements exist"""
    debug_log("Checking critical DOM elements...")
    
    elements_to_check = [
        "chatList", "chatListLoader", "welcomeScreen", "activeChat",
        "chatMessages", "messagesLoader", "messageInput", "sendMessageBtn"
    ]
    
    for element_id in elements_to_check:
        element = document.getElementById(element_id)
        if element:
            debug_log(f"✓ Found element: {element_id}")
        else:
            debug_log(f"✗ Missing element: {element_id}")

async def test_api_endpoints():
    """Test API endpoints to see if they're working"""
    debug_log("Testing API endpoints...")
    
    # Test fetch accepted offers
    try:
        debug_log("Testing /chat/accepted-offers endpoint...")
        response = await fetch("/chat/accepted-offers", 
                              method="GET",
                              credentials="include")
        
        debug_log(f"Response status: {response.status}")
        
        if response.ok:
            data = await response.json()
            debug_log(f"Received data: {json.dumps(data)[:200]}...")
            debug_log(f"Found {len(data)} offers")
            
            # Store this data for display
            window.test_offers = data
        else:
            debug_log(f"Error response: {await response.text()}")
    except Exception as e:
        debug_log(f"Error testing offers endpoint: {str(e)}")
    
    # Test fetch messages for an example offer
    try:
        debug_log("Testing /chat/messages/1 endpoint (example offer ID)...")
        response = await fetch("/chat/messages/1", 
                              method="GET",
                              credentials="include")
        
        debug_log(f"Response status: {response.status}")
        
        if response.ok:
            data = await response.json()
            debug_log(f"Received data: {json.dumps(data)[:200]}...")
        else:
            debug_log(f"Error response: {await response.text()}")
    except Exception as e:
        debug_log(f"Error testing messages endpoint: {str(e)}")

def display_test_data():
    """Display test data directly in the UI"""
    debug_log("Displaying test data in the UI...")
    
    try:
        # Create a debug container if it doesn't exist
        debug_container = document.getElementById("debug-container")
        if not debug_container:
            debug_container = document.createElement("div")
            debug_container.id = "debug-container"
            debug_container.style.position = "absolute"
            debug_container.style.top = "10px"
            debug_container.style.right = "10px"
            debug_container.style.backgroundColor = "rgba(0, 0, 0, 0.8)"
            debug_container.style.color = "white"
            debug_container.style.padding = "10px"
            debug_container.style.borderRadius = "5px"
            debug_container.style.zIndex = "9999"
            debug_container.style.maxWidth = "400px"
            debug_container.style.maxHeight = "80vh"
            debug_container.style.overflow = "auto"
            
            document.body.appendChild(debug_container)
        
        # Clear previous content
        debug_container.innerHTML = "<h3>Debug Information</h3>"
        
        # Add user ID
        user_id = window.localStorage.getItem("userId") or "Not set"
        debug_container.innerHTML += f"<p><strong>User ID:</strong> {user_id}</p>"
        
        # Add chat list information
        chat_list = document.getElementById("chatList")
        if chat_list:
            debug_container.innerHTML += f"<p><strong>Chat list:</strong> Present</p>"
            debug_container.innerHTML += f"<p><strong>Chat list content:</strong> {chat_list.innerHTML.slice(0, 100)}...</p>"
        else:
            debug_container.innerHTML += f"<p><strong>Chat list:</strong> Missing</p>"
        
        # Add button to display manual chat
        debug_btn = document.createElement("button")
        debug_btn.textContent = "Populate Test Chat"
        debug_btn.style.padding = "5px 10px"
        debug_btn.style.marginTop = "10px"
        debug_btn.style.backgroundColor = "#4CAF50"
        debug_btn.style.color = "white"
        debug_btn.style.border = "none"
        debug_btn.style.borderRadius = "4px"
        debug_btn.style.cursor = "pointer"
        
        debug_btn.addEventListener("click", create_proxy(populate_test_chat))
        
        debug_container.appendChild(debug_btn)
        
    except Exception as e:
        console.error(f"Error displaying test data: {str(e)}")

def populate_test_chat(event=None):
    """Manually populate the chat list with test data"""
    debug_log("Populating test chat data...")
    
    try:
        # Manually create chat list items
        chat_list = document.getElementById("chatList")
        if not chat_list:
            debug_log("Chat list element not found")
            return
        
        # Clear existing content
        chat_list.innerHTML = ""
        
        # Create test chat items
        for i in range(1, 3):
            chat_item = document.createElement("div")
            chat_item.className = "chat-list-item"
            chat_item.setAttribute("data-offer-id", str(i))
            
            chat_item.innerHTML = f"""
                <img class="chat-list-item-img" src="/static/image_test/profile_default.jpg">
                <div class="chat-list-item-info">
                    <div class="chat-list-item-name">Test User {i}</div>
                    <div class="chat-list-item-last-msg">Trade #{i} with User {i+10}</div>
                </div>
                <div class="chat-list-item-meta">
                    <div class="chat-list-item-time">Just now</div>
                </div>
            """
            
            chat_item.addEventListener("click", create_proxy(lambda e, i=i: show_test_chat(i)))
            
            chat_list.appendChild(chat_item)
        
        # Hide welcome screen
        welcome_screen = document.getElementById("welcomeScreen")
        if welcome_screen:
            welcome_screen.style.display = "none"
        
        debug_log("Test chat list populated")
        
    except Exception as e:
        debug_log(f"Error populating test chat: {str(e)}")

def show_test_chat(offer_id):
    """Show a test chat with example messages"""
    debug_log(f"Showing test chat for offer {offer_id}")
    
    try:
        # Show active chat
        active_chat = document.getElementById("activeChat")
        if active_chat:
            active_chat.style.display = "flex"
        
        # Update chat header
        chat_user_name = document.getElementById("chatUserName")
        if chat_user_name:
            chat_user_name.textContent = f"Test User {offer_id}"
        
        chat_item_info = document.getElementById("chatItemInfo")
        if chat_item_info:
            chat_item_info.textContent = f"Trade #{offer_id}"
        
        # Populate chat messages
        messages_container = document.getElementById("chatMessages")
        if messages_container:
            messages_container.innerHTML = ""
            
            # Add example messages
            for i in range(1, 5):
                message_div = document.createElement("div")
                message_div.className = f"message {['incoming', 'outgoing'][i % 2]}"
                
                message_div.innerHTML = f"""
                    <div class="message-text">This is a test message #{i} for trade #{offer_id}</div>
                    <div class="message-time">Just now</div>
                """
                
                messages_container.appendChild(message_div)
            
            # Scroll to bottom
            messages_container.scrollTop = messages_container.scrollHeight
        
        debug_log("Test chat displayed")
        
    except Exception as e:
        debug_log(f"Error showing test chat: {str(e)}")

# Add button to page
def add_debug_button():
    debug_log("Adding debug button to page...")
    
    try:
        button = document.createElement("button")
        button.textContent = "Run Diagnostics"
        button.style.position = "fixed"
        button.style.bottom = "10px"
        button.style.right = "10px"
        button.style.zIndex = "9999"
        button.style.padding = "8px 15px"
        button.style.backgroundColor = "#FF5722"
        button.style.color = "white"
        button.style.border = "none"
        button.style.borderRadius = "4px"
        button.style.fontWeight = "bold"
        button.style.cursor = "pointer"
        
        button.addEventListener("click", create_proxy(lambda e: asyncio.ensure_future(diagnostic_test())))
        
        document.body.appendChild(button)
        
        debug_log("Debug button added")
        
    except Exception as e:
        console.error(f"Error adding debug button: {str(e)}")

# Run on page load
def on_page_load(event=None):
    debug_log("Page loaded, adding debug tools...")
    add_debug_button()

# Add page load listener
document.addEventListener("DOMContentLoaded", create_proxy(on_page_load))

console.log(document.getElementById('chatList'))