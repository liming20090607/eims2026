@echo off
chcp 65001 >nul
echo.
echo ========================================
echo 🚀 EIMS系统启动器
echo ========================================
echo.

echo [1/2] 验证数据库配置...
python validate_db.py
if errorlevel 1 (
    echo.
    echo ❌ 数据库验证失败，服务器未启动
    pause
    exit /b 1
)

echo.
echo [2/2] 启动Django服务器...
echo.
python manage.py runserver 0.0.0.0:8000
