@echo off
chcp 65001 >nul
title EIMS2026 服务器
cls
echo ========================================
echo   EIMS2026 服务器启动
echo ========================================
echo.
echo 📁 工作目录：%CD%
echo 🚀 正在启动 Django 开发服务器...
echo.

REM 切换到项目根目录执行
cd /d "%~dp0"

REM 启动服务器
python manage.py runserver 0.0.0.0:8000

pause
