# backend/api/routes/item_routes.py

from fastapi import APIRouter
from typing import List

router = APIRouter()

# Simulating a list of items (in memory, can be replaced with DB later)
virtual_items = [
    {"name": "Item 1", "description": "Description of Item 1", "color": "#FF6347"},
    {"name": "Item 2", "description": "Description of Item 2", "color": "#4682B4"},
    {"name": "Item 3", "description": "Description of Item 3", "color": "#32CD32"},
]

current_index = 0

@router.get("/item")
async def get_item():
    global current_index
    if current_index >= len(virtual_items):
        current_index = 0  # Reset if all items have been shown
    item = virtual_items[current_index]
    current_index += 1  # Move to the next item
    return item
