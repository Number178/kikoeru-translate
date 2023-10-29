import time

class TaskStatus:
    NONE = 0 # 非法状态
    PENDING = 1 # 待执行
    DOWNLOADING = 2 # 正在下在音频
    DOWNLOADED = 3 # 下载完成
    TRASCRIPTING = 4 # 转录中
    SUCCESS = 5 # 转录成功
    ERROR = 6 # 转录失败

"""
{
    "status": 0, // TaskStatus.xxx
    "resourceUrl": "http://10.10.10.10/download/file.mp3",
    "displayName": "", // 用来展示文件名称的字段，可以包含路径分隔符，这个主要是用来作为搜索的字段，例如外部发起转录任务后，断开链接，后面想要通过文件名、workId等内容来搜索此前转录的结果
    "createdTime": 1698494924.7412841, // 创建时间，用于排序
}
"""

def createNewTask(resourceUrl:str, displayName:str)->object:
    return {
        "status": TaskStatus.PENDING,
        "resourceUrl": resourceUrl,
        "displayName": displayName,
        "createdTime": time.time(),
        "mediaPath": "",
        "lrcPath": "",
    }
