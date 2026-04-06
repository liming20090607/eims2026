@echo off
chcp 65001 >nul
echo ======================================
echo 安装 HTTPS 开发支持
echo ======================================
echo.
echo 正在安装 django-extensions...
echo.

pip install django-extensions

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ======================================
    echo ✅ 安装成功！
    echo ======================================
    echo.
    echo 下一步：
    echo   1. 双击 run_https.bat 启动 HTTPS 服务器
    echo   2. 访问 https://localhost:8000
    echo   3. 首次运行会自动生成 SSL 证书
    echo.
) else (
    echo.
    echo ======================================
    echo ❌ 安装失败
    echo ======================================
    echo.
    echo 请检查：
    echo   1. Python 是否正确安装
    echo   2. pip 是否可用
    echo   3. 网络连接是否正常
    echo.
)

pause
