#!/bin/bash
# Check Gunicorn error logs

echo "======================================"
echo "Gunicorn Error Logs"
echo "======================================"
echo ""

echo "=== Last 100 lines of error log ==="
sudo tail -n 100 /var/log/eims/error.log
echo ""

echo "=== Last 50 lines of supervisord log ==="
sudo tail -n 50 /var/log/supervisor/supervisord.log
echo ""

echo "=== Supervisor config ==="
sudo cat /etc/supervisord.d/eims.ini
echo ""

echo "=== Gunicorn config ==="
sudo cat /var/www/eims/gunicorn.conf.py
echo ""

echo "=== Python environment ==="
python3 --version
which python3
echo ""

echo "=== Virtual environment ==="
ls -la /var/www/eims/venv/bin/python3.10
echo ""

echo "=== Django app status ==="
cd /var/www/eims
source venv/bin/activate
python manage.py check 2>&1 | head -n 20
