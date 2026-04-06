@echo off
chcp 65001 >nul
title Fix Admin Styles
echo ========================================
echo   Fix Django Admin Styles
echo ========================================
echo.
echo Executing SSH commands to fix static files...
echo.

ssh root@39.106.41.239 "cd /var/www/eims; source venv/bin/activate; python manage.py collectstatic --noinput --clear; supervisorctl restart eims"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   Static Files Fixed!
    echo ========================================
    echo.
    echo NOW:
    echo   1. Press Ctrl+F5 to hard refresh browser
    echo   2. Visit: http://39.106.41.239:8000/admin/
    echo.
) else (
    echo.
    echo ========================================
    echo   Failed!
    echo ========================================
    echo.
    echo Please check network and try again.
)

pause
