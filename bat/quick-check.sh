#!/bin/bash
# Simple check script for import-export

echo "========================================"
echo "  Import-Export Quick Check"
echo "========================================"
echo ""

cd /var/www/eims
source venv/bin/activate

echo "1. Checking package installation..."
pip show django-import-export | grep "Name:\|Version:"

echo ""
echo "2. Checking admin.py configuration..."
echo "Looking for ImportExportModelAdmin:"
grep -n "ImportExportModelAdmin" eims_app/admin.py

echo ""
echo "Looking for Resource classes:"
grep -n "class.*Resource" eims_app/admin.py

echo ""
echo "3. Testing Django import..."
export DJANGO_SETTINGS_MODULE=eims_app.settings
python3 -c "
import django
django.setup()
from eims_app.admin import EmployeeAdmin, IMPORT_EXPORT_AVAILABLE
print(f'IMPORT_EXPORT_AVAILABLE: {IMPORT_EXPORT_AVAILABLE}')
print(f'EmployeeAdmin bases: {EmployeeAdmin.__bases__}')
if hasattr(EmployeeAdmin, 'resource_classes'):
    print(f'✓ resource_classes configured: {EmployeeAdmin.resource_classes}')
else:
    print('✗ resource_classes NOT configured')
"

echo ""
echo "4. Restarting Gunicorn..."
supervisorctl restart eims

echo ""
echo "========================================"
echo "  Check Complete!"
echo "========================================"
echo ""
echo "NOW: Open browser and press Ctrl+F5"
echo "Then visit: http://39.106.41.239:8000/admin/eims_app/employee/"
echo ""
