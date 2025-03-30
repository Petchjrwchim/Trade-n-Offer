from js import document
from pyodide.ffi import create_proxy

# Simulated database of notifications (mock dataset)
mock_notifications = [
    {"title": "Uiverse", "time": "1m ago", "content": "New offer received!", "gradient": "linear-gradient(135deg, rgb(255, 137, 176), rgb(126, 93, 255))"},
    {"title": "Uiverse", "time": "5m ago", "content": "Item trade completed.", "gradient": "linear-gradient(180deg, rgb(242, 124, 40), rgb(255, 69, 243))"},
    {"title": "Uiverse", "time": "10m ago", "content": "New message in chat.", "gradient": "linear-gradient(90deg, rgb(242, 212, 40), rgb(255, 56, 56))"},
    {"title": "Uiverse", "time": "15m ago", "content": "Wishlist item available!", "gradient": "linear-gradient(45deg, rgb(70, 197, 255), rgb(64, 64, 255))"},
    {"title": "Uiverse", "time": "20m ago", "content": "Profile updated.", "gradient": "linear-gradient(45deg, rgb(247, 158, 85), rgb(231, 38, 249))"},
    {"title": "Uiverse", "time": "25m ago", "content": "New trade request received.", "gradient": "linear-gradient(135deg, rgb(255, 137, 176), rgb(126, 93, 255))"},
    {"title": "Uiverse", "time": "30m ago", "content": "Item sold successfully.", "gradient": "linear-gradient(180deg, rgb(242, 124, 40), rgb(255, 69, 243))"}
]

def toggle_notification(event):
    notification_card = document.getElementById("notification-card")
    notification_card.classList.toggle("active")
    if notification_card.classList.contains("active"):
        update_notifications()  # Update notifications when opening the card

def update_notifications():
    messages_container = document.getElementById("messages-container")
    messages_container.innerHTML = ""  # Clear existing messages

    # Simulate fetching from a database (using mock data here)
    for i, notification in enumerate(mock_notifications):
        message_html = f"""
            <div class="message">
                <div class="message-icon" style="background: {notification['gradient']}"></div>
                <div class="message-info">
                    <div class="message-header">
                        <div class="message-title">{notification['title']}</div>
                        <div class="message-time">{notification['time']}</div>
                    </div>
                    <div class="message-content">{notification['content']}</div>
                </div>
            </div>
        """
        messages_container.innerHTML += message_html

    # Add animation delays dynamically
    messages = messages_container.querySelectorAll(".message")
    for i, message in enumerate(messages):
        message.style.animationDelay = f"calc({4 - i} * var(--delay))"

# Add event listener for notification
notification_button = document.getElementById("notification-toggle")
if notification_button:
    notification_button.addEventListener("click", create_proxy(toggle_notification))

# Initialize notifications when the page loads
window.addEventListener("load", create_proxy(lambda e: update_notifications()))