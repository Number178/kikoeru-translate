# background_task 只处理已下载完成的文件，本身不负责下载文件
# 因为kikoeru的下载url会根据实际文件夹内的内容发生变化，
# 如果长时间等待，task中媒体url对应的文件可能会发生错乱，
# 外部应当保证task在process_task当中能够立即拿到正确的音频文件

import datetime
from pysondb.db import JsonDatabase
import time
import json
import os
from server.task import TaskStatus
import server.common as common
import shutil
from transcribe import WhisperModel
import math

output_dir = common.getOutputDir()
input_dir = common.getInputDir()

def format_seconds(
    seconds: float,
    decimal_marker: str = ".",
) -> str:
    assert seconds >= 0, "non-negative timestamp expected"

    just_seconds = math.floor(seconds) % 60
    just_hundredths_seconds = math.floor(100 * (seconds - math.floor(seconds))) # lrc 秒数以下用0-99显示剩余数位，而不是毫秒，所以这里乘以100, ref: https://en.wikipedia.org/wiki/LRC_(file_format)
    just_minutes = math.floor(seconds / 60)
    return (
        f"[{just_minutes:02d}:{just_seconds:02d}{decimal_marker}{just_hundredths_seconds:02d}]"
    )

# output complete lrc contents joined by '\n'
def transcribe_audio(audio_path:str, model:WhisperModel)->str:
    segments, _ = model.transcribe(task="transcribe", audio=audio_path, language="zh")
    return "\n".join(
        map(
            lambda segment: f"{format_seconds(segment.start)} {segment.text}",
            segments,
        )
    )

def process_task(task, db: JsonDatabase, model: WhisperModel):
    print("process task start")
    id = task['id']
    print(" task id = ", id)
    
    print(json.dumps(task, indent=4))
    db.updateById(id, {
        "status": TaskStatus.TRASCRIPTING,
    })
    output_lrc_name = f"{id}.lrc"
    output_lrc_path = os.path.join(output_dir, output_lrc_name)

    # 开始转译
    audio_path = os.path.join(input_dir, task['mediaPath'])
    lrcContent: str = transcribe_audio(audio_path, model)
    with open(output_lrc_path, "w", encoding="utf8") as f:
        f.write(lrcContent)

    # # 模拟转译结果，提供一个虚假的结果
    # time.sleep(10)
    # shutil.copy(os.path.join(common.getOutputDir(), "dummy.lrc"), output_lrc_path)

    db.updateById(id, {
        "status": TaskStatus.SUCCESS,
        "lrcPath": output_lrc_name,
    })

    # 删除本地音频文件
    os.remove(audio_path)

    print("process task complete\n\n")

def run_background_task_infinitly(db: JsonDatabase, wait_seconds:int, model: WhisperModel):
    # 启动阶段，检查之前的任务执行情况
    # 将处于 TRASCRIPTING 的任务设置为 DOWNLOADED，
    # 因为翻译到中途的话，肯定没有结果保存下来，重新来过
    print("clean previous unfinished trascripting tasks, reset to downloaed and ready to redo task again")
    tasks = db.getByQuery({"status": TaskStatus.TRASCRIPTING})
    for t in tasks:
        print("reset task id = ", t['id'])
        db.updateById(t['id'], {
            "status": TaskStatus.DOWNLOADED,
        })

    while True:
        datas = db.getByQuery({"status": TaskStatus.DOWNLOADED})

        if len(datas) == 0:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\rempty tasks({now}) wait for another {wait_seconds} seconds", end="")
            time.sleep(wait_seconds)
            continue
        else:
            print("\n")
        
        frontTask = datas[0]

        process_task(frontTask, db, model)

def load_model(model_path:str):
    device = common.getTranscribeDevice()
    compute_type = "default" if device == "cuda" else "int8"
    model = WhisperModel(model_path, device=device, compute_type=compute_type)
    return model

def main():
    db = common.getDbInstance()
    bgIdleSecs = common.getBackgroundIdleSeconds()
    print("load model start")
    model = load_model(common.getModelPath())
    print("load model finished, start background loop, waiting for transcribe task")
    run_background_task_infinitly(db, bgIdleSecs, model)

if __name__ == "__main__":
    main()
        