"""
修复部门的租户关联 - 将开发者租户的部门重新分配到鼎策公司
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_department import Department
from eims_app.models.model_tenant import Tenant

print("="*80)
print("修复部门的租户关联")
print("="*80)

# 获取租户
dingce_tenant = Tenant.objects.get(code='dingce')
developer_tenant = Tenant.objects.get(code='开发者')

print(f"\n📋 目标租户: {dingce_tenant.name} (ID: {dingce_tenant.id})")
print(f"📋 当前租户: {developer_tenant.name} (ID: {developer_tenant.id})")

# 查找需要更新的部门
depts_to_update = Department.objects.filter(tenant=developer_tenant)
print(f"\n🏢 需要更新的部门数量: {depts_to_update.count()}")

for dept in depts_to_update:
    print(f"   - {dept.department_code}: {dept.department_name}")

# 确认更新
print("\n⚠️  是否将这些部门更新为鼎策公司？")
print("   输入 'yes' 确认更新，输入其他内容取消")
response = input("\n是否继续? (yes/no): ").strip().lower()

if response == 'yes':
    count = 0
    for dept in depts_to_update:
        dept.tenant = dingce_tenant
        dept.save()
        count += 1
        print(f"   ✓ 已更新: {dept.department_name}")
    
    print(f"\n✅ 成功更新 {count} 个部门的租户关联！")
    print("   现在访问 /dingce/departments/ 应该能看到这些部门了")
else:
    print("\n❌ 取消更新")

print("\n" + "="*80)
