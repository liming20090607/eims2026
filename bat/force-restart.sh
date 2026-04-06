#!/bin/bash
# Force restart and check status

echo "======================================"
echo "Force Restart Gunicorn"
echo "======================================"
echo ""

# Kill any existing gunicorn processes
echo "Stopping all Gunicorn processes..."
sudo pkill -9 gunicorn
sleep 1

# Stop in supervisor
echo "Stopping in Supervisor..."
sudo supervisorctl stop eims
sleep 1

# Start in supervisor
echo ""
echo "Starting in Supervisor..."
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

echo "Local Access Test:"
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
echo "Final Status"
echo "======================================"
echo ""

if sudo netstat -tlnp 2>/dev/null | grep -q ":8000"; then
    echo "✅ Port 8000: LISTENING"
    echo "✅ Service is ready!"
    echo ""
    echo "You can visit: http://39.106.41.239:8000/"
else
    echo "❌ Port 8000: NOT LISTENING"
    echo "❌ Service failed to start"
    echo ""
    echo "Check logs:"
    echo "sudo tail -f /var/log/eims/error.log"
fi
