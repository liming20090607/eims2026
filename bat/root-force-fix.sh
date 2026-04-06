#!/bin/bash
# Force fix using root - Complete cleanup and restart

echo "======================================"
echo "Root Force Fix - Complete Restart"
echo "======================================"
echo ""

# Stop supervisor first
echo "Stopping Supervisor..."
sudo systemctl stop supervisord
sleep 2

# Kill all gunicorn
echo "Killing all Gunicorn processes..."
sudo pkill -9 gunicorn
sleep 1

# Remove old config
echo "Removing old configuration..."
sudo rm -f /etc/supervisord.d/eims.ini
sleep 1

# Create new config
echo "Creating new configuration..."
sudo tee /etc/supervisord.d/eims.ini > /dev/null << 'EOF'
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
stdout_logfile=/var/www/eims/logs/gunicorn-supervisor.log
stderr_logfile=/var/www/eims/logs/gunicorn-error.log
EOF

echo "Configuration created!"

# Create logs directory
echo ""
echo "Creating logs directory..."
mkdir -p /var/www/eims/logs
sudo chown admin:admin /var/www/eims/logs

# Start supervisor
echo ""
echo "Starting Supervisor..."
sudo systemctl start supervisord
sleep 3

# Check status
echo ""
echo "======================================"
echo "Status Check"
echo "======================================"
echo ""

echo "Supervisor Status:"
sudo supervisorctl status eims
echo ""

echo "Gunicorn Processes:"
ps aux | grep -E "[g]unicorn" | head -n 5
echo ""

echo "Port 8000:"
sudo netstat -tlnp 2>/dev/null | grep ":8000" || echo "NOT LISTENING"
echo ""

# Test access multiple times
echo "Testing local access (10 attempts)..."
for i in {1..10}; do
    response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 http://localhost:8000/ 2>/dev/null)
    if [ "$response" != "000" ]; then
        echo "Attempt $i: HTTP $response - SUCCESS!"
        break
    else
        echo "Attempt $i: Waiting..."
        sleep 2
    fi
done

echo ""
echo "======================================"
echo "Final Status"
echo "======================================"
echo ""

if sudo netstat -tlnp 2>/dev/null | grep -q ":8000"; then
    echo "✅ Port 8000: LISTENING"
    echo "✅ Service is ready!"
    echo ""
    echo "Visit: http://39.106.41.239:8000/"
else
    echo "❌ Port 8000: NOT LISTENING"
    echo ""
    echo "Checking error logs..."
    echo ""
    echo "=== Last 50 lines of gunicorn error log ==="
    sudo tail -n 50 /var/www/eims/logs/gunicorn-error.log 2>/dev/null || echo "Log not found"
    echo ""
    echo "=== Last 30 lines of supervisor log ==="
    sudo tail -n 30 /var/log/supervisor/supervisord.log
fi
