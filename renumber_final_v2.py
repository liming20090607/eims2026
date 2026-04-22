"""
最终版：重新编号当前数据库中的31名员工
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

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
print("重新编号当前数据库中的员工")
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

# 逐个更新（使用Django ORM的update方法避免信号触发）
updated_count = 0
for prefix, emps in sorted(tenant_groups.items()):
    tenant_name = emps[0].tenant.name if emps[0].tenant else "无公司"
    print(f"📋 {prefix} ({tenant_name}): {len(emps)} 人")
    
    for idx, emp in enumerate(emps, 1):
        new_code = f"{prefix}{idx:03d}"
        
        # 直接更新数据库，绕过ORM的信号和验证
        Employee.objects.filter(id=emp.id).update(personnel_code=new_code)
        
        updated_count += 1
        print(f"   ✅ {emp.name}: {new_code}")

print(f"\n✅ 成功更新 {updated_count} 名员工")
print("\n" + "=" * 80)
print("完成！请运行 verify_employee_codes.py 验证结果")
print("=" * 80)
