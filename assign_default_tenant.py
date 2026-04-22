"""
为没有租户关联的用户分配默认租户
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model
from eims_app.models import Tenant, UserProfile, UserTenantRelation

User = get_user_model()

print("=" * 80)
print("为没有租户的用户分配默认租户")
print("=" * 80)

# 获取默认租户（广西鼎策工程顾问有限责任公司）
default_tenant = Tenant.objects.get(id=2)
print(f"\n默认租户: {default_tenant.name} (ID: {default_tenant.id})")

# 找出所有没有租户关联的用户
users_without_tenant = []
users = User.objects.filter(is_active=True)

for user in users:
    has_relation = UserTenantRelation.objects.filter(user=user).exists()
    has_profile_tenant = False
    try:
        profile = UserProfile.objects.get(user=user)
        has_profile_tenant = profile.tenant is not None
    except UserProfile.DoesNotExist:
        pass
    
    if not has_relation and not has_profile_tenant:
        users_without_tenant.append(user)

print(f"\n需要分配租户的用户数: {len(users_without_tenant)}")

# 为这些用户创建 UserProfile 和 UserTenantRelation
created_profile = 0
created_relation = 0
skipped = 0

for user in users_without_tenant:
    try:
        # 1. 确保有 UserProfile
        profile, profile_created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'tenant': default_tenant}
        )
        
        if profile_created:
            print(f"✓ {user.username}: 创建 UserProfile")
            created_profile += 1
        elif not profile.tenant:
            profile.tenant = default_tenant
            profile.save()
            print(f"✓ {user.username}: 更新 UserProfile.tenant")
        
        # 2. 创建 UserTenantRelation
        relation, relation_created = UserTenantRelation.objects.get_or_create(
            user=user,
            tenant=default_tenant,
            defaults={
                'is_primary': True,
                'remark': '自动分配的默认公司'
            }
        )
        
        if relation_created:
            print(f"✓ {user.username}: 创建 UserTenantRelation -> {default_tenant.name}")
            created_relation += 1
        else:
            print(f"⊘ {user.username}: UserTenantRelation 已存在")
            skipped += 1
            
    except Exception as e:
        print(f"✗ {user.username}: 错误 - {e}")

print("\n" + "=" * 80)
print("完成统计:")
print("=" * 80)
print(f"✓ 创建/更新 UserProfile: {created_profile} 个")
print(f"✓ 创建 UserTenantRelation: {created_relation} 条")
print(f"⊘ 已存在跳过: {skipped} 个")
print(f"总计处理: {len(users_without_tenant)} 个用户")

# 验证
print("\n验证结果:")
print("-" * 80)
final_check = User.objects.filter(is_active=True)
with_relation = User.objects.filter(usertenantrelation__isnull=False).distinct()
without_relation = User.objects.filter(usertenantrelation__isnull=True).distinct()

print(f"活跃用户总数: {final_check.count()}")
print(f"有 UserTenantRelation 的用户: {with_relation.count()}")
print(f"没有 UserTenantRelation 的用户: {without_relation.count()}")

if without_relation.count() > 0:
    print("\n仍然没有关联的用户:")
    for user in without_relation:
        print(f"   - {user.username}")

print("\n" + "=" * 80)
