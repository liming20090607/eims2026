#!/bin/bash
# 检查 Gunicorn 错误日志

echo "========================================"
echo "  检查 Gunicorn 错误"
echo "========================================"
echo ""

echo "1. Supervisor 错误日志:"
tail -50 /var/www/eims/logs/gunicorn-error.log

echo ""
echo "2. Gunicorn 输出日志:"
tail -50 /var/www/eims/logs/gunicorn-out.log

echo ""
echo "3. 尝试手动启动 Gunicorn 查看错误:"
cd /var/www/eims
source venv/bin/activate
python manage.py check 2>&1 | head -30

echo ""
echo "========================================"
echo "  检查完成"
echo "========================================"
