import js

# Simulated database as an array of dictionaries
users_db = [
    {"username": "admin", "password": "1234"},
    {"username": "user1", "password": "password"},
]

def login():
    """Handles user login by checking credentials against the database."""
    username = js.document.getElementById("username").value
    password = js.document.getElementById("password").value

    if username and password:
        for user in users_db:
            if user["username"] == username and user["password"] == password:
                js.alert(f"Welcome, {username}!")
                return

        js.alert("Incorrect username or password!")
    else:
        js.alert("Please enter both username and password!")

def register():
    """Registers a new user if the username is not already in the database."""
    username = js.document.getElementById("username").value
    password = js.document.getElementById("password").value

    if username and password:
        for user in users_db:
            if user["username"] == username:
                js.alert("Username already exists! Try another.")
                return

        users_db.append({"username": username, "password": password})
        success_sound = js.Audio.new("data/sounds/jump.wav")
        success_sound.play()
        js.alert(f"User {username} registered successfully!")
    else:
        js.alert("Please enter a username and password!")

# Expose functions to JavaScript
js.login = login
js.register = register
