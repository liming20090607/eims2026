@echo off
chcp 65001 >nul
title Check Service Status
echo ========================================
echo   Check Service Status
echo ========================================
echo.

ssh root@39.106.41.239 "supervisorctl status eims; ps aux | grep gunicorn"

pause
