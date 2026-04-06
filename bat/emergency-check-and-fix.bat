@echo off
chcp 65001 >nul
title Emergency Fix and Restart
echo ========================================
echo   Emergency Fix and Restart
echo ========================================
echo.

ssh root@39.106.41.239 "echo '=== 最新错误日志 ==='; tail -50 /var/www/eims/logs/error.log; echo ''; echo '=== 当前服务状态 ==='; supervisorctl status eims; echo ''; echo '=== Gunicorn 进程 ==='; ps aux | grep gunicorn | grep -v grep"

pause
