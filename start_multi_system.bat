@echo off
chcp 65001 >nul
echo ==========================================
echo   多系统架构 - 快速启动脚本
echo ==========================================
echo.
echo 正在启动Django服务器...
echo.
echo 访问地址:
echo   - 智能路由入口: http://127.0.0.1:8000/
echo   - 鼎策系统:     http://127.0.0.1:8000/dingce/
echo   - 晟昌系统:     http://127.0.0.1:8000/shengchang/
echo   - 嘉诚达系统:   http://127.0.0.1:8000/jiachengda/
echo   - Root后台:     http://127.0.0.1:8000/root/
echo.
echo 按 Ctrl+C 停止服务器
echo ==========================================
echo.

python manage.py runserver
