#!/bin/bash
# Check Django settings and fix ROOT_URLCONF

echo "======================================"
echo "Check Django Settings"
echo "======================================"
echo ""

echo "=== Current ROOT_URLCONF setting ==="
grep -n "ROOT_URLCONF" /var/www/eims/settings.py
echo ""

echo "=== Python path in settings.py ==="
grep -n "sys.path" /var/www/eims/settings.py
echo ""

echo "=== BASE_DIR setting ==="
grep -n "BASE_DIR" /var/www/eims/settings.py | head -n 5
echo ""

echo "=== Check project structure ==="
ls -la /var/www/eims/ | head -n 20
echo ""

echo "=== Check if urls.py exists ==="
ls -la /var/www/eims/urls.py 2>/dev/null || echo "urls.py not found"
echo ""

echo "=== Check wsgi.py ==="
grep -n "os.environ.setdefault" /var/www/eims/wsgi.py
