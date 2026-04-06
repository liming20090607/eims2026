@echo off
chcp 65001 >nul
echo ======================================
echo 深度诊断服务器 Admin 问题
echo ======================================
echo.
echo 请输入服务器密码（root 用户的密码）：
echo.

echo 正在执行深度检查...
ssh root@39.106.41.239 @"
cd /var/www/eims
source venv/bin/activate

echo '======================================'
echo '1. Django 版本'
echo '======================================'
python -m django --version

echo.
echo '======================================'
echo '2. 检查 settings.py 配置'
echo '======================================'
echo 'STATIC_URL:'
grep -n '^STATIC_URL' settings.py || echo '未设置'
echo ''
echo 'STATIC_ROOT:'
grep -n '^STATIC_ROOT' settings.py || echo '未设置'
echo ''
echo 'DEBUG:'
grep -n '^DEBUG' settings.py || echo '未设置'

echo.
echo '======================================'
echo '3. 查看完整的 staticfiles 目录结构'
echo '======================================'
if [ -d staticfiles ]; then
    echo 'staticfiles 目录存在'
    ls -la staticfiles/
    echo ''
    echo 'admin 目录:'
    if [ -d staticfiles/admin ]; then
        ls -la staticfiles/admin/
        echo ''
        echo 'admin/css 目录:'
        ls -la staticfiles/admin/css/
        echo ''
        echo 'base.css 文件详情:'
        ls -lh staticfiles/admin/css/base.css 2>/dev/null || echo 'base.css 不存在！'
    else
        echo 'admin 目录不存在！'
    fi
else
    echo 'staticfiles 目录不存在！'
fi

echo.
echo '======================================'
echo '4. 尝试手动收集静态文件（详细模式）'
echo '======================================'
python manage.py collectstatic --noinput --verbosity 2 2>&1 | tail -50

echo.
echo '======================================'
echo '5. 检查收集后的文件'
echo '======================================'
echo '总文件数:'
find staticfiles -type f | wc -l
echo ''
echo 'Admin CSS 文件:'
find staticfiles/admin -name '*.css' 2>/dev/null | head -10 || echo '无 CSS 文件'

echo.
echo '======================================'
echo '6. 检查服务状态和日志'
echo '======================================'
sudo supervisorctl status eims
echo ''
echo '最近错误日志（最后 20 行）:'
sudo tail -20 /var/log/supervisor/eims.err.log 2>/dev/null || echo '日志文件不存在'

echo.
echo '======================================'
echo '7. 检查 Gunicorn 绑定地址'
echo '======================================'
ps aux | grep gunicorn | grep -v grep
echo ''
echo '监听端口:'
sudo netstat -tlnp | grep :8000 || sudo ss -tlnp | grep :8000 || echo '无法查看端口'

echo.
echo '======================================'
echo '8. 测试访问静态文件'
echo '======================================'
echo '尝试访问 Django 静态文件 URL...'
curl -I http://127.0.0.1:8000/static/admin/css/base.css 2>&1 | head -5 || echo '无法访问'

echo.
echo '======================================'
echo '诊断完成！'
echo '======================================'
echo.
echo '请告诉我以下信息：'
echo 1. base.css 是否存在？文件大小是多少？'
echo 2. staticfiles 目录中有多少文件？'
echo 3. 服务状态是 RUNNING 还是其他？'
echo 4. curl 测试返回什么状态码？'
"@

echo.
echo ======================================
echo 诊断完成
echo ======================================
echo.
pause
