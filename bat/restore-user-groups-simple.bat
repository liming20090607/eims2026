@echo off
chcp 65001 >nul
title Restore User Groups - Simple Method
echo ========================================
echo   Restore User Groups and Permissions
echo ========================================
echo.

echo Step 1: Uploading backup file to server...
scp -C "E:\EIMS2026\backup_before_phase4.json" root@39.106.41.239:/root/

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Upload failed!
    echo Please check SSH connection.
    pause
    exit /b 1
)

echo.
echo Step 2: Uploading restore script to server...
scp -C "E:\EIMS2026\bat\restore-groups-script.py" root@39.106.41.239:/root/

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Script upload failed!
    pause
    exit /b 1
)

echo.
echo Step 3: Running restore script on server...
echo ========================================
echo.

ssh root@39.106.41.239 "cd /var/www/eims && source venv/bin/activate && python3 /root/restore-groups-script.py"

echo.
echo ========================================
if %ERRORLEVEL% EQU 0 (
    echo   SUCCESS!
    echo ========================================
    echo.
    echo NOW:
    echo   1. Refresh browser (F5)
    echo   2. Go to Admin -^> Auth -^> Groups
    echo   3. Check Users page for group assignments
) else (
    echo   FAILED!
    echo ========================================
    echo.
    echo Please check error messages above.
)

echo.
pause
