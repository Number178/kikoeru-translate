set BG_TASK_WAIT_SECS=5

set CONFIG_DIR=%cd%\config

:: 数据库目录
set DB_PATH=%CONFIG_DIR%\db

:: 音频存储目录，其中的音频文件在完成后会被删除
set INPUT_PATH=%CONFIG_DIR%\cache\input 

::字幕输出目录，长期存储，不删除
set OUTPUT_PATH=%CONFIG_DIR%\cache\output

:: 服务器端口
set PORT=8820

.\server_main\server_main.exe

:: 运行失败也不要关闭窗口
@pause
