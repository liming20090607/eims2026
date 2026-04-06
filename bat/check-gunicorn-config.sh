#!/bin/bash
# 检查 Supervisor 和 Gunicorn 配置

echo "========================================"
echo "  检查 Gunicorn 配置"
echo "========================================"
echo ""

echo "1. Supervisor 配置:"
cat /etc/supervisor/conf.d/eims.conf 2>/dev/null || cat /etc/supervisord.d/eims.ini 2>/dev/null

echo ""
echo "2. Gunicorn 配置文件:"
cat /var/www/eims/gunicorn.conf.py 2>/dev/null

echo ""
echo "3. 检查 Nginx 配置:"
nginx -T 2>&1 | grep -A 10 "location /static" || echo "Nginx 未配置静态文件"

echo ""
echo "4. 当前运行的 Gunicorn 命令:"
ps aux | grep gunicorn

echo ""
echo "========================================"
echo "  检查完成"
echo "========================================"
