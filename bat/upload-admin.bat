@echo off
chcp 65001 >nul
title Upload Admin.py with Import-Export
echo ========================================
echo   Upload Admin.py to Server
echo ========================================
echo.
echo Uploading eims_app\admin.py to server...
echo.

scp eims_app\admin.py root@39.106.41.239:/var/www/eims/eims_app/admin.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   Upload SUCCESSFUL!
    echo ========================================
    echo.
    echo Next steps:
    echo   1. SSH to server
    echo   2. Clear Python cache
    echo   3. Restart Gunicorn
    echo.
    echo OR run: upload-and-restart.bat
    echo.
) else (
    echo.
    echo ========================================
    echo   Upload FAILED!
    echo ========================================
    echo.
    echo Please check network connection.
)

pause
