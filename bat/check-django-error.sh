#!/bin/bash
# Check Django error logs

echo "======================================"
echo "Django Error Logs"
echo "======================================"
echo ""

echo "=== Last 100 lines of Gunicorn error log ==="
tail -n 100 /var/www/eims/logs/gunicorn-error.log
echo ""

echo "=== Last 50 lines of Supervisor log ==="
tail -n 50 /var/log/supervisor/supervisord.log
echo ""

echo "=== Current Gunicorn processes ==="
ps aux | grep -E "[g]unicorn" | head -n 10
echo ""

echo "=== Port 8000 status ==="
netstat -tlnp 2>/dev/null | grep ":8000" || echo "NOT LISTENING"
