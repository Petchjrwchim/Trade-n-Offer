from js import document
from pyodide.ffi import create_proxy

menu_toggle = document.getElementById('menu-toggle')
sidebar = document.getElementById('sidebar')
is_open = False

def toggle_sidebar(*args):
    global is_open
    if is_open:
        sidebar.classList.remove('active')
        menu_toggle.classList.remove('active')
        is_open = False
    else:
        sidebar.classList.add('active')
        menu_toggle.classList.add('active')
        is_open = True

def check_outside_click(event):
    global is_open
    if is_open:
        if not (sidebar.contains(event.target) or menu_toggle.contains(event.target)):
            sidebar.classList.remove('active')
            menu_toggle.classList.remove('active')
            is_open = False


toggle_proxy = create_proxy(toggle_sidebar)
outside_proxy = create_proxy(check_outside_click)


menu_toggle.addEventListener('click', toggle_proxy)
document.addEventListener('click', outside_proxy)