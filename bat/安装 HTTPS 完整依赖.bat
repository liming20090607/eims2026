@echo off
chcp 65001 >nul
echo ======================================
echo 安装 HTTPS 开发环境完整依赖
echo ======================================
echo.

echo [1/2] 安装 Werkzeug...
pip install werkzeug

echo.
echo [2/2] 安装 django-extensions...
pip install django-extensions

echo.
if %ERRORLEVEL% EQU 0 (
    echo ======================================
    echo ✅ 安装完成！
    echo ======================================
    echo.
    echo 下一步：
    echo   双击 run_https.bat 启动 HTTPS 服务器
    echo   或执行：python manage.py runserver_plus --cert-file cert.pem --key-file key.pem 0.0.0.0:8000
    echo.
    pause
) else (
    echo.
    echo ======================================
    echo ❌ 安装失败
    echo ======================================
    echo.
    pause
)
