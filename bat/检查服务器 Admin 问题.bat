@echo off
chcp 65001 >nul
echo ======================================
echo 检查服务器 Admin 样式问题
echo ======================================
echo.
echo 请输入服务器密码（root 用户的密码）：
echo.

echo 正在检查服务器配置...
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
grep -n 'USE_DARK_THEME\|ADMIN_SITE_HEADER' settings.py || echo '未找到主题配置'

echo.
echo '======================================'
echo '3. 检查静态文件目录'
echo '======================================'
ls -la staticfiles/ | head -20

echo.
echo '======================================'
echo '4. 检查 Admin 静态文件'
echo '======================================'
ls -la staticfiles/admin/css/ | head -10

echo.
echo '======================================'
echo '5. 检查 base.css 是否存在'
echo '======================================'
ls -la staticfiles/admin/css/base.css || echo 'base.css 不存在！'

echo.
echo '======================================'
echo '6. 服务状态'
echo '======================================'
sudo supervisorctl status eims

echo.
echo '======================================'
echo '7. 检查 Nginx 配置（如果有）'
echo '======================================'
if [ -f /etc/nginx/nginx.conf ]; then
    echo 'Nginx 已安装'
    nginx -v
else
    echo 'Nginx 未安装'
fi
"@

echo.
echo ======================================
echo 检查完成
echo ======================================
echo.
echo 请告诉我检查结果，特别是：
echo 1. staticfiles/admin/css/base.css 是否存在？
echo 2. settings.py 中是否有主题配置？
echo 3. 服务状态是否正常？
echo.
pause
