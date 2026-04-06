@echo off
chcp 65001 >nul
echo ======================================
echo 测试本地 Django Admin 样式
echo ======================================
echo.

echo 当前 Django 版本：
python -m django --version

echo.
echo ======================================
echo 启动 Django 开发服务器...
echo ======================================
echo.
echo 提示：
echo 1. 服务器启动后，访问：http://localhost:8000/admin/
echo 2. 检查 Admin 样式是否正常
echo 3. 应该看到：蓝色/灰色样式，无黑块
echo 4. 按 Ctrl+C 停止服务器
echo.
echo 按任意键启动服务器...
pause >nul

echo.
echo 正在启动...
python manage.py runserver

echo.
echo ======================================
echo 服务器已停止
echo ======================================
echo.
pause
