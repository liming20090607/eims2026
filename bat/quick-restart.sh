#!/bin/bash
# Quick restart script for Gunicorn

echo "======================================"
echo "Restarting Gunicorn Service"
echo "======================================"
echo ""

# Stop
echo "Stopping Gunicorn..."
sudo supervisorctl stop eims
sleep 2

# Check if stopped
if sudo supervisorctl status eims | grep -q "STOPPED"; then
    echo "Stopped successfully"
else
    echo "Force stopping..."
    sudo supervisorctl stop eims
    sleep 1
fi

# Start
echo ""
echo "Starting Gunicorn..."
sudo supervisorctl start eims
sleep 3

# Check status
echo ""
echo "Service Status:"
sudo supervisorctl status eims

# Check process
echo ""
echo "Gunicorn Process:"
ps aux | grep -E "[g]unicorn" | head -n 3

# Check port
echo ""
echo "Port 8000:"
sudo netstat -tln 2>/dev/null | grep ":8000" || echo "Not listening yet"

# Test local access
echo ""
echo "Testing local access..."
if curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 http://localhost:8000/ > /dev/null 2>&1; then
    echo "Local access: OK"
    echo ""
    echo "======================================"
    echo "SUCCESS! Service is running"
    echo "======================================"
    echo ""
    echo "Now you can visit:"
    echo "  http://39.106.41.239:8000/admin/"
    echo ""
    echo "Remember to configure Alibaba Cloud Security Group!"
else
    echo "Local access: Waiting..."
    echo ""
    echo "Please wait a few more seconds and try again"
fi
