#!/bin/bash
# 检查静态文件配置

echo "========================================"
echo "  检查静态文件配置"
echo "========================================"
echo ""

cd /var/www/eims
source venv/bin/activate

echo "1. 检查 settings.py 中的静态文件配置:"
echo ""
grep -n "STATIC_URL\|STATIC_ROOT\|STATICFILES_DIRS" eims_app/settings.py

echo ""
echo "2. 检查 staticfiles 目录:"
ls -la staticfiles/ | head -10

echo ""
echo "3. 检查 admin 静态文件:"
ls -la staticfiles/admin/ | head -10

echo ""
echo "4. 检查 Nginx 配置:"
cat /etc/nginx/conf.d/eims.conf 2>/dev/null || cat /etc/nginx/nginx.conf | grep -A 10 "location /static"

echo ""
echo "========================================"
echo "  检查完成"
echo "========================================"
