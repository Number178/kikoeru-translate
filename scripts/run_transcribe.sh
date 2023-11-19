model_dir="./model"
audio_dir="./audio"
output_dir="./output"
python3 ./run_transcribe.py \
 --model $model_dir \
 --audio-dir $audio_dir \
 --save-dir $output_dir \
 --device auto