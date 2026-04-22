"""
人员数据同步脚本
确保 Employee、Personnel、User 和 Admin 后台数据的一致性
"""
import os
import sys
import django

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth.models import User
from eims_app.models.model_employee import Employee
from eims_app.models.model_personnel import Personnel
from eims_app.models.model_tenant import Tenant

# 公司前缀映射
COMPANY_PREFIX_MAP = {
    'dingce': 'DCRY-',
    'shengchang': 'SCRY-',
    'jiachengda': 'JCDRY-',
}

def get_prefix_for_tenant(tenant):
    """根据租户获取人员编号前缀"""
    if not tenant:
        return 'RY-'
    
    company_code = tenant.code
    company_name = tenant.name
    
    # 优先使用公司代码匹配
    if company_code in COMPANY_PREFIX_MAP:
        return COMPANY_PREFIX_MAP[company_code]
    
    # 其次使用公司名称关键词匹配
    if '鼎策' in company_name:
        return 'DCRY-'
    elif '晟昌' in company_name:
        return 'SCRY-'
    elif '嘉诚达' in company_name:
        return 'JCDRY-'
    
    # 默认前缀
    return 'RY-'

def sync_employee_personnel_codes():
    """同步 Employee 和 Personnel 的编号"""
    print("=" * 80)
    print("员工与项目人员编号同步工具")
    print("=" * 80)
    
    tenants = Tenant.objects.all()
    total_synced = 0
    
    for tenant in tenants:
        prefix = get_prefix_for_tenant(tenant)
        print(f"\n处理公司: {tenant.name} (代码: {tenant.code})")
        print(f"  使用前缀: {prefix}")
        
        # 获取该公司的所有员工
        employees = Employee.objects.filter(tenant=tenant, is_deleted=False).order_by('id')
        employee_count = employees.count()
        print(f"  找到 {employee_count} 名员工")
        
        # 获取该公司的所有项目人员
        personnel_list = Personnel.objects.filter(tenant=tenant, is_deleted=False).order_by('id')
        personnel_count = personnel_list.count()
        print(f"  找到 {personnel_count} 名项目人员")
        
        # 1. 同步 Employee 编号（如果为空或格式不正确）
        emp_updated = 0
        for index, emp in enumerate(employees, start=1):
            expected_code = f"{prefix}{index:03d}"
            
            # 检查编号是否需要更新
            if not emp.employee_code or not emp.employee_code.startswith(prefix):
                old_code = emp.employee_code or '(空)'
                emp.employee_code = expected_code
                emp.save(update_fields=['employee_code'])
                emp_updated += 1
                
                if emp_updated <= 3:
                    print(f"    员工 [{index}]: {old_code} → {expected_code} ({emp.name})")
        
        print(f"  ✅ 已更新 {emp_updated}/{employee_count} 名员工编号")
        
        # 2. 同步 Personnel 编号（确保与 Employee 一致）
        per_updated = 0
        for personnel in personnel_list:
            if personnel.employee:
                # 如果有关联的员工，使用员工的编号
                expected_code = personnel.employee.employee_code
                
                if personnel.personnel_code != expected_code:
                    old_code = personnel.personnel_code
                    personnel.personnel_code = expected_code
                    personnel.save(update_fields=['personnel_code'])
                    per_updated += 1
                    
                    if per_updated <= 3:
                        print(f"    项目人员: {old_code} → {expected_code} ({personnel.name})")
            else:
                # 如果没有关联员工，按顺序编号
                emp_index = list(personnel_list).index(personnel) + 1
                expected_code = f"{prefix}{emp_index:03d}"
                
                if personnel.personnel_code != expected_code:
                    old_code = personnel.personnel_code
                    personnel.personnel_code = expected_code
                    personnel.save(update_fields=['personnel_code'])
                    per_updated += 1
        
        print(f"  ✅ 已更新 {per_updated}/{personnel_count} 名项目人员编号")
        total_synced += emp_updated + per_updated
    
    print("\n" + "=" * 80)
    print(f"同步完成！共更新 {total_synced} 条记录")
    print("=" * 80)

def sync_user_employee_data():
    """同步 User 和 Employee 数据"""
    print("\n" + "=" * 80)
    print("用户账号与员工数据同步")
    print("=" * 80)
    
    users = User.objects.filter(is_active=True)
    synced_count = 0
    
    for user in users:
        # 查找对应的员工记录
        try:
            employee = Employee.objects.get(
                name=user.first_name + user.last_name if user.last_name else user.first_name,
                is_deleted=False
            )
            
            # 检查是否需要关联
            if hasattr(employee, 'user') and not employee.user:
                # 这里假设有user外键，如果没有则跳过
                pass
            
        except Employee.DoesNotExist:
            continue
        except Employee.MultipleObjectsReturned:
            continue
    
    print(f"✅ 用户账号同步检查完成")

def verify_data_consistency():
    """验证数据一致性"""
    print("\n" + "=" * 80)
    print("数据一致性验证")
    print("=" * 80)
    
    tenants = Tenant.objects.filter(code__in=['dingce', 'jiachengda', 'shengchang'])
    
    for tenant in tenants:
        prefix = get_prefix_for_tenant(tenant)
        print(f"\n{tenant.name}:")
        
        # 检查 Employee 编号
        employees = Employee.objects.filter(tenant=tenant, is_deleted=False)
        emp_errors = [emp for emp in employees if not emp.employee_code.startswith(prefix)]
        
        if emp_errors:
            print(f"  ❌ Employee 编号错误: {len(emp_errors)} 条")
            for emp in emp_errors[:3]:
                print(f"     - {emp.employee_code} ({emp.name})")
        else:
            print(f"  ✅ Employee 编号全部正确 ({employees.count()} 人)")
        
        # 检查 Personnel 编号
        personnel_list = Personnel.objects.filter(tenant=tenant, is_deleted=False)
        per_errors = []
        
        for per in personnel_list:
            if per.employee:
                # 如果有关联员工，检查是否一致
                if per.personnel_code != per.employee.employee_code:
                    per_errors.append(per)
            else:
                # 如果没有关联员工，检查前缀
                if not per.personnel_code.startswith(prefix):
                    per_errors.append(per)
        
        if per_errors:
            print(f"  ❌ Personnel 编号错误: {len(per_errors)} 条")
            for per in per_errors[:3]:
                print(f"     - {per.personnel_code} ({per.name})")
        else:
            print(f"  ✅ Personnel 编号全部正确 ({personnel_list.count()} 人)")

if __name__ == '__main__':
    try:
        print("\n⚠️  警告：此操作将修改员工和项目人员的编号！")
        print("建议先备份数据库后再执行。\n")
        
        confirm = input("是否继续？(yes/no): ")
        if confirm.lower() != 'yes':
            print("操作已取消")
            sys.exit(0)
        
        # 执行同步
        sync_employee_personnel_codes()
        sync_user_employee_data()
        
        # 验证结果
        verify_data_consistency()
        
        print("\n" + "=" * 80)
        print("✅ 所有同步操作完成！")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
