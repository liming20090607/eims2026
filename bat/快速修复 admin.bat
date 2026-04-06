@echo off
chcp 65001 >nul
echo ======================================
echo 快速修复 Django Admin 样式
echo ======================================
echo.
echo 请输入服务器密码（root 用户的密码）：
echo.

echo 正在重新收集静态文件...
ssh root@39.106.41.239 "cd /var/www/eims && source venv/bin/activate && python manage.py collectstatic --clear --noinput"

echo.
echo ======================================
echo 设置静态文件目录权限...
ssh root@39.106.41.239 "sudo chown -R admin:admin /var/www/eims/staticfiles && sudo chmod -R 755 /var/www/eims/staticfiles"

echo.
echo ======================================
echo 重启服务...
ssh root@39.106.41.239 "sudo supervisorctl restart eims"

echo.
echo ======================================
echo 修复完成！
echo ======================================
echo.
echo 请按以下步骤操作：
echo 1. 打开浏览器
echo 2. 访问：http://39.106.41.239:8000/admin/
echo 3. 按 Ctrl+F5 强制刷新缓存
echo.
echo 如果仍有问题，请查看修复方案文档：
echo E:\EIMS2026\Admin 样式修复方案.md
echo.
pause
