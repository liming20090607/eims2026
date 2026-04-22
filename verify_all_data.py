"""
验证所有迁移的数据
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model
from eims_app.models.model_tenant import Tenant
from eims_app.models.model_employee import Employee
from eims_app.models.model_personnel import Personnel
from eims_app.models.model_department import Department
from eims_app.models.model_user import UserProfile, UserTenantRelation

User = get_user_model()

print("="*70)
print("数据迁移验证报告")
print("="*70)

# 1. 公司信息
print("\n【1】公司信息 (租户)")
print("-" * 70)
tenants = Tenant.objects.all()
print(f"总计: {tenants.count()} 家公司\n")

for tenant in tenants:
    user_count = UserTenantRelation.objects.filter(tenant=tenant).count()
    dept_count = Department.objects.filter(tenant=tenant).count()
    emp_count = Employee.objects.filter(tenant=tenant).count()
    pers_count = Personnel.objects.filter(tenant=tenant).count()
    
    print(f"公司名称: {tenant.name}")
    print(f"  代码: {tenant.code}")
    print(f"  用户数: {user_count}")
    print(f"  部门数: {dept_count}")
    print(f"  员工数: {emp_count}")
    print(f"  人员花名册: {pers_count}")
    print()

# 2. 部门信息
print("\n【2】部门信息")
print("-" * 70)
departments = Department.objects.all()
print(f"总计: {departments.count()} 个部门\n")

for dept in departments[:5]:
    print(f"  • {dept.department_name} ({dept.department_code})")
if departments.count() > 5:
    print(f"  ... 还有 {departments.count() - 5} 个部门")

# 3. 员工主数据
print("\n【3】员工主数据")
print("-" * 70)
employees = Employee.objects.all()
print(f"总计: {employees.count()} 名员工\n")

for emp in employees[:5]:
    print(f"  • {emp.employee_code} - {emp.name} (性别: {'男' if emp.gender == 0 else '女'})")
if employees.count() > 5:
    print(f"  ... 还有 {employees.count() - 5} 名员工")

# 4. 人员花名册
print("\n【4】人员花名册")
print("-" * 70)
personnel_list = Personnel.objects.all()
print(f"总计: {personnel_list.count()} 条记录\n")

for pers in personnel_list[:5]:
    emp_info = f" [员工: {pers.employee.name}]" if pers.employee else ""
    print(f"  • {pers.personnel_code} - {pers.name}{emp_info}")
if personnel_list.count() > 5:
    print(f"  ... 还有 {personnel_list.count() - 5} 条记录")

# 5. 用户账号
print("\n【5】用户账号")
print("-" * 70)
users = User.objects.all()
print(f"总计: {users.count()} 个用户账号\n")

superusers = users.filter(is_superuser=True)
print(f"超级管理员 ({superusers.count()}):")
for u in superusers:
    print(f"  • {u.username}")

regular_users = users.filter(is_superuser=False)
print(f"\n普通用户 ({regular_users.count()}):")
for u in regular_users[:5]:
    profile_str = ""
    try:
        profile = u.profile
        if profile.real_name:
            profile_str = f" ({profile.real_name})"
    except:
        pass
    print(f"  • {u.username}{profile_str}")
if regular_users.count() > 5:
    print(f"  ... 还有 {regular_users.count() - 5} 个用户")

# 6. 用户-公司关联
print("\n【6】用户-公司关联")
print("-" * 70)
relations = UserTenantRelation.objects.all()
print(f"总计: {relations.count()} 条关联记录\n")

# 显示每个公司的用户
for tenant in tenants:
    if tenant.code == 'root_admin':
        continue
    relations_for_tenant = UserTenantRelation.objects.filter(tenant=tenant)
    print(f"{tenant.name}:")
    for rel in relations_for_tenant[:3]:
        primary_marker = " [主]" if rel.is_primary else ""
        print(f"  • {rel.user.username}{primary_marker}")
    if relations_for_tenant.count() > 3:
        print(f"  ... 还有 {relations_for_tenant.count() - 3} 个用户")
    print()

# 总结
print("="*70)
print("迁移总结")
print("="*70)
print(f"✓ 公司: {tenants.count()} 家 (包括 Root Admin)")
print(f"✓ 部门: {departments.count()} 个")
print(f"✓ 员工: {employees.count()} 名")
print(f"✓ 人员花名册: {personnel_list.count()} 条")
print(f"✓ 用户账号: {users.count()} 个")
print(f"✓ 用户-公司关联: {relations.count()} 条")
print("="*70)

print("\n超级管理员操作指南:")
print("1. 登录: http://localhost:8000/")
print("   用户名: root")
print("   密码: root123456")
print("\n2. 访问根管理后台: http://localhost:8000/root/")
print("   - 可以查看所有公司的数据")
print("   - 可以切换公司进行管理")
print("   - 可以管理用户、部门、员工等")
print("\n3. 切换到具体公司:")
print("   - 鼎策公司: http://localhost:8000/dingce/")
print("   - 晟昌公司: http://localhost:8000/shengchang/")
print("   - 嘉诚达公司: http://localhost:8000/jiachengda/")
print("="*70)
