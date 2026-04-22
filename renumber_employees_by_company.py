"""
批量重新编号员工人员编号
根据公司代码设置不同的前缀：
- 鼎策 (dingce): DCRY-XXX
- 晟昌 (shengchang): SCRY-XXX
- 嘉诚达 (jiachengda): JCDRY-XXX
- 其他/无公司: QTRY-XXX
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import transaction
from eims_app.models import Employee, Tenant

# 定义公司前缀映射
COMPANY_PREFIX_MAP = {
    'dingce': 'DCRY-',
    'shengchang': 'SCRY-',
    'jiachengda': 'JCDRY-',
}

# 默认前缀（无公司或其他公司）
DEFAULT_PREFIX = 'QTRY-'

def get_prefix_for_employee(employee):
    """根据员工所属公司获取前缀"""
    if not employee.tenant:
        return DEFAULT_PREFIX
    
    tenant_code = employee.tenant.code.lower()
    
    # 尝试精确匹配
    if tenant_code in COMPANY_PREFIX_MAP:
        return COMPANY_PREFIX_MAP[tenant_code]
    
    # 尝试通过公司名称匹配
    tenant_name = employee.tenant.name
    if '鼎策' in tenant_name or 'dingce' in tenant_name.lower():
        return 'DCRY-'
    elif '晟昌' in tenant_name or 'shengchang' in tenant_name.lower():
        return 'SCRY-'
    elif '嘉诚达' in tenant_name or 'jiachengda' in tenant_name.lower():
        return 'JCDRY-'
    
    # 默认前缀
    return DEFAULT_PREFIX

def renumber_employees():
    """重新编号所有员工"""
    print("=" * 80)
    print("开始批量重新编号员工人员编号")
    print("=" * 80)
    
    # 获取所有未删除的员工，按租户和ID排序
    employees = Employee.objects.filter(is_deleted=False).order_by('tenant_id', 'id')
    
    total_count = employees.count()
    print(f"\n📊 找到 {total_count} 名员工需要处理\n")
    
    # 按租户分组统计
    tenant_stats = {}
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    with transaction.atomic():
        for idx, employee in enumerate(employees, 1):
            try:
                # 确定前缀
                prefix = get_prefix_for_employee(employee)
                
                # 获取租户信息用于统计
                tenant_name = employee.tenant.name if employee.tenant else "无公司"
                tenant_key = f"{prefix} ({tenant_name})"
                
                if tenant_key not in tenant_stats:
                    tenant_stats[tenant_key] = 0
                
                tenant_stats[tenant_key] += 1
                new_number = tenant_stats[tenant_key]
                
                # 生成新的人员编号
                new_personnel_code = f"{prefix}{new_number:03d}"
                
                # 检查是否需要更新
                if employee.personnel_code != new_personnel_code:
                    old_code = employee.personnel_code
                    employee.personnel_code = new_personnel_code
                    employee.save(update_fields=['personnel_code'])
                    
                    print(f"✅ [{idx}/{total_count}] {old_code} → {new_personnel_code} | {employee.name}")
                    updated_count += 1
                else:
                    print(f"⏭️  [{idx}/{total_count}] {new_personnel_code} (无需更新) | {employee.name}")
                    skipped_count += 1
                    
            except Exception as e:
                print(f"❌ [{idx}/{total_count}] 处理失败: {str(e)} | {employee.name}")
                error_count += 1
    
    print("\n" + "=" * 80)
    print("✅ 重新编号完成！")
    print("=" * 80)
    print(f"\n📈 统计信息:")
    print(f"   总员工数: {total_count}")
    print(f"   已更新: {updated_count}")
    print(f"   跳过: {skipped_count}")
    print(f"   错误: {error_count}")
    
    print(f"\n📋 各公司人员分布:")
    for tenant_key, count in sorted(tenant_stats.items()):
        print(f"   - {tenant_key}: {count} 人")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    # 确认操作
    print("⚠️  警告：此操作将修改所有员工的人员编号！")
    print("请确认是否继续？(输入 yes 继续，其他任意键取消)")
    confirm = input("> ").strip().lower()
    
    if confirm == 'yes':
        renumber_employees()
    else:
        print("❌ 操作已取消")
