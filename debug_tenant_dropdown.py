import os
import sys
import django

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_local_mysql')
django.setup()

from eims_app.models.model_tenant import Tenant
from eims_app.models.model_user import UserProfile
from django.contrib.auth import get_user_model

User = get_user_model()

print("=== 诊断切换公司下拉列表为空问题 ===\n")

# 1. 检查 Tenant 表数据
print("1. Tenant 表数据:")
tenants = Tenant.objects.filter(is_active=True)
print(f"   活跃公司数量: {tenants.count()}")
for t in tenants:
    print(f"   - ID: {t.id}, Name: {t.name}, Code: {t.code}, Active: {t.is_active}")

# 2. 检查超级管理员
print("\n2. 超级管理员:")
superusers = User.objects.filter(is_superuser=True)
print(f"   超级管理员数量: {superusers.count()}")
for su in superusers:
    print(f"   - Username: {su.username}, ID: {su.id}")

# 3. 模拟 context processor 逻辑
print("\n3. 模拟 context processor 逻辑:")
admin = superusers.first()
if admin:
    print(f"   测试用户: {admin.username} (is_superuser={admin.is_superuser})")
    
    # 测试超级管理员路径
    tenants_for_super = Tenant.objects.filter(is_active=True)
    print(f"   超级管理员路径 - 活跃公司数: {tenants_for_super.count()}")
    for t in tenants_for_super:
        print(f"     - {t.name}")
    
    # 测试 UserProfile
    try:
        profile = UserProfile.objects.get(user=admin)
        print(f"\n   UserProfile 存在:")
        print(f"   - ID: {profile.id}")
        print(f"   - tenant: {profile.tenant}")
        print(f"   - tenant_id: {profile.tenant_id}")
        
        if profile.tenant:
            # 测试普通用户路径
            tenants_for_user = Tenant.objects.filter(is_active=True, userprofile=profile)
            print(f"\n   普通用户路径（通过UserProfile关联）- 公司数: {tenants_for_user.count()}")
            for t in tenants_for_user:
                print(f"     - {t.name}")
        else:
            print(f"\n   ⚠ 警告: UserProfile.tenant 为 None！")
    except UserProfile.DoesNotExist:
        print(f"\n   ⚠ UserProfile 不存在！需要创建")

# 4. 检查所有 Tenant（包括非活跃的）
print("\n4. 所有 Tenant 记录（包括非活跃）:")
all_tenants = Tenant.objects.all()
print(f"   总记录数: {all_tenants.count()}")
for t in all_tenants:
    print(f"   - ID: {t.id}, Name: {t.name}, Active: {t.is_active}")

print("\n✅ 诊断完成！")
