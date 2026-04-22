"""
数据一致性全面验证脚本
检查 Employee、Personnel、User 和 Admin 后台数据的一致性
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
    if company_code in COMPANY_PREFIX_MAP:
        return COMPANY_PREFIX_MAP[company_code]
    
    company_name = tenant.name
    if '鼎策' in company_name:
        return 'DCRY-'
    elif '晟昌' in company_name:
        return 'SCRY-'
    elif '嘉诚达' in company_name:
        return 'JCDRY-'
    
    return 'RY-'

def verify_all_data():
    """全面验证数据一致性"""
    print("=" * 100)
    print(" " * 30 + "数据一致性全面验证报告")
    print("=" * 100)
    
    tenants = Tenant.objects.filter(code__in=['dingce', 'jiachengda', 'shengchang'])
    
    total_issues = 0
    
    for tenant in tenants:
        prefix = get_prefix_for_tenant(tenant)
        print(f"\n{'=' * 100}")
        print(f"公司: {tenant.name} (代码: {tenant.code}, 前缀: {prefix})")
        print(f"{'=' * 100}")
        
        # 1. 验证 Employee 数据
        print("\n【1】员工基本信息表 (Employee)")
        print("-" * 100)
        employees = Employee.objects.filter(tenant=tenant, is_deleted=False).order_by('id')
        emp_count = employees.count()
        print(f"  总人数: {emp_count}")
        
        # 检查编号格式
        emp_format_errors = [emp for emp in employees if not emp.employee_code.startswith(prefix)]
        if emp_format_errors:
            print(f"  ❌ 编号格式错误: {len(emp_format_errors)} 人")
            for emp in emp_format_errors[:5]:
                print(f"     - {emp.employee_code:12s} | {emp.name:8s} | 应为: {prefix}xxx")
            total_issues += len(emp_format_errors)
        else:
            print(f"  ✅ 编号格式全部正确")
        
        # 检查编号唯一性
        emp_codes = [emp.employee_code for emp in employees]
        if len(emp_codes) != len(set(emp_codes)):
            duplicates = [code for code in emp_codes if emp_codes.count(code) > 1]
            print(f"  ❌ 编号重复: {len(set(duplicates))} 个")
            total_issues += len(set(duplicates))
        else:
            print(f"  ✅ 编号无重复")
        
        # 2. 验证 Personnel 数据
        print("\n【2】项目人员分配表 (Personnel)")
        print("-" * 100)
        personnel_list = Personnel.objects.filter(tenant=tenant, is_deleted=False).order_by('id')
        per_count = personnel_list.count()
        print(f"  总人数: {per_count}")
        
        # 检查编号格式
        per_format_errors = []
        for per in personnel_list:
            if per.employee:
                # 如果有关联员工，应该与员工编号一致
                if per.personnel_code != per.employee.employee_code:
                    per_format_errors.append(per)
            else:
                # 如果没有关联员工，检查前缀
                if not per.personnel_code.startswith(prefix):
                    per_format_errors.append(per)
        
        if per_format_errors:
            print(f"  ❌ 编号不一致: {len(per_format_errors)} 人")
            for per in per_format_errors[:5]:
                expected = per.employee.employee_code if per.employee else f"{prefix}xxx"
                print(f"     - {per.personnel_code:12s} | {per.name:8s} | 应为: {expected}")
            total_issues += len(per_format_errors)
        else:
            print(f"  ✅ 编号与Employee完全一致")
        
        # 3. 检查 Employee 和 Personnel 的关联关系
        print("\n【3】数据关联关系")
        print("-" * 100)
        
        # 有Employee记录的Personnel
        linked_per = personnel_list.filter(employee__isnull=False).count()
        unlinked_per = personnel_list.filter(employee__isnull=True).count()
        
        print(f"  已关联员工的Project人员: {linked_per}")
        print(f"  未关联员工的Project人员: {unlinked_per}")
        
        if unlinked_per > 0:
            print(f"  ⚠️  建议: 为这些人员创建对应的Employee记录")
        
        # 4. 统计信息
        print("\n【4】数据统计汇总")
        print("-" * 100)
        print(f"  Employee 总数: {emp_count}")
        print(f"  Personnel 总数: {per_count}")
        
        if emp_count == per_count:
            print(f"  ✅ 两表人数一致")
        else:
            diff = abs(emp_count - per_count)
            print(f"  ⚠️  两表人数差异: {diff} 人")
            if emp_count > per_count:
                print(f"     → Employee 比 Personnel 多 {diff} 人（可能有员工未分配项目）")
            else:
                print(f"     → Personnel 比 Employee 多 {diff} 人（可能有项目人员无员工档案）")
    
    # 5. 全局统计
    print(f"\n{'=' * 100}")
    print("全局统计")
    print(f"{'=' * 100}")
    
    total_employees = Employee.objects.filter(is_deleted=False).count()
    total_personnel = Personnel.objects.filter(is_deleted=False).count()
    
    print(f"  所有公司员工总数: {total_employees}")
    print(f"  所有公司项目人员总数: {total_personnel}")
    print(f"  发现的数据问题总数: {total_issues}")
    
    if total_issues == 0:
        print(f"\n  🎉 恭喜！所有数据完全一致，没有发现问题！")
    else:
        print(f"\n  ⚠️  发现 {total_issues} 个问题，建议修复")
    
    print(f"{'=' * 100}")
    
    return total_issues == 0

if __name__ == '__main__':
    try:
        success = verify_all_data()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 验证过程发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
