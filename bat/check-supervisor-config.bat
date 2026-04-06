@echo off
chcp 65001 >nul
title Check Supervisor Config and Process
echo ========================================
echo   Check Configuration and Process
echo ========================================
echo.

ssh root@39.106.41.239 "echo '=== 当前 Supervisor 配置 ==='; cat /etc/supervisor/conf.d/eims.conf; echo ''; echo '=== Gunicorn 进程 ==='; ps aux | grep gunicorn | grep -v grep; echo ''; echo '=== 服务状态 ==='; supervisorctl status eims"

pause
