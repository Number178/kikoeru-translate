echo clean build folder
set DIST_FOLDER=%cd%\dist
rmdir /s /q %DIST_FOLDER%
mkdir %DIST_FOLDER%

echo build background worker exe
pyinstaller .\run_worker.py

echo build server exe
pyinstaller .\server\server_main.py

echo copy startup script
xcopy server\for_end_user\*.* %DIST_FOLDER%

echo copy cuda dlls, please ensure source cuda dll is existed
xcopy cache\cudnn %DIST_FOLDER%\cudnn /E /S /I

set MODEL_FOLDER=%DIST_FOLDER%\config\cache\model
mkdir %MODEL_FOLDER%

echo copy model to dist
robocopy Y:\Codes\kikoeru-translate\cache\model %MODEL_FOLDER% /E /S
