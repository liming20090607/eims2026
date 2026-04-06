@echo off
chcp 65001 >nul
echo ======================================
echo 快速检查服务器 Django Admin 状态
echo ======================================
echo.
echo 请输入服务器密码（root 用户的密码）：
echo.

ssh root@39.106.41.239 @"
echo '======================================'
echo '1. Django 版本'
echo '======================================'
cd /var/www/eims
source venv/bin/activate
python -m django --version

echo.
echo '======================================'
echo '2. settings.py 配置检查'
echo '======================================'
echo '检查 ADMIN_SITE_HEADER:'
grep -n 'ADMIN_SITE_HEADER' settings.py || echo '❌ 未配置'

echo.
echo '检查 USE_DARK_THEME（不应存在）:'
grep -n 'USE_DARK_THEME' settings.py && echo '⚠️ 发现不兼容配置！' || echo '✅ 无不兼容配置'

echo.
echo '检查 settings.py 语法:'
python -c \"import settings; print('✅ 语法正确')\" 2>&1 || echo '❌ 语法错误！'

echo.
echo '查看 settings.py 末尾 10 行:'
tail -10 settings.py

echo.
echo '======================================'
echo '3. 静态文件检查'
echo '======================================'
echo 'staticfiles 目录:'
if [ -d staticfiles ]; then
    ls -la staticfiles/ | head -5
    echo ''
    echo 'admin 目录:'
    if [ -d staticfiles/admin ]; then
        ls -la staticfiles/admin/ | head -5
        echo ''
        echo 'CSS 文件:'
        ls -la staticfiles/admin/css/ | head -10
        echo ''
        if [ -f staticfiles/admin/css/base.css ]; then
            echo '✅ base.css 存在'
        else
            echo '❌ base.css 不存在！'
        fi
    else
        echo '❌ staticfiles/admin 目录不存在！'
    fi
else
    echo '❌ staticfiles 目录不存在！'
fi

echo.
echo '======================================'
echo '4. 服务状态'
echo '======================================'
sudo supervisorctl status eims

echo.
echo '======================================'
echo '5. 进程监听端口'
echo '======================================'
sudo netstat -tlnp | grep ':8000\|:80' || echo '未找到监听端口'

echo.
echo '======================================'
echo '6. 最近日志（最后 20 行）'
echo '======================================'
sudo journalctl -u eims -n 20 --no-pager | tail -20

echo.
echo '======================================'
echo '✅ 检查完成！'
echo '======================================'
echo.
"@

pause
