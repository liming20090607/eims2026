@echo off
chcp 65001 >nul
title EIMS2026 服务器
echo ========================================
echo   EIMS2026 服务器启动中...
echo ========================================
echo.
echo 服务器地址:
echo   - 电脑访问: http://localhost:8000
echo   - 手机访问: http://本机IP:8000
echo.
echo 提示: 按 Ctrl+C 停止服务器
echo ========================================
echo.
python manage.py runserver 0.0.0.0:8000
