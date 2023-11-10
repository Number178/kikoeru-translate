# save this as app.py
from typing import Dict
import task
import flask
from flask import request, abort
from flask_cors import CORS
import common
import json
import os
import threading
import time
import urllib.request
import shutil

static_folder = os.path.join(os.path.dirname(__file__), "static")
print("static folder: ", static_folder)

app = flask.Flask(__name__, static_folder=static_folder, static_url_path='')
CORS(app)

db = common.getDbInstance()
output_dir = common.getOutputDir()
input_dir = common.getInputDir()
server_port = common.getServerPort()

def normalizeTask(t:Dict):
    a = t.copy()
    a['id'] = str(a['id'])
    a.pop("mediaPath")
    a.pop("lrcPath")
    a.pop("resourceUrl")
    return a

def multithread_download_file(id:int):
    db = common.getDbInstance()
    output_dir = common.getInputDir() # 音频文件下载到这个地方
    print("multi thread download file, id = ", id)

    db.updateById(id, {
        "status": task.TaskStatus.DOWNLOADING,
    })
    t = db.getById(id)

    # 从最开始上传task的displayName中获取这个文件的扩展名，比如 ".mp3"
    arr = os.path.splitext(t['displayName'])
    ext = arr[-1] if len(arr) > 1 else ""
    save_file_name = f"{id}{ext}"
    save_file_path = os.path.join(output_dir, save_file_name)
    with urllib.request.urlopen(t['resourceUrl']) as response, open(save_file_path, "wb") as save_file:
        shutil.copyfileobj(response, save_file)

    db.updateById(id, {
        "status": task.TaskStatus.DOWNLOADED,
        "mediaPath": save_file_name,
    })
    print("file downloaded, id = ", id)
    print("file path = ", save_file_path)

@app.route("/task/new", methods=["POST"])
def newTask():
    content = request.json
    t = task.createNewTask(content['url'], content['name'])
    db.add(t)

    thread = threading.Thread(target=multithread_download_file, args=[t['id']])
    thread.start()

    return json.dumps({
        "id": str(t["id"])
    })

@app.route("/task/search", methods=["GET"])
def searchTask():
    keyword = request.args.get("keyword", "none")
    print("keyword = ", keyword)
    tasks = db.reSearch("displayName", keyword)
    print("result numbers = ", len(tasks))
    return json.dumps(list(map(normalizeTask, tasks)))

@app.route("/task/get/<int:id>", methods=["GET"])
def getTask(id):
    task = db.getById(id)
    return json.dumps(normalizeTask(task))

@app.route("/task/download/<int:id>", methods=["GET"])
def downloadTask(id):
    print("download id = ", id)
    tlist = db.getByQuery({
        "id": id,
        "status": task.TaskStatus.SUCCESS,
    })

    if len(tlist) == 0:
        abort(404, "no success task found")
        return 

    with open(os.path.join(output_dir, tlist[0]['lrcPath']), "r", encoding="utf8") as f:
        lrcContent = f.read()
        
    return json.dumps({ "lrcContent": lrcContent })

if __name__ == '__main__':
    app.run(port=server_port, host="0.0.0.0")