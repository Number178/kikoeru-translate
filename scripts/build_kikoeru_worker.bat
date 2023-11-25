echo clean build folder
set DIST_FOLDER=%cd%\dist
rmdir /s /q %DIST_FOLDER%
mkdir %DIST_FOLDER%\cache

echo build kikoeru worker exe
pyinstaller .\run_kikoeru_worker.py

echo copy startup script
xcopy scripts\kikoeru_worker_scripts\*.* %DIST_FOLDER%

echo copy cuda dlls, please ensure source cuda dll is existed
xcopy cache\cudnn %DIST_FOLDER%\cache\cudnn /E /S /I

echo copy model to dist
robocopy .\cache\model %DIST_FOLDER%\cache\model /E /S
