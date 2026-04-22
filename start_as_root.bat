@echo off
chcp 65001 >nul
echo ========================================
echo   EIMS2026 超级管理员快速启动
echo ========================================
echo.
echo 正在启动 Django 服务器...
echo.

cd /d %~dp0
python manage.py runserver 0.0.0.0:8000

pause
