@echo off
chcp 65001 >nul
title EIMS2026 服务器
cls
echo ========================================
echo   EIMS2026 服务器启动
echo ========================================
echo.
python manage.py runserver 0.0.0.0:8000
pause
