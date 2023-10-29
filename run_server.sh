trap 'kill $(jobs -p)' EXIT


BG_TASK_WAIT_SECS="5"
DB_PATH="./db" # 数据库目录
INPUT_PATH="./cache/input" # 音频存储目录，其中的音频文件在完成后会被删除
OUTPUT_PATH="./cache/output" # 字幕输出目录，长期存储，不删除
MODEL_PATH="./cache/model" # 只读文件夹，模型存放路径，文件夹类似这个样子: ./cache/model/model.bin
TRANSCRIBE_DEVICE="auto" # 运行转译的加速设备，如果不提供，默认使用cpu

python3 -m server.background_task &
python server/server_main.py
