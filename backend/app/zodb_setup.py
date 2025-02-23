from ZODB import DB
from ZODB.FileStorage import FileStorage
import transaction


storage = FileStorage('database.fs')
db = DB(storage)
connection = db.open()
root = connection.root()

def get_root():
    return root

def commit_changes():
    transaction.commit()

def close_connection():
    connection.close()
