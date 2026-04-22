"""
智能批量重新编号员工人员编号（自动执行版，无需确认）
"""
import os
import sys
import django
import uuid

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

def renumber_employees_auto():
    """使用两阶段方法重新编号所有员工"""
    print("=" * 80)
    print("开始智能批量重新编号员工人员编号")
    print("=" * 80)
    
    employees = Employee.objects.filter(is_deleted=False).order_by('tenant_id', 'id')
    total_count = employees.count()
    print(f"\n📊 找到 {total_count} 名员工需要处理\n")
    
    # 第一阶段：临时编号
    print("🔄 第一阶段：清除现有编号（避免冲突）...")
    temp_count = 0
    for emp in employees:
        temp_code = f"TEMP-{uuid.uuid4().hex[:8]}"
        emp.personnel_code = temp_code
        emp.save(update_fields=['personnel_code'])
        temp_count += 1
    
    print(f"✅ 第一阶段完成：已临时编号 {temp_count} 名员工\n")
    
    # 第二阶段：正式编号
    print("🔄 第二阶段：按公司重新分配编号...")
    
    tenant_groups = {}
    for emp in employees:
        prefix = get_prefix_for_employee(emp)
        if prefix not in tenant_groups:
            tenant_groups[prefix] = []
        tenant_groups[prefix].append(emp)
    
    updated_count = 0
    for prefix, emps in sorted(tenant_groups.items()):
        tenant_name = emps[0].tenant.name if emps[0].tenant else "无公司"
        print(f"\n   📋 {prefix} ({tenant_name}): {len(emps)} 人")
        
        for idx, emp in enumerate(emps, 1):
            new_code = f"{prefix}{idx:03d}"
            emp.personnel_code = new_code
            emp.save(update_fields=['personnel_code'])
            updated_count += 1
            print(f"      ✅ {emp.name}: {new_code}")
    
    print("\n" + "=" * 80)
    print("✅ 重新编号完成！")
    print("=" * 80)
    print(f"\n📈 统计信息:")
    print(f"   总员工数: {total_count}")
    print(f"   已更新: {updated_count}")
    
    print(f"\n📋 各公司人员分布:")
    for prefix, emps in sorted(tenant_groups.items()):
        tenant_name = emps[0].tenant.name if emps[0].tenant else "无公司"
        print(f"   - {prefix} ({tenant_name}): {len(emps)} 人")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    renumber_employees_auto()
