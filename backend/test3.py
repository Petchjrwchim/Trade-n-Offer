from app.zodb_setup import get_root, commit_changes
from app.db_config import get_db_connection
import mysql.connector
from api.routes.item_class import TradeItem

# Get ZODB root
root = get_root()

# Ensure "trade_items" exists
if "trade_items" not in root:
    root["trade_items"] = {}

# ✅ Create new item
new_item_id = len(root["trade_items"]) + 1  # Auto-increment ZODB ID
new_item = TradeItem(
    name="Test Item for User 7",
    description="This is a test item",
    price=99.99,
    image="test.jpg",
    category="General"
)

# Store in ZODB
root["trade_items"][new_item_id] = new_item
commit_changes()  # Save changes

print(f"✅ Item {new_item_id} added to ZODB!")

# ✅ Store in MySQL with UserID 7
conn = get_db_connection()
cursor = conn.cursor()

try:
    cursor.execute(
        "INSERT INTO trade_items (userID, zodb_id) VALUES (%s, %s)",
        (7, new_item_id)
    )
    conn.commit()
    print(f"✅ Item {new_item_id} linked to UserID 7 in MySQL!")
except mysql.connector.Error as err:
    conn.rollback()
    print(f"❌ Failed to insert into MySQL: {err}")

cursor.close()
conn.close()
