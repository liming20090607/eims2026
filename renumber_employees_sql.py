"""
最终版：使用SQL直接批量更新人员编号
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection
from eims_app.models import Employee

# 定义公司前缀映射
COMPANY_PREFIX_MAP = {
    'dingce': 'DCRY-',
    'shengchang': 'SCRY-',
    'jiachengda': 'JCDRY-',
}

DEFAULT_PREFIX = 'QTRY-'

def get_prefix_for_employee(employee):
    """根据员工所属公司获取前缀"""
    if not employee.tenant:
        return DEFAULT_PREFIX
    
    tenant_code = employee.tenant.code.lower()
    
    if tenant_code in COMPANY_PREFIX_MAP:
        return COMPANY_PREFIX_MAP[tenant_code]
    
    tenant_name = employee.tenant.name
    if '鼎策' in tenant_name or 'dingce' in tenant_name.lower():
        return 'DCRY-'
    elif '晟昌' in tenant_name or 'shengchang' in tenant_name.lower():
        return 'SCRY-'
    elif '嘉诚达' in tenant_name or 'jiachengda' in tenant_name.lower():
        return 'JCDRY-'
    
    return DEFAULT_PREFIX

print("=" * 80)
print("使用SQL直接批量更新人员编号")
print("=" * 80)

# 获取所有员工并按租户排序
employees = list(Employee.objects.filter(is_deleted=False).order_by('tenant_id', 'id'))
total_count = len(employees)

print(f"\n📊 找到 {total_count} 名员工\n")

# 按前缀分组
tenant_groups = {}
for emp in employees:
    prefix = get_prefix_for_employee(emp)
    if prefix not in tenant_groups:
        tenant_groups[prefix] = []
    tenant_groups[prefix].append(emp)

# 准备批量更新
updates = []
for prefix, emps in sorted(tenant_groups.items()):
    tenant_name = emps[0].tenant.name if emps[0].tenant else "无公司"
    print(f"📋 {prefix} ({tenant_name}): {len(emps)} 人")
    
    for idx, emp in enumerate(emps, 1):
        new_code = f"{prefix}{idx:03d}"
        updates.append((new_code, emp.id))
        print(f"   ✅ {emp.name}: {new_code}")

print(f"\n🔄 开始批量更新 {len(updates)} 条记录...")

# 使用原生SQL批量更新
cursor = connection.cursor()
updated_count = 0

for new_code, emp_id in updates:
    cursor.execute(
        "UPDATE eims_app_employee SET personnel_code = %s WHERE id = %s",
        [new_code, emp_id]
    )
    updated_count += 1

print(f"\n✅ 成功更新 {updated_count} 条记录")
print("\n" + "=" * 80)
print("完成！")
print("=" * 80)
