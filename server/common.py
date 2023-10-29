import os
import pysondb
from pysondb.db import JsonDatabase

def getDbInstance()->JsonDatabase:
    db_PATH = os.environ.get("DB_PATH", "./db")
    path = os.path.join(db_PATH, "db.json")
    return pysondb.db.getDb(path)

def getBackgroundIdleSeconds()->int:
    return 5