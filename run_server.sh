trap 'kill $(jobs -p)' EXIT

python3 server/background_task.py &
python server/server_main.py
