#!/bin/bash
# Fix ROOT_URLCONF in settings.py

echo "======================================"
echo "Fix Django Settings"
echo "======================================"
echo ""

echo "Current ROOT_URLCONF setting:"
grep -n "ROOT_URLCONF" /var/www/eims/settings.py
echo ""

echo "Fixing ROOT_URLCONF..."
sed -i "s/ROOT_URLCONF = 'EIMS2026.urls'/ROOT_URLCONF = 'urls'/g" /var/www/eims/settings.py
echo ""

echo "Running database migrations..."
cd /var/www/eims
source venv/bin/activate
python3 manage.py migrate --noinput
echo ""

echo "New ROOT_URLCONF setting:"
grep -n "ROOT_URLCONF" /var/www/eims/settings.py
echo ""

echo "Restarting Gunicorn..."
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

echo "Testing local access..."
for i in {1..5}; do
    response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 http://localhost:8000/admin/ 2>/dev/null)
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
