trap 'kill $(jobs -p)' EXIT # 当前进程退出时，停止所有后台任务，主要是用来关闭worker

BG_TASK_WAIT_SECS="5"
DB_PATH="./db" # 数据库目录
INPUT_PATH="./cache/input" # 音频存储目录，其中的音频文件在完成后会被删除
OUTPUT_PATH="./cache/output" # 字幕输出目录，长期存储，不删除
MODEL_PATH="./cache/model" # 只读文件夹，模型存放路径，文件夹类似这个样子: ./cache/model/model.bin
TRANSCRIBE_DEVICE="auto" # 运行转译的加速设备，如果不提供，默认使用auto，可选: auto/cpu/cuda/mps
PORT="8820"

python run_worker.py &
python server/server_main.py
