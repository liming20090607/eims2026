@echo off
chcp 65001 >nul
echo ======================================
echo 修复 Django Admin 样式问题
echo ======================================
echo.
echo 请输入服务器密码（root 用户的密码）：
echo.

echo 步骤 1: 检查静态文件目录...
ssh root@39.106.41.239 "ls -la /var/www/eims/staticfiles/"

echo.
echo ======================================
echo 步骤 2: 检查 Django 配置...
ssh root@39.106.41.239 "grep -A 5 'STATIC_URL' /var/www/eims/settings.py"

echo.
echo ======================================
echo 步骤 3: 重新收集静态文件...
ssh root@39.106.41.239 "cd /var/www/eims && source venv/bin/activate && python manage.py collectstatic --clear --noinput"

echo.
echo ======================================
echo 步骤 4: 重启服务...
ssh root@39.106.41.239 "sudo supervisorctl restart eims"

echo.
echo ======================================
echo 修复完成！
echo ======================================
echo.
echo 请刷新浏览器页面（Ctrl+F5 强制刷新）
echo 访问：http://39.106.41.239:8000/admin/
echo.
pause
