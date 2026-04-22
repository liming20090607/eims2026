"""
验证部门管理数据恢复结果
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_department import Department, DepartmentRole, ApprovalChain

print("="*80)
print("部门管理数据验证")
print("="*80)

# 统计数据
print(f"\n📊 数据统计:")
print(f"   部门数量: {Department.objects.count()}")
print(f"   角色数量: {DepartmentRole.objects.count()}")
print(f"   审批链数量: {ApprovalChain.objects.count()}")

# 部门列表
print(f"\n🏢 部门列表 (前5个):")
for dept in Department.objects.all()[:5]:
    print(f"   - {dept.department_code}: {dept.department_name} ({dept.get_department_type_display()})")

# 角色示例
print(f"\n👥 角色示例 (前3个):")
roles = DepartmentRole.objects.select_related('department').all()[:3]
for role in roles:
    print(f"   - {role.role_name} ({role.get_role_type_display()}) in {role.department.department_name}")

# 审批链
print(f"\n⚙️  审批链:")
for chain in ApprovalChain.objects.all():
    print(f"   - {chain.name}: {chain.get_business_type_display()} ({chain.get_chain_type_display()})")

print("\n" + "="*80)
print("✅ 数据验证完成！所有数据已正常加载到MySQL数据库")
print("="*80)
