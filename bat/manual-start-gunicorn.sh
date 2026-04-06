#!/bin/bash
# 尝试直接启动 Gunicorn

echo "========================================"
echo "  手动启动 Gunicorn 测试"
echo "========================================"
echo ""

cd /var/www/eims
source venv/bin/activate

echo "1. 后台启动 Gunicorn:"
gunicorn --bind 0.0.0.0:8000 --workers 3 --daemon --pid /tmp/gunicorn.pid

echo ""
echo "2. 检查进程:"
ps aux | grep gunicorn

echo ""
echo "3. 测试访问:"
sleep 2
curl -I http://127.0.0.1:8000/admin/ 2>&1 | head -10

echo ""
echo "========================================"
echo "  测试完成"
echo "========================================"
