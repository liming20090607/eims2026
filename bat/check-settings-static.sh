#!/bin/bash
# 检查 settings.py 的静态文件配置

echo "========================================"
echo "  检查 settings.py 静态文件配置"
echo "========================================"
echo ""

cd /var/www/eims
source venv/bin/activate

echo "1. STATIC_URL 配置:"
grep -n "^STATIC_URL\|^STATIC_ROOT\|^STATICFILES_DIRS" settings.py

echo ""
echo "2. 检查 DEBUG 配置:"
grep -n "^DEBUG\s*=" settings.py

echo ""
echo "3. 检查 ALLOWED_HOSTS:"
grep -n "^ALLOWED_HOSTS" settings.py

echo ""
echo "4. 实际访问静态文件 URL:"
python3 -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()
from django.conf import settings
print(f'STATIC_URL: {settings.STATIC_URL}')
print(f'STATIC_ROOT: {settings.STATIC_ROOT}')
print(f'STATICFILES_DIRS: {getattr(settings, \"STATICFILES_DIRS\", [])}')
"

echo ""
echo "========================================"
echo "  检查完成"
echo "========================================"
