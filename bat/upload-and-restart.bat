@echo off
chcp 65001 >nul
title Upload Admin and Restart Server
echo ========================================
echo   Upload Admin and Restart
echo ========================================
echo.

:: Change to script directory
cd /d %~dp0
cd ..

echo Current directory: %CD%
echo.

echo Step 1: Uploading admin.py...
scp eims_app\admin.py root@39.106.41.239:/var/www/eims/eims_app/admin.py

if %ERRORLEVEL% NEQ 0 (
    echo Upload failed!
    pause
    exit /b 1
)

echo.
echo Step 2: Clearing Python cache...
ssh root@39.106.41.239 "cd /var/www/eims; find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; echo 'Cache cleared'"

echo.
echo Step 3: Restarting Gunicorn...
ssh root@39.106.41.239 "supervisorctl restart eims"

echo.
echo Step 4: Waiting for restart (5 seconds)...
timeout /t 5 /nobreak >nul

echo.
echo Step 5: Verifying configuration...
ssh root@39.106.41.239 "cd /var/www/eims; grep -n 'ImportExportModelAdmin' eims_app/admin.py | head -3"

echo.
echo ========================================
echo   COMPLETE!
echo ========================================
echo.
echo NOW:
echo   1. Press Ctrl+F5 to hard refresh browser
echo   2. Visit: http://39.106.41.239:8000/admin/eims_app/employee/
echo   3. You should see [导入] button!
echo.

pause
