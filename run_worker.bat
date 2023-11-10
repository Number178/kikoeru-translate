set BG_TASK_WAIT_SECS=5

set CONFIG_DIR=Y:\Codes\kikoeru-translate

:: 数据库目录
set DB_PATH=%CONFIG_DIR%\db

:: 音频存储目录，其中的音频文件在完成后会被删除
set INPUT_PATH=%CONFIG_DIR%\cache\input 

::字幕输出目录，长期存储，不删除
set OUTPUT_PATH=%CONFIG_DIR%\cache\output

:: 只读文件夹，模型存放路径，文件夹类似这个样子: ./cache/model/model.bin
set MODEL_PATH=%CONFIG_DIR%\cache\model

:: 运行转译的加速设备，如果不提供，默认使用cpu
:: set TRANSCRIBE_DEVICE=auto
set TRANSCRIBE_DEVICE=cuda

:: 配置cuda环境
set PATH=%PATH%;%cd%\cache\cudnn

python -m server.background_task
