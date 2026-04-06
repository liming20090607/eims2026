@echo off
chcp 65001 >nul
title Force Restart and Verify Import-Export
echo ========================================
echo   Force Restart and Verify
echo ========================================
echo.
echo This will:
echo   1. Stop Gunicorn
echo   2. Clear Python cache
echo   3. Start Gunicorn
echo   4. Verify import-export is working
echo.

echo Step 1: Stopping Gunicorn...
ssh root@39.106.41.239 "supervisorctl stop eims"

echo.
echo Step 2: Clearing Python cache...
ssh root@39.106.41.239 "cd /var/www/eims; find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; find . -name '*.pyc' -delete"

echo.
echo Step 3: Starting Gunicorn...
ssh root@39.106.41.239 "supervisorctl start eims"

echo.
echo Step 4: Waiting for service to start (10 seconds)...
timeout /t 10 /nobreak >nul

echo.
echo Step 5: Verifying import-export...
ssh root@39.106.41.239 "cd /var/www/eims; source venv/bin/activate; python3 << 'EOF'
import sys
sys.path.insert(0, '/var/www/eims')
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eims_app.settings')
import django
django.setup()

from eims_app.admin import EmployeeAdmin, IMPORT_EXPORT_AVAILABLE
print(f'IMPORT_EXPORT_AVAILABLE: {IMPORT_EXPORT_AVAILABLE}')
print(f'EmployeeAdmin bases: {EmployeeAdmin.__bases__}')
if hasattr(EmployeeAdmin, 'resource_classes'):
    print(f'resource_classes: {EmployeeAdmin.resource_classes}')
    print('✓ Import-Export is configured!')
else:
    print('✗ resource_classes not found!')
EOF
"

echo.
echo ========================================
echo   Restart Complete!
echo ========================================
echo.
echo NOW:
echo   1. Press Ctrl+F5 to hard refresh browser
echo   2. Visit: http://39.106.41.239:8000/admin/eims_app/employee/
echo   3. You should see [导入] button
echo.

pause
