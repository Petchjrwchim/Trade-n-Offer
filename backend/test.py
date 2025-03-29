from app.zodb_setup import get_root, commit_changes
from backend.api.models.item_class import TradeItem  # Ensure this matches your import path

# Get the root ZODB storage
root = get_root()

# Ensure the trade_items dictionary exists
if "trade_items" not in root:
    root["trade_items"] = {}

# Create a new trade item
new_item = TradeItem(
    name="Gaming Mouse",
    description="A high-performance wireless gaming mouse.",
    price=49.99,
    image="mouse.jpg",
    category="Electronics"
)

# Assign a unique item ID
item_id = len(root["trade_items"]) + 1  # Auto-increment ID
root["trade_items"][item_id] = new_item
commit_changes()  # Save changes to ZODB

print(f"✅ Item {item_id} added to ZODB: {new_item.name}")
