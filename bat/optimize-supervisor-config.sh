#!/bin/bash
# 优化 Supervisor 配置

echo "========================================"
echo "  优化 Supervisor 配置"
echo "========================================"
echo ""

# 写入优化后的配置
cat > /etc/supervisor/conf.d/eims.conf << 'EOF'
[program:eims]
command=/var/www/eims/venv/bin/gunicorn --config /var/www/eims/gunicorn.conf.py wsgi:application
directory=/var/www/eims
user=admin
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
numprocs=1
redirect_stderr=true
stdout_logfile=/var/www/eims/logs/gunicorn-out.log
stderr_logfile=/var/www/eims/logs/gunicorn-error.log
environment=DJANGO_SETTINGS_MODULE="settings",PATH="/var/www/eims/venv/bin"
EOF

echo "✓ 配置文件已更新"

# 重启 Supervisor
supervisorctl reread
supervisorctl update
supervisorctl restart eims

# 等待
echo ""
echo "等待服务启动..."
sleep 5

# 检查状态
echo ""
echo "=== 服务状态 ==="
supervisorctl status eims

echo ""
echo "=== Gunicorn 进程 ==="
ps aux | grep gunicorn | grep -v grep

echo ""
echo "========================================"
echo "  完成!"
echo "========================================"
echo ""
echo "现在请:"
echo "1. 按 Ctrl+F5 强制刷新浏览器"
echo "2. 访问 http://39.106.41.239:8000/admin/eims_app/employee/"
echo "3. 应该能稳定看到导入按钮了!"
echo ""
