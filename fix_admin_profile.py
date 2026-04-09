import os
import sys
import django

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_tenant import Tenant
from eims_app.models.model_user import UserProfile
from django.contrib.auth import get_user_model

User = get_user_model()

# 获取公司
tenant = Tenant.objects.first()
if not tenant:
    print("⚠ 没有找到公司数据")
    sys.exit(1)

print(f"当前公司: {tenant.name}")

# 找到超级管理员
admin_user = User.objects.filter(is_superuser=True).first()
if not admin_user:
    print("⚠ 未找到超级管理员")
    sys.exit(1)

print(f"超级管理员: {admin_user.username}")

# 确保 UserProfile 存在
try:
    profile = admin_user.profile
except UserProfile.DoesNotExist:
    print("创建 UserProfile...")
    profile = UserProfile.objects.create(user=admin_user)

# 更新 tenant
if profile.tenant != tenant:
    profile.tenant = tenant
    profile.save()
    print(f"✓ 已将 {admin_user.username} 关联到公司: {tenant.name}")
else:
    print(f"✓ {admin_user.username} 已经关联到公司: {tenant.name}")

print("\n✅ 完成！")
