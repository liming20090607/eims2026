"""
检查admin用户的公司关联情况
"""
import os
import sys
import django

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth.models import User
from eims_app.models import Tenant, UserProfile

# 获取admin用户
try:
    admin = User.objects.get(username='admin')
    print(f"✅ 找到admin用户")
    print(f"   - is_superuser: {admin.is_superuser}")
    print(f"   - first_name: {admin.first_name}")
    print(f"   - email: {admin.email}")
except User.DoesNotExist:
    print("❌ admin用户不存在")
    sys.exit(1)

# 检查UserProfile
try:
    profile = UserProfile.objects.get(user=admin)
    print(f"\n✅ 找到UserProfile")
    print(f"   - tenant: {profile.tenant}")
except UserProfile.DoesNotExist:
    print(f"\n⚠️  没有找到UserProfile，需要创建")
    profile = UserProfile.objects.create(user=admin)
    print(f"✅ 已创建UserProfile")

# 检查admin可以访问的公司
if admin.is_superuser:
    tenants = Tenant.objects.filter(is_active=True)
    print(f"\n📋 admin是超级管理员，可以访问所有公司：")
else:
    tenants = Tenant.objects.filter(is_active=True, userprofile=profile)
    print(f"\n📋 admin可以访问的公司：")

for tenant in tenants:
    print(f"   - {tenant.name} ({tenant.code})")

print(f"\n总计: {tenants.count()} 家公司")

if tenants.count() == 0:
    print("\n⚠️  admin没有关联任何公司！")
    print("建议：将admin关联到所有公司，或创建一个测试用户关联到多家公司")
elif tenants.count() == 1:
    print("\n⚠️  admin只关联了1家公司")
    print("系统会自动选择该公司，不会显示选择界面")
    print("\n如需测试公司选择功能，请关联多家公司")
else:
    print(f"\n✅ admin关联了{tenants.count()}家公司")
    print("登录时应该会显示公司选择界面")
