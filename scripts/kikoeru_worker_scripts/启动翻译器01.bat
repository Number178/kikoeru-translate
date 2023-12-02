set CONFIG_DIR=.\cache

:: kikoeru服务器url
set KIKOERU_URL=http://192.168.5.11:8888

:: kikoeru服务器用户名，开了用户验证的话就要填这个，没开就不用改这个
set KIKOERU_USER=admin

:: kikoeru服务器密码，开了用户验证的话就要填这个，没开就不用改这个
set KIKOERU_PASSWORD=123456

:: 当前翻译服务的名称，可配置多台翻译服务向同一个kikoeru翻译服务器请求翻译任务，
:: 翻译服务之间通过这个名字相互区别，注意名字里只能有字母数字下划线
set WORKER_NAME=windows_01
TITLE "%WORKER_NAME%"

:: 空闲时，轮询服务器的等待时间，单位秒
set BG_TASK_WAIT_SECS=10

:: 数据库目录，注意这里需要区分不同的WORKER_NAME，两个不同的worker不能使用相同的数据库目录
set DB_PATH=%CONFIG_DIR%\db_%WORKER_NAME%

:: 音频存储目录，其中的音频文件在完成后会被删除
set INPUT_PATH=%CONFIG_DIR%\input 

:: 只读文件夹，模型存放路径，文件夹类似这个样子: ./model/model.bin
set MODEL_PATH=%CONFIG_DIR%\model

:: 运行转译的加速设备，如果不提供，默认使用auto，可选：auto/cpu/cuda/mps
set TRANSCRIBE_DEVICE=auto

:: 配置cuda环境
set CUDA_DLL_PATH=%CONFIG_DIR%\cudnn
set PATH=%PATH%;%CUDA_DLL_PATH%

.\run_kikoeru_worker\run_kikoeru_worker.exe

:: 运行失败也不立即退出窗口
@pause
