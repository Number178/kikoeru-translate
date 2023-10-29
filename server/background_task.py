import pysondb
from pysondb.db import JsonDatabase
import time
import json
import os
from task import TaskStatus
import common

def process_task(task, db: JsonDatabase):
    print("process task start")
    id = task['id']
    print(" task id = ", id)
    
    print(json.dumps(task, indent=4))
    time.sleep(5)

    db.updateById(id,{"status": TaskStatus.SUCCESS})
    print("process task complete\n\n")

def run_background_task(db: JsonDatabase, wait_seconds:int):
    while True:
        datas = db.reSearch("status", TaskStatus.PENDING)

        if len(datas) == 0:
            print(f"empty tasks, wait for another {wait_seconds} seconds")
            time.sleep(wait_seconds)
            continue
        
        frontTask = datas[0]

        process_task(frontTask, db)

        
if __name__ == "__main__":
    db = common.getDbInstance()
    bgIdleSecs = common.getBackgroundIdleSeconds()
    run_background_task(db, bgIdleSecs)
        