@echo off
chcp 65001 >nul
title EIMS2026 HTTPS 服务器
cls
echo ========================================
echo   EIMS2026 HTTPS 开发服务器
echo ========================================
echo.
echo 📁 工作目录：%CD%
echo 🔒 正在启动 HTTPS 开发服务器...
echo.
echo 提示：
echo   - 首次运行会自动生成 SSL 证书
echo   - 浏览器可能会提示证书不受信任（正常）
echo   - 访问地址：https://localhost:8000
echo.

REM 切换到项目根目录
cd /d "%~dp0"

REM 安装 django-extensions（如果未安装）
pip show django-extensions >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [安装] 正在安装 django-extensions...
    pip install django-extensions
)

REM 启动 HTTPS 服务器
echo.
echo 🚀 启动服务器...
python manage.py runserver_plus --cert-file cert.pem --key-file key.pem 0.0.0.0:8000

pause
