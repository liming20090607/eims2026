@echo off
chcp 65001 >nul
title Upload and Restore Department & Role Data
echo ========================================
echo   Upload and Restore Department & Role Data
echo ========================================
echo.

echo Step 1: Uploading files to server...
scp -C "E:\EIMS2026\department_data.json" "E:\EIMS2026\role_data.json" root@39.106.41.239:/root/

echo.
echo Step 2: Cleaning and restoring data on server...
ssh root@39.106.41.239 << 'SSHEOF'
cd /root

# Clean the JSON files (remove the first line with Python path)
echo "Cleaning department_data.json..."
python3 -c "
import json
with open('department_data.json', 'r', encoding='utf-8') as f:
    content = f.read()
start = content.find('[')
clean = content[start:]
data = json.loads(clean)
print(f'  部门数据: {len(data)} 条记录')
with open('department_data_clean.json', 'w', encoding='utf-8') as f:
    f.write(clean)
"

echo "Cleaning role_data.json..."
python3 -c "
import json
with open('role_data.json', 'r', encoding='utf-8') as f:
    content = f.read()
start = content.find('[')
clean = content[start:]
data = json.loads(clean)
print(f'  角色数据: {len(data)} 条记录')
with open('role_data_clean.json', 'w', encoding='utf-8') as f:
    f.write(clean)
"

echo ""
echo "Step 3: Restoring to database..."
cd /var/www/eims
source venv/bin/activate

# 恢复部门数据
echo ""
echo "恢复部门数据..."
python3 << 'PYEOF'
import sys
sys.path.append('/var/www/eims')
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from eims_app.models import Department
import json

with open('/root/department_data_clean.json', 'r', encoding='utf-8') as f:
    dept_data = json.load(f)

success_count = 0
error_count = 0

for obj in dept_data:
    try:
        pk = obj['pk']
        fields = obj['fields']
        
        # 将 manager 设置为 None（如果引用的用户不存在）
        if fields.get('manager'):
            fields['manager'] = None
        
        # 创建或更新部门
        dept, created = Department.objects.update_or_create(
            pk=pk,
            defaults=fields
        )
        success_count += 1
        print(f"✓ 部门 {dept.department_code} - {dept.department_name}")
        
    except Exception as e:
        error_count += 1
        print(f"✗ 错误：{e}")

print(f"\n完成！成功：{success_count}, 失败：{error_count}")
PYEOF

# 恢复角色数据
echo ""
echo "恢复角色数据..."
python3 << 'PYEOF'
import sys
sys.path.append('/var/www/eims')
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from eims_app.models import Role
import json

with open('/root/role_data_clean.json', 'r', encoding='utf-8') as f:
    role_data = json.load(f)

success_count = 0
error_count = 0

for obj in role_data:
    try:
        pk = obj['pk']
        fields = obj['fields']
        
        # 创建或更新角色
        role, created = Role.objects.update_or_create(
            pk=pk,
            defaults=fields
        )
        success_count += 1
        print(f"✓ 角色 {role.name} - {role.description}")
        
    except Exception as e:
        error_count += 1
        print(f"✗ 错误：{e}")

print(f"\n完成！成功：{success_count}, 失败：{error_count}")
PYEOF

# 验证结果
echo ""
echo "Step 4: Verifying restored data..."
python3 << 'PYEOF'
import sys
sys.path.append('/var/www/eims')
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from eims_app.models import Department, Role

print(f"\n数据库中的部门数量: {Department.objects.count()}")
print("部门列表:")
for dept in Department.objects.all().order_by('order'):
    print(f"  - {dept.department_code}: {dept.department_name} (负责人: {dept.manager_name or '未设置'})")

print(f"\n数据库中的角色数量: {Role.objects.count()}")
print("角色列表:")
for role in Role.objects.all():
    print(f"  - {role.name}: {role.description}")
PYEOF

SSHEOF

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   Data Restored Successfully!
    echo ========================================
    echo.
    echo NOW:
    echo   1. Refresh browser (F5)
    echo   2. Check Department List page
    echo   3. Check Role Configuration page
    echo.
) else (
    echo.
    echo ========================================
    echo   Restore Failed!
    echo ========================================
    echo.
    echo Please check SSH connection and try again.
)

pause
