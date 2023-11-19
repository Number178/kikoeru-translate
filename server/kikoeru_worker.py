from typing import Tuple, Dict
import json
import os
import time
import datetime
import server.common as common
import requests

db_dir = common.getDbDir()
task_file_path = common.getTaskFilePath()
input_audio_dir = common.getInputDir()
worker_name = common.getWorkerName()
worker_idle_seconds = common.getBackgroundIdleSeconds()
kikoeru_url = common.getKikoeruUrl()
kikoeru_user = common.getKikoeruUser()
kikoeru_password = common.getKikoeruPassword()
is_need_auth = False

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

# task = {id: 0, secret: "777f7f7f77fd7"}
def processTask(task):
    print("存储task信息到本地文件中") # 目前一个worker一次只处理一个task
    # 当进行处理的时候，通过一个本地文件
    saveTaskToFile(task)

    if 'audio_file_name' not in task:
        print("下载音频文件")
        audio_file_name = f"{task['id']}{task['audio_ext']}"
        downloadAudioFile(task, audio_file_name)
        task['audio_file_name'] = audio_file_name
        saveTaskToFile(task)
    else:
        audio_file_name = task['audio_file_name']

    audio_file_path = os.path.join(input_audio_dir, audio_file_name)
    print("音频文件下载至：", audio_file_path)
    
    for i in range(10):
        time.sleep(0.5)
        updateTaskStatus(task, f"翻译进度: {(i+1)*10}%")

    finishTask(task, True, """
[00:00.00] 啊啦，有个可爱的孩子迷上了你
[00:05.16] 啊，没关系的哦
[00:07.96] 不是你搞错了房间
[00:10.72] 是哥哥你偶尔就进了这间房间
[00:14.10] 这间房间是只能和想做色色的事的人和我们精灵连接的唯一的地方
[00:25.92] 也就是说，哥哥现在是世界上最焦躁的状态
[00:34.92] 可以进来哦
[00:37.68] 请让我喝茶，慢慢说明一下
[00:42.92] 要喝什么？
[00:45.92] 这样啊
[00:47.56] 那么，请让我准备精灵特制的红茶
[00:53.76] 那么，请坐到床上去
[01:08.20] 哥哥，一副非常可爱的表情呢
[01:15.08] 刚才也说过了，真是太可爱了
[01:19.88] 虽然我已经在这里做了好几年下流的事了
[01:28.52] 但可能还是第一次体验到这么想吃的人
[01:40.80] 红茶我拿来了，请吧
[01:48.76] 那么，再次欢迎来到异世界
[01:53.92] 关于本店的系统的事情，请允许我为您说明
[01:59.96] 本店不会付您任何钱
[02:05.00] 相对的，在玩法的最后
[02:07.60] 会收下您浓稠的精液
[02:11.60] 那个时候，请您尽情的射出浓稠的精液吧
[02:19.30] 如果客人在中途射精的话，我们会接受惩罚
[02:27.84] 如果没有问题的话，我想就这样给您按摩
[02:34.84] 可以吗？
[02:39.68] 竟然是这么快就答应了，真可靠啊
""")

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

def main():
    print("hello world: ")
    print("kikoeru_url = ", kikoeru_url)
    print("kikoeru_user = ", kikoeru_user)
    print("kikoeru_password = ", kikoeru_password)
    
    global is_need_auth
    global kikoeru_token

    is_need_auth = checkKikoeruAuth(kikoeru_url)

    if is_need_auth:
        kikoeru_token = loginKikoeru(kikoeru_url, kikoeru_user, kikoeru_password)
        if kikoeru_token != "":
            common.saveToken(kikoeru_token)
            setupSession(session, kikoeru_token)

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