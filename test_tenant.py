import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model
from eims_app.models import UserProfile, Tenant

print("="*60)
print("多租户功能测试")
print("="*60)
print()

# 1. 测试租户列表
print("1. 租户列表:")
for tenant in Tenant.objects.all():
    user_count = tenant.get_active_user_count()
    print(f"   - {tenant.code}: {tenant.name} ({user_count} 个用户)")
print()

# 2. 测试超级管理员的租户分配
User = get_user_model()
superuser = User.objects.filter(is_superuser=True).first()
if superuser:
    profile = UserProfile.objects.get(user=superuser)
    print(f"2. 超级管理员信息:")
    print(f"   用户名: {superuser.username}")
    print(f"   所属租户: {profile.tenant.name if profile.tenant else '无'}")
    print(f"   租户ID: {profile.tenant.id if profile.tenant else '无'}")
else:
    print("2. 未找到超级管理员")
print()

# 3. 测试中间件导入
try:
    from eims_app.middleware import TenantMiddleware
    print("3. ✅ TenantMiddleware 导入成功")
except ImportError as e:
    print(f"3. ❌ TenantMiddleware 导入失败: {e}")
print()

# 4. 测试工具函数
try:
    from eims_app.utils.tenant_utils import get_queryset_for_tenant
    print("4. ✅ 租户工具函数导入成功")
except ImportError as e:
    print(f"4. ❌ 租户工具函数导入失败: {e}")
print()

print("="*60)
print("测试完成！")
print("="*60)
