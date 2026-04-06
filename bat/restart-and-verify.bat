@echo off
chcp 65001 >nul
title Restart Server and Verify
echo ========================================
echo   Restart Server and Verify
echo ========================================
echo.
echo Restarting Gunicorn service...
echo.

ssh root@39.106.41.239 "supervisorctl restart eims"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Service restarted successfully!
    echo.
    echo Waiting 5 seconds for service to start...
    timeout /t 5 /nobreak >nul
    echo.
    echo Testing access...
    curl -I http://39.106.41.239:8000/admin/
    echo.
    echo ========================================
    echo   Restart COMPLETE!
    echo ========================================
    echo.
    echo You can now:
    echo   1. Visit: http://39.106.41.239:8000/admin/
    echo   2. Login with admin account
    echo   3. Click on any model (Employee, Project, etc.)
    echo   4. Click "Import" button (top right)
    echo   5. Upload your Excel/CSV file
    echo.
) else (
    echo.
    echo ========================================
    echo   Restart FAILED!
    echo ========================================
    echo.
    echo Please check server status.
)

pause
