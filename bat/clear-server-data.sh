#!/bin/bash
# Clear all data and restore from backup

echo "========================================"
echo "  Clear Server Data and Restore"
echo "========================================"
echo ""

cd /var/www/eims
source venv/bin/activate

echo "Step 1: Current data status"
echo "----------------------------------------"
python3 manage.py shell << 'EOF'
from eims_app import models
from django.contrib.auth.models import User

print('Current data:')
print(f'  Employees: {models.Employee.objects.count()}')
print(f'  Departments: {models.Department.objects.count()}')
print(f'  Notices: {models.Notice.objects.count()}')
print(f'  Users: {User.objects.count()}')
EOF

echo ""
echo "Step 2: Clear all data (except admin user)"
echo "----------------------------------------"
echo "This will remove all data except the admin user."
echo "Press Ctrl+C to cancel, or wait 3 seconds to continue..."
sleep 3

# 清除所有数据，但保留 admin 用户
python3 manage.py shell << 'EOF'
from django.contrib.auth.models import User
from eims_app import models

# 保存 admin 用户
admin = User.objects.filter(username='admin').first()
print(f'Admin user will be preserved: {admin}')

# 清除所有表
from django.core.management import call_command
call_command('flush', '--noinput')

# 恢复 admin 用户
if admin:
    admin.save()
    print(f'Admin user preserved: {admin.username}')
EOF

echo ""
echo "Step 3: Restore from backup"
echo "----------------------------------------"
if [ -f "local_backup_full.json" ]; then
    echo "Restoring from local_backup_full.json..."
    python3 manage.py loaddata local_backup_full.json
    echo ""
    echo "Restore completed!"
else
    echo "ERROR: local_backup_full.json not found!"
    echo "Please upload it first using scp."
    exit 1
fi

echo ""
echo "Step 4: Verify restored data"
echo "----------------------------------------"
python3 manage.py shell << 'EOF'
from eims_app import models
from django.contrib.auth.models import User

print('Restored data:')
print(f'  Employees: {models.Employee.objects.count()}')
print(f'  Departments: {models.Department.objects.count()}')
print(f'  Notices: {models.Notice.objects.count()}')
print(f'  Projects: {models.Project.objects.count()}')
print(f'  Contracts: {models.Contract.objects.count()}')
print(f'  Users: {User.objects.count()}')
print('')
print('Data restore successful!')
EOF

echo ""
echo "========================================"
echo "  All Done!"
echo "========================================"
echo ""
echo "Restarting Gunicorn..."
supervisorctl restart eims

echo ""
echo "You can now access: http://39.106.41.239:8000/"
echo ""
