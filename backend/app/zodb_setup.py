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
        commit_changes()
        connection.close()
    except Exception as e:
        print(f"Error closing ZODB connection: {str(e)}")


