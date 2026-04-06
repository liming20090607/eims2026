@echo off
chcp 65001 >nul
echo ======================================
echo 修复 Admin 静态文件 404 错误
echo ======================================
echo.
echo 问题：Django Admin 的 CSS 文件返回 404
echo 原因：静态文件未正确收集
echo.
echo 请输入服务器密码（root 用户的密码）：
echo.

echo 正在执行修复命令...
ssh root@39.106.41.239 @"
cd /var/www/eims
source venv/bin/activate

echo '======================================'
echo '步骤 1: 清空静态文件...'
echo '======================================'
python manage.py collectstatic --clear --noinput

echo.
echo '======================================'
echo '步骤 2: 重新收集静态文件（详细模式）...'
echo '======================================'
python manage.py collectstatic --noinput --verbosity 2

echo.
echo '======================================'
echo '步骤 3: 检查静态文件目录...'
echo '======================================'
ls -la staticfiles/
ls -la staticfiles/admin/

echo.
echo '======================================'
echo '步骤 4: 设置权限...'
echo '======================================'
chown -R admin:admin staticfiles
chmod -R 755 staticfiles

echo.
echo '======================================'
echo '步骤 5: 重启服务...'
echo '======================================'
supervisorctl restart eims

echo.
echo '======================================'
echo '步骤 6: 查看服务状态...'
echo '======================================'
supervisorctl status eims

echo.
echo '======================================'
echo '修复完成！'
echo '======================================'
echo.
echo '请刷新浏览器：http://39.106.41.239:8000/admin/'
echo '按 Ctrl+F5 强制刷新'
"@

echo.
echo ======================================
echo 修复命令已执行！
echo ======================================
echo.
echo 请在浏览器中：
echo 1. 访问：http://39.106.41.239:8000/admin/
echo 2. 按 Ctrl+F5 强制刷新
echo 3. 查看是否还有 404 错误
echo.
pause
