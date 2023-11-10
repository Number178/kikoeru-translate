set BG_TASK_WAIT_SECS=5

set CONFIG_DIR=%cd%\config

:: 数据库目录
set DB_PATH=%CONFIG_DIR%\db

:: 音频存储目录，其中的音频文件在完成后会被删除
set INPUT_PATH=%CONFIG_DIR%\cache\input 

::字幕输出目录，长期存储，不删除
set OUTPUT_PATH=%CONFIG_DIR%\cache\output

:: 只读文件夹，模型存放路径，文件夹类似这个样子: ./cache/model/model.bin
set MODEL_PATH=%CONFIG_DIR%\cache\model

:: 运行转译的加速设备，如果不提供，默认使用auto，可选：auto/cpu/cuda/mps
set TRANSCRIBE_DEVICE=auto

:: 配置cuda环境
set CUDA_DLL_PATH=%cd%\cudnn
set PATH=%PATH%;%CUDA_DLL_PATH%

.\run_worker\run_worker.exe

:: 运行失败也不要关闭窗口
@pause
