@echo off
chcp 65001 >nul
title Install Import-Export Tool
echo ========================================
echo   Install Django Import-Export Tool
echo ========================================
echo.
echo This will install django-import-export on the server.
echo.
echo Installing...
echo.

ssh root@39.106.41.239 "cd /var/www/eims; source venv/bin/activate; pip install django-import-export"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   Installation SUCCESSFUL!
    echo ========================================
    echo.
    echo Import-Export feature is now enabled!
    echo.
    echo Next steps:
    echo   1. Restart the server
    echo   2. Login to Admin backend
    echo   3. Click "Import" button on any model
    echo.
) else (
    echo.
    echo ========================================
    echo   Installation FAILED!
    echo ========================================
    echo.
    echo Please check network connection and try again.
)

pause
