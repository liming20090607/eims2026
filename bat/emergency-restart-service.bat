@echo off
chcp 65001 >nul
title Emergency Restart EIMS Service
echo ========================================
echo   Emergency Service Restart
echo ========================================
echo.

ssh root@39.106.41.239 "supervisorctl status eims; ps aux | grep gunicorn | grep -v grep; cd /var/www/eims; supervisorctl restart eims; sleep 3; supervisorctl status eims"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   Service Restarted!
    echo ========================================
    echo.
    echo NOW:
    echo   1. Wait 5 seconds for service to start
    echo   2. Press F5 to refresh browser
    echo   3. The page should load now!
    echo.
) else (
    echo.
    echo ========================================
    echo   Restart Failed!
    echo ========================================
    echo.
    echo Please check SSH connection and try again.
)

pause
