"""
为所有用户创建 UserTenantRelation 记录
基于现有的 UserProfile.tenant 数据
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model
from eims_app.models import Tenant, UserProfile, UserTenantRelation

User = get_user_model()

print("=" * 80)
print("为用户创建 UserTenantRelation 记录")
print("=" * 80)

# 统计信息
created_count = 0
skipped_count = 0
error_count = 0
no_tenant_count = 0

users = User.objects.filter(is_active=True)
print(f"\n活跃用户总数: {users.count()}")

for user in users:
    try:
        # 检查是否已经有 UserTenantRelation 记录
        existing_relations = UserTenantRelation.objects.filter(user=user)
        
        if existing_relations.exists():
            skipped_count += 1
            print(f"⊘ {user.username}: 已有 {existing_relations.count()} 条记录，跳过")
            continue
        
        # 尝试从 UserProfile 获取租户
        tenant = None
        try:
            profile = UserProfile.objects.get(user=user)
            tenant = profile.tenant
        except UserProfile.DoesNotExist:
            pass
        
        if not tenant:
            no_tenant_count += 1
            print(f"✗ {user.username}: 没有关联的租户，跳过")
            continue
        
        # 创建 UserTenantRelation 记录
        relation = UserTenantRelation.objects.create(
            user=user,
            tenant=tenant,
            is_primary=True,  # 设为主要公司
            remark='从 UserProfile 迁移'
        )
        created_count += 1
        print(f"✓ {user.username}: 创建记录 -> {tenant.name}")
        
    except Exception as e:
        error_count += 1
        print(f"✗ {user.username}: 错误 - {e}")

print("\n" + "=" * 80)
print("完成统计:")
print("=" * 80)
print(f"✓ 成功创建: {created_count} 条记录")
print(f"⊘ 已存在跳过: {skipped_count} 个用户")
print(f"✗ 没有租户跳过: {no_tenant_count} 个用户")
print(f"✗ 发生错误: {error_count} 个用户")
print(f"总计处理: {users.count()} 个用户")

if no_tenant_count > 0:
    print("\n⚠️  警告: 以下用户没有关联任何租户，需要手动分配:")
    users_without_tenant = []
    for user in users:
        has_relation = UserTenantRelation.objects.filter(user=user).exists()
        has_profile_tenant = False
        try:
            profile = UserProfile.objects.get(user=user)
            has_profile_tenant = profile.tenant is not None
        except UserProfile.DoesNotExist:
            pass
        
        if not has_relation and not has_profile_tenant:
            users_without_tenant.append(user.username)
    
    for username in users_without_tenant[:20]:
        print(f"   - {username}")
    if len(users_without_tenant) > 20:
        print(f"   ... 还有 {len(users_without_tenant) - 20} 个用户")

print("\n" + "=" * 80)
