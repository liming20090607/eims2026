@echo off
chcp 65001 >nul
title Re-upload and Restore User Groups
echo ========================================
echo   Re-upload and Restore User Groups
echo ========================================
echo.

echo Step 1: Uploading FIXED restore script to server...
scp -C "E:\EIMS2026\bat\restore-groups-script.py" root@39.106.41.239:/root/

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Script upload failed!
    pause
    exit /b 1
)

echo.
echo Step 2: Running restore script on server...
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
