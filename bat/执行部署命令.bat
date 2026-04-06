@echo off
chcp 65001 >nul
echo ======================================
echo 部署用户账号管理功能
echo ======================================
echo.
echo 请输入服务器密码（root 用户的密码）：
echo.

echo 正在执行部署命令...
ssh root@39.106.41.239 "cd /var/www/eims && source venv/bin/activate && python manage.py collectstatic --noinput && python manage.py check && sudo supervisorctl restart eims && sudo supervisorctl status eims"

echo.
echo ======================================
echo 部署完成！
echo ======================================
echo.
echo 请在浏览器访问：
echo http://xietongai.com.cn/user-management/
echo.
pause
