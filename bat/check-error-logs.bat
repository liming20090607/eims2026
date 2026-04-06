@echo off
chcp 65001 >nul
title Check Gunicorn Error Logs
echo ========================================
echo   Check Error Logs
echo ========================================
echo.

ssh root@39.106.41.239 "tail -100 /var/www/eims/logs/error.log; echo '---'; tail -100 /var/www/eims/logs/gunicorn-error.log; echo '---'; ps aux | grep gunicorn | grep -v grep"

pause
