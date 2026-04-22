"""
检查部门管理的租户过滤问题
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_department import Department
from eims_app.models.model_tenant import Tenant

print("="*80)
print("检查部门管理的租户过滤问题")
print("="*80)

# 1. 查看所有租户
print("\n📋 系统中的租户:")
tenants = Tenant.objects.filter(is_active=True)
for tenant in tenants:
    print(f"   - ID: {tenant.id}, 名称: {tenant.name}, 编码: {tenant.code}")

# 2. 查看所有部门的租户关联
print("\n🏢 部门的租户关联:")
depts = Department.objects.all()
print(f"   总部门数: {depts.count()}")

# 按租户分组统计
tenant_counts = {}
for dept in depts:
    tenant_name = dept.tenant.name if dept.tenant else "无租户"
    tenant_counts[tenant_name] = tenant_counts.get(tenant_name, 0) + 1

for tenant_name, count in tenant_counts.items():
    print(f"   - {tenant_name}: {count} 个部门")

# 3. 显示部门详情
print("\n📊 部门详情:")
for dept in Department.objects.all()[:5]:
    tenant_info = dept.tenant.name if dept.tenant else "None"
    print(f"   - {dept.department_code}: {dept.department_name}")
    print(f"     租户: {tenant_info}, is_deleted: {dept.is_deleted}")

print("\n" + "="*80)
print("💡 分析:")
print("   如果部门没有关联租户(tenant=None)或租户不匹配，则会被过滤掉")
print("   需要确保部门的 tenant 字段与当前用户的租户匹配")
print("="*80)
