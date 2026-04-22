"""
检查当前登录用户的租户关联情况
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model
from eims_app.models import Tenant, UserProfile, UserTenantRelation

User = get_user_model()

print("=" * 80)
print("检查所有用户的租户关联情况")
print("=" * 80)

users = User.objects.filter(is_active=True).order_by('username')

print(f"\n总用户数: {users.count()}")
print("\n详细列表:")
print("-" * 80)
print(f"{'用户名':<15} {'超级管理员':<8} {'UTR记录':<8} {'UP租户':<30}")
print("-" * 80)

for user in users:
    # 检查 UserTenantRelation
    utr_count = UserTenantRelation.objects.filter(user=user).count()
    
    # 检查 UserProfile
    try:
        profile = UserProfile.objects.get(user=user)
        up_tenant = profile.tenant.name if profile.tenant else "无"
    except UserProfile.DoesNotExist:
        up_tenant = "无Profile"
    
    print(f"{user.username:<15} {str(user.is_superuser):<8} {utr_count:<8} {up_tenant:<30}")

# 统计信息
print("\n" + "=" * 80)
print("统计信息:")
print("=" * 80)

utr_users = User.objects.filter(usertenantrelation__isnull=False).distinct()
print(f"有 UserTenantRelation 记录的用户数: {utr_users.count()}")

no_utr_users = User.objects.filter(usertenantrelation__isnull=True, is_active=True)
print(f"没有 UserTenantRelation 记录的用户数: {no_utr_users.count()}")

no_profile_users = User.objects.filter(profile__isnull=True, is_active=True)
print(f"没有 UserProfile 的用户数: {no_profile_users.count()}")

print("\n建议:")
print("-" * 80)
if no_utr_users.count() > 0:
    print("⚠️  发现以下用户没有 UserTenantRelation 记录:")
    for user in no_utr_users[:10]:  # 只显示前10个
        print(f"   - {user.username}")
    if no_utr_users.count() > 10:
        print(f"   ... 还有 {no_utr_users.count() - 10} 个用户")
    
    print("\n💡 解决方案:")
    print("   1. 为这些用户创建 UserTenantRelation 记录")
    print("   2. 或者确保他们的 UserProfile.tenant 字段已正确设置")
    print("   3. 当前代码已经有回退机制，会使用 UserProfile.tenant")

if no_profile_users.count() > 0:
    print(f"\n⚠️  发现 {no_profile_users.count()} 个用户没有 UserProfile:")
    for user in no_profile_users[:10]:
        print(f"   - {user.username}")
    print("\n💡 这些用户将无法看到任何可切换的公司")

print("\n" + "=" * 80)
