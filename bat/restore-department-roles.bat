@echo off
chcp 65001 >nul
title Restore Department Role Data
echo ========================================
echo   Restore Department Role Data
echo ========================================
echo.

ssh root@39.106.41.239 << 'SSHEOF'
cd /var/www/eims
source venv/bin/activate

echo "=== 开始恢复部门角色数据 ==="

python3 << 'PYEOF'
import sys
import os
sys.path.append('/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from eims_app.models import Department, DepartmentRole
from django.contrib.auth.models import User

print("\n步骤 1: 检查当前数据库状态")
print("=" * 60)
print(f"部门数量: {Department.objects.count()}")
print(f"部门角色数量: {DepartmentRole.objects.count()}")
print(f"用户数量: {User.objects.count()}")

print("\n当前部门列表:")
for dept in Department.objects.all().order_by('id'):
    print(f"  ID={dept.id}, Code={dept.department_code}, Name={dept.department_name}")

print("\n当前用户列表 (前10个):")
for user in User.objects.all().order_by('id')[:10]:
    print(f"  ID={user.id}, Username={user.username}, Name={user.first_name or ''} {user.last_name or ''}")

print("\n步骤 2: 清除现有部门角色数据")
print("=" * 60)
DepartmentRole.objects.all().delete()
print("✓ 已清除所有现有部门角色数据")

print("\n步骤 3: 创建部门角色")
print("=" * 60)

# 从备份中恢复的数据
# 注意：department=1 对应监理部，user=11 需要确认是否存在
try:
    # 尝试获取部门（ID=1）
    dept = Department.objects.get(id=1)
    print(f"✓ 找到部门: {dept.department_code} - {dept.department_name}")
except Department.DoesNotExist:
    print("✗ 未找到 ID=1 的部门，使用第一个部门")
    dept = Department.objects.first()
    if not dept:
        print("✗ 错误：数据库中没有任何部门！")
        sys.exit(1)
    print(f"✓ 使用部门: {dept.department_code} - {dept.department_name}")

# 尝试获取用户（ID=11）
try:
    user = User.objects.get(id=11)
    print(f"✓ 找到用户: ID={user.id}, Username={user.username}")
except User.DoesNotExist:
    print("✗ 未找到 ID=11 的用户，尝试使用部门负责人")
    # 如果部门有负责人，使用负责人
    if dept.manager:
        user = dept.manager
        print(f"✓ 使用部门负责人: {user.username}")
    else:
        # 否则使用第一个超级用户
        user = User.objects.filter(is_superuser=True).first()
        if user:
            print(f"✓ 使用超级用户: {user.username}")
        else:
            print("✗ 错误：找不到合适的用户！")
            sys.exit(1)

# 创建部门角色
dept_role = DepartmentRole.objects.create(
    department=dept,
    user=user,
    role_type='manager',
    role_name='监理部主任',
    is_primary=False,
    permissions='view,edit,submit'
)

print(f"\n✓ 成功创建部门角色:")
print(f"  部门: {dept_role.department.department_name}")
print(f"  用户: {dept_role.user.username}")
print(f"  角色: {dept_role.role_name}")
print(f"  类型: {dept_role.get_role_type_display()}")

print("\n步骤 4: 验证结果")
print("=" * 60)
all_dept_roles = DepartmentRole.objects.all()
print(f"数据库中共有 {len(all_dept_roles)} 个部门角色:")
for dr in all_dept_roles:
    print(f"  - {dr.department.department_name}: {dr.user.username} - {dr.role_name} ({dr.get_role_type_display()})")

PYEOF

SSHEOF

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   Department Role Data Restored!
    echo ========================================
    echo.
    echo NOW:
    echo   1. Refresh browser (F5)
    echo   2. Check Department Roles page
    echo   3. Should see at least 1 role configured
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
