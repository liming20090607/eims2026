@echo off
chcp 65001 >nul
echo ======================================
echo 快速修复 Admin 样式（一条命令）
echo ======================================
echo.
echo 问题：/static/admin/css/base.css 返回 404
echo 解决：重新收集静态文件
echo.
echo 请输入服务器密码（root 用户的密码）：
echo.

echo 正在执行修复...
ssh root@39.106.41.239 "cd /var/www/eims && source venv/bin/activate && python manage.py collectstatic --clear --noinput && python manage.py collectstatic --noinput && sudo chown -R admin:admin staticfiles && sudo chmod -R 755 staticfiles && sudo supervisorctl restart eims && echo '修复完成！'"

echo.
echo ======================================
echo 修复命令已发送
echo ======================================
echo.
echo 请在浏览器中：
echo 1. 访问：http://39.106.41.239:8000/admin/
echo 2. 按 Ctrl+F5 强制刷新
echo.
pause
