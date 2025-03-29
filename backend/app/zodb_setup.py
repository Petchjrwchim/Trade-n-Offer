from ZODB import DB
from ZODB.FileStorage import FileStorage
import transaction

storage = FileStorage('zodb_db/database.fs')
db = DB(storage)
connection = db.open()
root = connection.root()

def get_root():
    return root

def commit_changes():
    try:
        transaction.commit()
    except Exception as e:
        transaction.abort()
        raise Exception(f"Failed to commit changes to ZODB: {str(e)}")

def close_connection():
    try:
        # Commit any pending transactions before closing
        commit_changes()
        connection.close()
    except Exception as e:
        print(f"Error closing ZODB connection: {str(e)}")


def inspect_zodb():
    # You can change 'trade_items' to the actual key you're using in your ZODB database
    trade_items = root.get('trade_items', None)

    if trade_items is None:
        print("No data found in 'trade_items'")
    else:
        print("Trade Items in ZODB:")
        for item_id, item_obj in trade_items.items():
            print(f"ID: {item_id}, Name: , Price: , Category: ")

inspect_zodb()