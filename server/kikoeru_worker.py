from typing import Tuple, Dict
import json
import os
import time
import datetime
import server.common as common
import requests
import math
from transcribe import WhisperModel

db_dir = common.getDbDir()
task_file_path = common.getTaskFilePath()
input_audio_dir = common.getInputDir()
worker_name = common.getWorkerName()
worker_idle_seconds = common.getBackgroundIdleSeconds()
kikoeru_url = common.getKikoeruUrl()
kikoeru_user = common.getKikoeruUser()
kikoeru_password = common.getKikoeruPassword()
is_need_auth = False
model: WhisperModel = None

# 使用session进行通信，保存token，每一次运行前检查token是否失效，如果失效，需要重新登陆验证
def setupSession(session:requests.Session, token:str):
    headers = {
        # "Content-Type": "application/json",
    }
    if token != "":
        headers["Authorization"] = f"Bearer {token}"
    session.headers = headers

session = requests.session()
setupSession(session, common.getToken())

# 检查kikoeru用户验证
# 返回False表示不需要用户验证
# 返回True表示需要用户验证
def checkKikoeruAuth(url):
    response = session.get(
        f"{url}/api/auth/me"
    )
    if response.status_code == 200:
        print("当前状态下kikoeru服务器可直接通信")
        return False
    elif response.status_code == 401:
        print("kikoeru服务器需要用户验证")
        return True
    else:
        print(response)
        raise Exception(f"检查服务器登陆时，发生未知错误：{response.status_code}")

def loginKikoeru(url:str, user:str, password:str)->str:
    print("尝试登陆获取token")
    response = session.post(
        f"{url}/api/auth/me",
        {
            "name": user,
            "password": password,
        }
    )
    if response.status_code == 200:
        print("登陆成功")
        kikoeru_token = response.json()['token']
        print("token = ", kikoeru_token)
        return kikoeru_token
    else:
        print("登陆失败")
        return ""

# return [success, not_task_can_acquire, task]
def acquireTask(url:str)->Tuple[bool, bool, Dict]:
    try:
        res = session.post(
            f"{url}/api/lyric/translate/acquire",
            {
                "worker_name": worker_name,
            }
        )
        # print("acquire task response: ", res.status_code)
        no_task_can_acquire = res.status_code == 404
        success = res.status_code == 200
        data = res.json()
    except:
        return [False, True, None]
    # print(data)
    return (success, no_task_can_acquire, data)

def sleepAndWait(secs:int, info):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\r{info} ({now}) wait for another {secs} seconds", end="")
    time.sleep(secs)

def updateTaskStatus(task:Dict, status:str)->bool:
    try:
        res = session.post(
            f"{kikoeru_url}/api/lyric/translate/status",
            {
                **task,
                "worker_status": status,
            }
        )
        print("  任务进度：", status)
        
        return res.json()['success']
    except Exception as e:
        print("updateTaskStatus error: ", e)

def downloadAudioFile(task:Dict, save_name:str)->bool:
    try:
        r = session.get(f"{kikoeru_url}/api/lyric/translate/download", params={
            "id": task["id"],
            "secret": task["secret"],
        }, stream=True)
        with open(os.path.join(input_audio_dir, save_name), 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)
        return True
    except Exception as e:
        print("下载音频失败：", e)
        return False

def finishTask(task:Dict, success:bool, lrc_content:str):
    print("上传任务结果")
    try:
        r = session.post(f"{kikoeru_url}/api/lyric/translate/finish", json={
            "id": task["id"],
            "secret": task["secret"],
            "success": success,
            "lrc_content": lrc_content,
        })
        if r.status_code != 200:
            print("上传任务结果失败", r.json())
    except Exception as e:
        print("上传任务结果失败：", e)
        return False

def saveTaskToFile(task:Dict):
    with open(task_file_path, "w", encoding="utf8") as f:
        json.dump(task, f, indent=4)

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
def transcribe_audio(audio_path:str)->str:
    global model
    segments, _ = model.transcribe(task="transcribe", audio=audio_path, language="zh")
    return "\n".join(
        map(
            lambda segment: f"{format_seconds(segment.start)} {segment.text}",
            segments,
        )
    )

def checkTaskIsDelete(task:Dict)->bool:
    try:
        r = session.get(f"{kikoeru_url}/api/lyric/translate/get", params={
            "id": task["id"],
        }, stream=True)
        if r.status_code == 200:
            data = r.json()
            print("get task status, data = ", data)
            return 'task' not in data
    except Exception as e:
        print("检查任务状态失败：", e)
        raise e

# task = {id: 0, secret: "777f7f7f77fd7"}
def processTask(task):
    print("存储task信息到本地文件中") # 目前一个worker一次只处理一个task
    # 当进行处理的时候，通过一个本地文件记录，方便重启翻译服务器后继续前面的任务
    saveTaskToFile(task)

    # 处理前，获取一次任务状态，如果任务被删除了的话，则不处理，直接返回
    if checkTaskIsDelete(task):
        print("服务器上的翻译任务已被删除，跳过当前任务")
        os.unlink(task_file_path)
        return

    if 'audio_file_name' not in task:
        print("下载音频文件")
        audio_file_name = f"{task['id']}{task['audio_ext']}"
        downloadAudioFile(task, audio_file_name)
        task['audio_file_name'] = audio_file_name
        saveTaskToFile(task)
    else:
        audio_file_name = task['audio_file_name']

    audio_file_path = os.path.join(input_audio_dir, audio_file_name)
    print("音频文件位于：", audio_file_path)

    success = False
    lrc_content = ""
    try:
        print("翻译中...")
        lrc_content = transcribe_audio(audio_file_path)
        success = True
        print("翻译成功")
    except Exception as e:
        print("transcripting error, ", e)
        success = False
        
    finishTask(task, success, lrc_content)

    print(" 任务完成，删除本地记录")
    os.unlink(audio_file_path)
    os.unlink(task_file_path)

def clearOldTaskAtStartup():
    print("尝试处理上一次没有完成的翻译任务")
    if not os.path.exists(task_file_path):
        print("没有遗留的未完成任务，继续正常运行")
        return

    print("发现有未完成的任务，加载并执行")
    with open(task_file_path, "r", encoding="utf8") as f:
        task = json.load(f)
    processTask(task)

def load_model():
    print("load model start")
    global model
    model_path = common.getModelPath()
    device = common.getTranscribeDevice()
    compute_type = "default"
    model = WhisperModel(model_path, device=device, compute_type=compute_type)
    print("load model finished, start background loop, waiting for transcribe task")

def main():
    print("hello world: ")
    print("kikoeru_url = ", kikoeru_url)
    print("kikoeru_user = ", kikoeru_user)
    print("kikoeru_password = ", kikoeru_password)
    
    global is_need_auth
    global kikoeru_token
    global model

    is_need_auth = checkKikoeruAuth(kikoeru_url)

    if is_need_auth:
        kikoeru_token = loginKikoeru(kikoeru_url, kikoeru_user, kikoeru_password)
        if kikoeru_token != "":
            common.saveToken(kikoeru_token)
            setupSession(session, kikoeru_token)

    load_model()

    clearOldTaskAtStartup()
    
    while True:
        success, run_out_of_task, task = acquireTask(kikoeru_url)

        if run_out_of_task:
            sleepAndWait(worker_idle_seconds, "翻译队列为空")
        elif not success:
            sleepAndWait(worker_idle_seconds, f"发生错误(${task.error})")
        else: # success
            print("")
            print("task.id = ", task['id'], "task.secret = ", task['secret'])
            processTask(task)
            
if __name__ == "__main__":
    main()