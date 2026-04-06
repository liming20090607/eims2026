@echo off
chcp 65001 >nul
echo ======================================
echo 修复服务器 Admin 样式问题
echo ======================================
echo.
echo 说明：
echo 本地显示正常，说明代码和版本都没问题
echo 服务器显示异常，说明静态文件配置有问题
echo.
echo 请输入服务器密码（root 用户的密码）：
echo.

echo 正在执行修复...
ssh root@39.106.41.239 @"
cd /var/www/eims
source venv/bin/activate

echo '======================================'
echo '步骤 1: 检查当前 Django 版本'
echo '======================================'
python -m django --version

echo.
echo '======================================'
echo '步骤 2: 查看 settings.py 中的静态文件配置'
echo '======================================'
grep -n 'STATIC_URL\|STATIC_ROOT\|STATICFILES_DIRS' settings.py

echo.
echo '======================================'
echo '步骤 3: 清空并重新收集静态文件'
echo '======================================'
echo '清空 staticfiles...'
python manage.py collectstatic --clear --noinput

echo.
echo '验证静态文件已收集...'
ls -la staticfiles/admin/css/ | head -10

echo.
echo '检查 base.css 是否存在...'
if [ -f staticfiles/admin/css/base.css ]; then
    echo '✅ base.css 存在'
    ls -la staticfiles/admin/css/base.css
else
    echo '❌ base.css 不存在！'
fi

echo.
echo '======================================'
echo '步骤 4: 设置正确的权限'
echo '======================================'
echo '设置 staticfiles 目录权限...'
sudo chown -R admin:admin staticfiles
sudo chmod -R 755 staticfiles

echo.
echo '验证权限...'
ls -ld staticfiles
ls -ld staticfiles/admin

echo.
echo '======================================'
echo '步骤 5: 重启 Gunicorn 服务'
echo '======================================'
echo '重启 eims 服务...'
sudo supervisorctl restart eims

echo.
echo '等待服务启动...'
sleep 3

echo.
echo '查看服务状态...'
sudo supervisorctl status eims

echo.
echo '======================================'
echo '步骤 6: 检查 Nginx 配置（如果使用）'
echo '======================================'
if [ -f /etc/nginx/nginx.conf ]; then
    echo 'Nginx 已安装，检查配置...'
    nginx -t
    
    if [ -f /etc/nginx/sites-available/eims ]; then
        echo '检查 eims 站点配置...'
        grep -A 5 'location /static' /etc/nginx/sites-available/eims || echo '未找到 static 配置'
    else
        echo 'eims 站点配置文件不存在'
    fi
else
    echo 'Nginx 未安装（Django 开发服务器直接处理静态文件）'
fi

echo.
echo '======================================'
echo '修复完成！'
echo '======================================'
echo.
echo '请执行以下操作：'
echo 1. 访问：http://39.106.41.239:8000/admin/'
echo 2. 按 Ctrl+F5 强制刷新'
echo 3. 清除浏览器缓存'
echo 4. 使用无痕模式测试'
echo.
echo '如果仍然不正常，请告诉我：'
echo - base.css 是否存在？'
echo - Nginx 是否安装？'
echo - 服务状态是否正常？'
"@

echo.
echo ======================================
echo 修复命令已执行！
echo ======================================
echo.
echo 请在浏览器中：
echo 1. 访问：http://39.106.41.239:8000/admin/
echo 2. 按 Ctrl+F5 强制刷新
echo 3. 查看样式是否正常
echo.
pause
