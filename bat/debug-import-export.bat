@echo off
chcp 65001 >nul
title Debug Import-Export Issue
echo ========================================
echo   Debug Import-Export Issue
echo ========================================
echo.
echo Running detailed diagnostics on server...
echo.

ssh root@39.106.41.239 "cd /var/www/eims; source venv/bin/activate; python3 << 'PYEOF'
import sys
import traceback

print('=' * 60)
print('Django Import-Export Debug Report')
print('=' * 60)
print()

# 1. Check installation
print('1. Checking installation...')
try:
    import import_export
    print(f'   ✓ django-import-export installed')
    print(f'     Version: {import_export.__version__}')
    print(f'     Location: {import_export.__file__}')
except Exception as e:
    print(f'   ✗ Import failed: {e}')

print()

# 2. Try importing admin classes
print('2. Testing admin import...')
try:
    from import_export.admin import ImportExportModelAdmin
    print(f'   ✓ ImportExportModelAdmin imported successfully')
except Exception as e:
    print(f'   ✗ Import failed: {e}')
    traceback.print_exc()

print()

# 3. Try importing resources
print('3. Testing resources import...')
try:
    from import_export import resources
    print(f'   ✓ resources imported successfully')
except Exception as e:
    print(f'   ✗ Import failed: {e}')

print()

# 4. Check admin.py configuration
print('4. Checking admin.py configuration...')
try:
    sys.path.insert(0, '/var/www/eims')
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eims_app.settings')
    
    import django
    django.setup()
    
    from eims_app import admin
    print(f'   ✓ admin.py loaded successfully')
    print(f'   ✓ IMPORT_EXPORT_AVAILABLE = {getattr(admin, \"IMPORT_EXPORT_AVAILABLE\", False)}')
    
    # Check if Resource classes exist
    if hasattr(admin, 'EmployeeResource'):
        print(f'   ✓ EmployeeResource exists')
    else:
        print(f'   ✗ EmployeeResource NOT found')
    
    if hasattr(admin, 'ProjectResource'):
        print(f'   ✓ ProjectResource exists')
    else:
        print(f'   ✗ ProjectResource NOT found')
    
    if hasattr(admin, 'ContractResource'):
        print(f'   ✓ ContractResource exists')
    else:
        print(f'   ✗ ContractResource NOT found')
    
except Exception as e:
    print(f'   ✗ Error loading admin.py: {e}')
    traceback.print_exc()

print()

# 5. Check registered admin classes
print('5. Checking registered admin classes...')
try:
    from django.contrib import admin as django_admin
    from eims_app.models import Employee, Project, Contract
    
    # Check Employee admin
    employee_admin = django_admin.site._registry.get(Employee)
    if employee_admin:
        print(f'   ✓ EmployeeAdmin registered')
        print(f'     Class: {employee_admin.__class__}')
        print(f'     Bases: {employee_admin.__class__.__bases__}')
        if hasattr(employee_admin, 'resource_classes'):
            print(f'     resource_classes: {employee_admin.resource_classes}')
        else:
            print(f'     ✗ NO resource_classes')
    
    # Check Project admin
    project_admin = django_admin.site._registry.get(Project)
    if project_admin:
        print(f'   ✓ ProjectAdmin registered')
        print(f'     Class: {project_admin.__class__}')
        print(f'     Bases: {project_admin.__class__.__bases__}')
    
    # Check Contract admin
    contract_admin = django_admin.site._registry.get(Contract)
    if contract_admin:
        print(f'   ✓ ContractAdmin registered')
        print(f'     Class: {contract_admin.__class__}')
        print(f'     Bases: {contract_admin.__class__.__bases__}')
    
except Exception as e:
    print(f'   ✗ Error: {e}')
    traceback.print_exc()

print()
print('=' * 60)
print('Debug Report Complete')
print('=' * 60)
PYEOF
"

echo.
pause
