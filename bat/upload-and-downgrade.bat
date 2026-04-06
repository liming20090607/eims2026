@echo off
chcp 65001 >nul
title Upload and Run Downgrade Script
echo ========================================
echo   Downgrade Import-Export
echo ========================================
echo.

echo Upgrading downgrade script to server...
scp E:\EIMS2026\bat\downgrade-import-export.sh root@39.106.41.239:/tmp/downgrade-import-export.sh

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Script uploaded!
    echo.
    echo Now SSH to server and run:
    echo bash /tmp/downgrade-import-export.sh
    echo.
    echo OR run these commands manually:
    echo   ssh root@39.106.41.239
    echo   cd /var/www/eims
    echo   source venv/bin/activate
    echo   pip install django-import-export==3.3.7 --force-reinstall
    echo   find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
    echo   supervisorctl restart eims
    echo.
) else (
    echo.
    echo Upload failed!
)

pause
