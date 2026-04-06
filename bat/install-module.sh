#!/bin/bash
# Install missing django_extensions module

echo "======================================"
echo "Install Missing Module"
echo "======================================"
echo ""

echo "Installing django-extensions..."
cd /var/www/eims
source venv/bin/activate
pip install django-extensions

echo ""
echo "Module installed!"
echo ""

echo "======================================"
echo "Restarting Gunicorn"
echo "======================================"
echo ""

# Restart using supervisor
supervisorctl restart eims
sleep 5

echo ""
echo "======================================"
echo "Status Check"
echo "======================================"
echo ""

echo "Supervisor Status:"
supervisorctl status eims
echo ""

echo "Gunicorn Processes:"
ps aux | grep -E "[g]unicorn" | head -n 5
echo ""

echo "Port 8000:"
netstat -tlnp 2>/dev/null | grep ":8000" || echo "NOT LISTENING"
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
