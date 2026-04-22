"""
验证员工人员编号的当前状态
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Employee, Tenant

print("=" * 80)
print("员工人员编号当前状态")
print("=" * 80)

# 获取所有未删除的员工
employees = Employee.objects.filter(is_deleted=False).order_by('tenant_id', 'id')

total_count = employees.count()
print(f"\n📊 总员工数: {total_count}\n")

# 按公司统计
stats = {}
for emp in employees:
    tenant_name = emp.tenant.name if emp.tenant else "无公司"
    tenant_code = emp.tenant.code if emp.tenant else "none"
    
    key = f"{tenant_code} - {tenant_name}"
    if key not in stats:
        stats[key] = []
    
    stats[key].append(emp)

# 显示每个公司的员工
for key, emps in sorted(stats.items()):
    print(f"\n{'='*60}")
    print(f"🏢 {key}")
    print(f"   人数: {len(emps)}")
    print(f"{'='*60}")
    
    for emp in emps[:10]:  # 只显示前10个作为示例
        print(f"   - {emp.personnel_code} | {emp.name}")
    
    if len(emps) > 10:
        print(f"   ... 还有 {len(emps) - 10} 人")

print("\n" + "=" * 80)
