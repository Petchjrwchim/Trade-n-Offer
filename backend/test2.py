from app.zodb_setup import get_root

root = get_root()

if "trade_items" in root:
    for item_id, item in root["trade_items"].items():
        print(f"Item ID: {item_id}, Name: {item.name}, Price: {item.price}")
else:
    print("No trade items found in ZODB.")
