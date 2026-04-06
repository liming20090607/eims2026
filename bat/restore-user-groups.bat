@echo off
chcp 65001 >nul
title Restore User Groups and Permissions
echo ========================================
echo   Restore User Groups and Permissions
echo ========================================
echo.

echo Step 1: Checking if backup file exists on server...
ssh root@39.106.41.239 "ls -lh /root/backup_before_phase4.json 2>&1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Backup file not found on server!
    echo Please run upload-backup-to-server.bat first.
    echo.
    pause
    exit /b 1
)

echo.
echo Step 2: Restoring user groups and permissions...
echo ========================================
echo.

ssh root@39.106.41.239 "cd /var/www/eims && source venv/bin/activate && python3 << 'PYEOF'
import sys
import os
sys.path.append('/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from django.contrib.auth.models import User, Group, Permission
import json

print('\n=== Step 1: Reading backup file ===')
backup_file = '/root/backup_before_phase4.json'

try:
    with open(backup_file, 'r', encoding='utf-8') as f:
        content = f.read()
        start = content.find('[')
        data = json.loads(content[start:])
    print(f'✓ Successfully read backup file')
except Exception as e:
    print(f'✗ Error reading file: {e}')
    sys.exit(1)

groups_data = [obj for obj in data if obj['model'] == 'auth.group']
users_data = [obj for obj in data if obj['model'] == 'auth.user']

print(f'✓ Found {len(groups_data)} groups')
print(f'✓ Found {len(users_data)} users')

print('\n=== Step 2: Clearing existing groups ===')
Group.objects.all().delete()
print('✓ Cleared all existing groups')

print('\n=== Step 3: Restoring groups ===')
for group_obj in groups_data:
    try:
        pk = group_obj['pk']
        fields = group_obj['fields']
        perm_ids = fields.get('permissions', [])
        
        group, created = Group.objects.update_or_create(
            id=pk,
            defaults={'name': fields['name']}
        )
        
        if perm_ids:
            permissions = Permission.objects.filter(id__in=perm_ids)
            group.permissions.set(permissions)
        
        status = 'Created' if created else 'Updated'
        print(f'✓ [{status}] Group: {group.name} (ID={group.id}), Permissions: {group.permissions.count()}')
        
    except Exception as e:
        print(f'✗ Error (Group ID={group_obj.get(\"pk\", \"?\")}): {e}')

print('\n=== Step 4: Restoring user-group relationships ===')
success_count = 0
error_count = 0

for user_obj in users_data:
    try:
        pk = user_obj['pk']
        fields = user_obj['fields']
        
        if pk == 1:
            continue
        
        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            print(f'⚠ Skip: User ID={pk} ({fields.get(\"username\", \"unknown\")}) does not exist')
            continue
        
        group_ids = fields.get('groups', [])
        
        if group_ids:
            groups = Group.objects.filter(id__in=group_ids)
            user.groups.set(groups)
            success_count += 1
            print(f'✓ User {user.username}: assigned to {len(group_ids)} groups')
        else:
            success_count += 1
            
    except Exception as e:
        error_count += 1
        print(f'✗ Error (User ID={user_obj.get(\"pk\", \"?\")}): {e}')

print(f'\nCompleted! Success: {success_count}, Errors: {error_count}')

print('\n=== Step 5: Verification ===')
all_groups = Group.objects.all().order_by('id')
print(f'Total groups in database: {len(all_groups)}')
for group in all_groups:
    print(f'  - ID={group.id}, Name={group.name}, Members={group.user_set.count()}, Permissions={group.permissions.count()}')

users_with_groups = User.objects.filter(groups__isnull=False).distinct()
print(f'\nUsers with group assignments: {users_with_groups.count()}')

PYEOF"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   User Groups Restored Successfully!
    echo ========================================
    echo.
    echo NOW:
    echo   1. Refresh browser (F5)
    echo   2. Go to Admin -> Auth -> Groups
    echo   3. Check Users page for group assignments
    echo.
) else (
    echo.
    echo ========================================
    echo   Restore Failed!
    echo ========================================
    echo.
    echo Please check error messages above.
)

pause
