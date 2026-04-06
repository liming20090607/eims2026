#!/bin/bash
# Fix Supervisor configuration and restart

echo "======================================"
echo "Fix Supervisor Configuration"
echo "======================================"
echo ""

# Check if config directory exists
if [ ! -d "/etc/supervisord.d" ]; then
    echo "Creating supervisord.d directory..."
    sudo mkdir -p /etc/supervisord.d
fi

# Create eims.ini config
echo "Creating eims.ini configuration..."
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
echo ""

# Check if log directory exists
if [ ! -d "/var/www/eims/logs" ]; then
    echo "Creating logs directory..."
    mkdir -p /var/www/eims/logs
fi

# Reload supervisor
echo "Reloading Supervisor..."
sudo supervisorctl reread
sudo supervisorctl update
sleep 2

# Stop any existing processes
echo ""
echo "Stopping existing Gunicorn processes..."
sudo pkill -9 gunicorn 2>/dev/null || echo "No Gunicorn processes found"
sleep 1

# Start service
echo ""
echo "Starting EIMS service..."
sudo supervisorctl start eims
sleep 5

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

echo "Testing local access..."
for i in {1..5}; do
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
echo "Done"
echo "======================================"
