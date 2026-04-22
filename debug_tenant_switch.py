"""
调试切换公司下拉列表为空的问题
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model
from eims_app.models import Tenant, UserProfile, UserTenantRelation

User = get_user_model()

print("=" * 80)
print("调试切换公司下拉列表问题")
print("=" * 80)

# 1. 检查活跃租户
active_tenants = Tenant.objects.filter(is_active=True)
print(f"\n1. 活跃租户数量: {active_tenants.count()}")
for tenant in active_tenants:
    print(f"   - {tenant.name} (ID: {tenant.id})")

# 2. 检查所有用户及其关联
users = User.objects.filter(is_active=True)
print(f"\n2. 活跃用户数量: {users.count()}")

for user in users[:5]:  # 只检查前5个用户
    print(f"\n   用户: {user.username} (ID: {user.id}, 超级管理员: {user.is_superuser})")
    
    # 检查 UserProfile
    try:
        profile = UserProfile.objects.get(user=user)
        print(f"     UserProfile.tenant: {profile.tenant.name if profile.tenant else 'None'}")
    except UserProfile.DoesNotExist:
        print(f"     UserProfile: 不存在")
    
    # 检查 UserTenantRelation
    relations = UserTenantRelation.objects.filter(user=user)
    print(f"     UserTenantRelation 记录数: {relations.count()}")
    for rel in relations:
        print(f"       - {rel.tenant.name} (主公司: {rel.is_primary})")

# 3. 模拟 context_processors 的逻辑
print("\n" + "=" * 80)
print("3. 模拟 context_processors 中的租户查询逻辑")
print("=" * 80)

test_users = User.objects.filter(is_active=True)[:3]
for user in test_users:
    print(f"\n用户: {user.username} (超级管理员: {user.is_superuser})")
    
    tenants_all = []
    try:
        if user.is_superuser:
            tenants_all = list(Tenant.objects.filter(is_active=True))
            print(f"  → 超级管理员，返回所有活跃公司")
        else:
            user_tenant_relations = UserTenantRelation.objects.filter(
                user=user,
                tenant__is_active=True
            ).select_related('tenant')
            
            tenants_all = [rel.tenant for rel in user_tenant_relations]
            print(f"  → 通过 UserTenantRelation 查询到 {len(tenants_all)} 个公司")
            
            if not tenants_all:
                try:
                    user_profile = UserProfile.objects.get(user=user)
                    if user_profile.tenant and user_profile.tenant.is_active:
                        tenants_all = [user_profile.tenant]
                        print(f"  → UserTenantRelation 为空，回退到 UserProfile.tenant")
                except UserProfile.DoesNotExist:
                    pass
        
        print(f"  → 最终结果: {len(tenants_all)} 个公司")
        for t in tenants_all:
            print(f"     - {t.name}")
    except Exception as e:
        print(f"  → 错误: {e}")

print("\n" + "=" * 80)
print("调试完成")
print("=" * 80)
