@echo off
chcp 65001 >nul
title Check Database Status
echo ========================================
echo   Check Database Data Status
echo ========================================
echo.
echo Checking remote database...
echo.
ssh root@39.106.41.239 "cd /var/www/eims; source venv/bin/activate; python3 manage.py shell << 'EOF'
from eims_app.models import *
print('=== Database Status ===')
print(f'Projects: {Project.objects.count()}')
print(f'Employees: {Employee.objects.count()}')
print(f'Departments: {Department.objects.count()}')
print(f'Notices: {Notice.objects.count()}')
print(f'Users: {User.objects.count()}')
print('')
print('=== Recent Projects ===')
for p in Project.objects.all()[:5]:
    print(f'- {p.project_name}')
print('')
print('=== Employees ===')
for e in Employee.objects.all()[:5]:
    print(f'- {e.name} ({e.department})')
EOF
"

pause
