@echo off
chcp 65001 >nul
title Check Django Setup
echo ========================================
echo   Check Django Setup
echo ========================================
echo.

ssh root@39.106.41.239 "cd /var/www/eims; source venv/bin/activate; python manage.py check; echo '=== 最新错误日志 ==='; tail -50 /var/www/eims/logs/error.log; echo ''; echo '=== 服务状态 ==='; supervisorctl status eims"

pause
