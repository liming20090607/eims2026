@echo off
chcp 65001 >nul
title EIMS2026 本地开发服务器
cls

echo ========================================
echo   EIMS2026 本地开发服务器
echo ========================================
echo.
echo 📁 项目目录: %CD%
echo 🌐 访问地址: http://127.0.0.1:8000
echo 🔧 Django 版本: 
python -c "import django; print(django.get_version())" 2>nul
echo.
echo ⚠️  按 Ctrl+C 停止服务器
echo.
echo ========================================
echo.

REM 切换到项目根目录
cd /d "%~dp0"

REM 检查虚拟环境
if exist "venv\Scripts\activate.bat" (
    echo ✅ 激活虚拟环境...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  未找到虚拟环境，使用系统 Python
)

echo.
echo 🚀 正在启动 Django 开发服务器...
echo.

REM 启动服务器
python manage.py runserver 0.0.0.0:8000

pause
