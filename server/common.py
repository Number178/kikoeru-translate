import os
import pysondb
from pysondb.db import JsonDatabase

def getDbDir()->str:
    p = os.environ.get("DB_PATH", "./db")
    if not os.path.exists(p):
        os.makedirs(p)
    return p

def getDbInstance()->JsonDatabase:
    DB_PATH = getDbDir()
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

def getKikoeruUrl()->str:
    url = os.environ.get("KIKOERU_URL", None)
    if url is None:
        raise Exception("kikoeur url not configed")
    return url.rstrip("/") # remove trailing /

def getKikoeruUser()->str:
    return os.environ.get("KIKOERU_USER", "")

def getKikoeruPassword()->str:
    return os.environ.get("KIKOERU_PASSWORD", "")

def getToken()->str:
    p = getDbDir()
    token_file = os.path.join(p, "token")
    if not os.path.exists(token_file):
        return ""
    with open(token_file, "r", encoding="utf8") as f:
        return f.readline().strip()
    
def saveToken(token:str):
    p = getDbDir()
    token_file = os.path.join(p, "token")
    with open(token_file, "w", encoding="utf8") as f:
        f.write(token)

def getWorkerName()->str:
    return os.environ.get("WORKER_NAME", "default_worker")

db_dir = ""
def getTaskFilePath()->str:
    global db_dir
    if db_dir == "":
        db_dir = getDbDir()
    return os.path.join(db_dir, "task.json")
    