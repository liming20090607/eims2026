#!/bin/bash
# Quick fix for import-export templates

echo "========================================"
echo "  Fixing Import-Export Templates"
echo "========================================"
echo ""

cd /var/www/eims
source venv/bin/activate

echo "1. Checking current version..."
pip show django-import-export | grep Version

echo ""
echo "2. Downgrading to version 3.3.7 (stable)..."
pip install django-import-export==3.3.7 --force-reinstall

echo ""
echo "3. Clearing cache..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null

echo ""
echo "4. Restarting Gunicorn..."
supervisorctl restart eims

echo ""
echo "========================================"
echo "  Fix Complete!"
echo "========================================"
echo ""
echo "Please refresh browser (Ctrl+F5)"
echo "and visit: http://39.106.41.239:8000/admin/eims_app/employee/"
echo ""
