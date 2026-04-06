@echo off
chcp 65001 >nul
echo ======================================
echo 快速检查服务器 Django 版本
echo ======================================
echo.
echo 请输入服务器密码（root 用户的密码）：
echo.

ssh root@39.106.41.239 "cd /var/www/eims && source venv/bin/activate && echo 'Django 版本：' && python -m django --version && echo '' && echo 'Python 版本：' && python --version && echo '' && echo '已安装的 Django 包：' && pip list | grep -i django"

echo.
echo ======================================
echo 检查完成
echo ======================================
echo.
pause
