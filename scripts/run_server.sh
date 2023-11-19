trap 'kill $(jobs -p)' EXIT # 当前进程退出时，停止所有后台任务，主要是用来关闭worker

CONFIG_DIR="/Volumes/common/Codes/kikoeru-translate"
export BG_TASK_WAIT_SECS="5"
export DB_PATH="$CONFIG_DIR/db" # 数据库目录
export INPUT_PATH="$CONFIG_DIR/cache/input" # 音频存储目录，其中的音频文件在完成后会被删除
export OUTPUT_PATH="$CONFIG_DIR/cache/output" # 字幕输出目录，长期存储，不删除
export MODEL_PATH="$CONFIG_DIR/model" # 只读文件夹，模型存放路径，文件夹类似这个样子: ./cache/model/model.bin
export TRANSCRIBE_DEVICE="auto" # 运行转译的加速设备，如果不提供，默认使用cpu
export PORT="8820"


echo DB_PATH = $DB_PATH
python run_worker.py & 
python server/server_main.py
