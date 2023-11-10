import os
import pysondb
from pysondb.db import JsonDatabase

def getDbInstance()->JsonDatabase:
    DB_PATH = os.environ.get("DB_PATH", "./db")
    if not os.path.exists(DB_PATH):
        os.makedirs(DB_PATH)
    path = os.path.join(DB_PATH, "db.json")
    return pysondb.db.getDb(path)

def getInputDir()->str:
    p = os.environ.get("INPUT_PATH", "./cache/input")
    if not os.path.exists(p):
        os.makedirs(p)
    return os.path.abspath(p)

def getOutputDir()->str:
    p = os.environ.get("OUTPUT_PATH", "./cache/output")
    if not os.path.exists(p):
        os.makedirs(p)
    return os.path.abspath(p)

def getModelPath()->str:
    p = os.environ.get("MODEL_PATH", "./cache/model")
    if not os.path.exists(p):
        os.makedirs(p)
    return os.path.abspath(p)

def getBackgroundIdleSeconds()->int:
    s = os.environ.get("BG_TASK_WAIT_SECS", "5")
    return int(s)

def getTranscribeDevice()->str:
    return os.environ.get("TRANSCRIBE_DEVICE", "auto")

def getServerPort()->int:
    return int(os.environ.get("PORT", "8820"))
