#!/bin/bash
# 找到 settings.py 并检查静态文件配置

echo "========================================"
echo "  查找 settings.py"
echo "========================================"
echo ""

# 查找 settings.py
echo "1. 查找 settings.py 位置:"
find /var/www/eims -name "settings.py" 2>/dev/null

echo ""
echo "2. 查看项目结构:"
ls -la /var/www/eims/

echo ""
echo "3. 检查 settings.py 配置:"
SETTINGS_FILE=$(find /var/www/eims -name "settings.py" | head -1)
if [ -n "$SETTINGS_FILE" ]; then
    echo "找到 settings.py: $SETTINGS_FILE"
    echo ""
    grep -n "STATIC_URL\|STATIC_ROOT\|STATICFILES_DIRS" "$SETTINGS_FILE"
fi

echo ""
echo "4. 检查 Nginx 配置:"
nginx -T 2>/dev/null | grep -A 5 "location /static" || cat /etc/nginx/nginx.conf

echo ""
echo "========================================"
echo "  检查完成"
echo "========================================"
