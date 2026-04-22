"""
检查并删除编号重复或无公司的员工
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Employee
from django.db.models import Count

print("=" * 80)
print("检查编号重复和无公司的员工")
print("=" * 80)

# 1. 检查编号重复（排除已删除和临时编号）
print("\n🔍 检查重复的人员编号...")
duplicates = Employee.objects.filter(
    is_deleted=False
).exclude(
    personnel_code__startswith='TEMP-'
).exclude(
    personnel_code__startswith='DELETED-'
).exclude(
    personnel_code=''
).values('personnel_code').annotate(
    count=Count('id')
).filter(count__gt=1)

if duplicates:
    print(f"\n⚠️  找到 {len(duplicates)} 个重复的编号:")
    for dup in duplicates:
        code = dup['personnel_code']
        emps = Employee.objects.filter(personnel_code=code, is_deleted=False)
        print(f"\n   编号: {code}")
        for emp in emps:
            print(f"      - ID:{emp.id} | {emp.name} | tenant:{emp.tenant_id} | created:{emp.create_time}")
else:
    print("✅ 没有发现重复的编号")

# 2. 检查无公司的员工（tenant为空）
print("\n\n🔍 检查无公司的员工...")
no_tenant_emps = Employee.objects.filter(
    is_deleted=False,
    tenant__isnull=True
).exclude(
    personnel_code__startswith='TEMP-'
).exclude(
    personnel_code__startswith='DELETED-'
)

if no_tenant_emps:
    print(f"\n⚠️  找到 {no_tenant_emps.count()} 名无公司的员工:")
    for emp in no_tenant_emps:
        print(f"   - ID:{emp.id} | {emp.personnel_code} | {emp.name} | created:{emp.create_time}")
else:
    print("✅ 没有发现无公司的员工")

# 3. 统计信息
print("\n\n📊 总体统计:")
total_active = Employee.objects.filter(is_deleted=False).count()
total_deleted = Employee.objects.filter(is_deleted=True).count()
with_tenant = Employee.objects.filter(is_deleted=False, tenant__isnull=False).count()
without_tenant = Employee.objects.filter(is_deleted=False, tenant__isnull=True).count()

print(f"   活跃员工总数: {total_active}")
print(f"   已删除员工数: {total_deleted}")
print(f"   有公司的员工: {with_tenant}")
print(f"   无公司的员工: {without_tenant}")

print("\n" + "=" * 80)
