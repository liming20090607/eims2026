"""
测试登录路由逻辑
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth.models import User
from eims_app.models.model_tenant import Tenant
from eims_app.models.model_user import UserProfile, UserTenantRelation

print("="*80)
print("登录路由逻辑测试")
print("="*80)

# 检查现有的用户和租户关系
print("\n1. 现有用户列表:")
users = User.objects.all()
for user in users:
    print(f"   - {user.username} (ID: {user.id}, 超级管理员: {user.is_superuser})")

print("\n2. 现有租户列表:")
tenants = Tenant.objects.all()
for tenant in tenants:
    print(f"   - {tenant.name} (代码: {tenant.code}, ID: {tenant.id})")

print("\n3. 用户-租户关系:")
relations = UserTenantRelation.objects.all()
if relations.exists():
    for rel in relations:
        print(f"   - 用户: {rel.user.username} -> 租户: {rel.tenant.name}")
else:
    print("   (暂无用户-租户关系记录)")

print("\n4. UserProfile中的租户设置:")
profiles = UserProfile.objects.all()
for profile in profiles:
    if profile.tenant:
        print(f"   - {profile.user.username} -> {profile.tenant.name}")
    else:
        print(f"   - {profile.user.username} -> (未设置)")

print("\n" + "="*80)
print("登录路由规则说明:")
print("="*80)
print("""
✅ 已实现的功能:

1. 超级管理员 (is_superuser=True):
   - 登录后自动跳转到 /root/ 后台管理系统
   - 可以访问所有租户系统

2. 普通用户 - 单公司:
   - 如果只属于一个公司，自动跳转到对应公司系统
   - 例如: /dingce/, /shengchang/, /jiachengda/

3. 普通用户 - 多公司:
   - 如果属于多个公司，显示公司选择界面
   - 用户从中选择要进入的公司系统

4. 普通用户 - 无公司:
   - 如果没有分配任何公司，显示错误提示
   - 需要联系管理员分配权限

⚠️  注意事项:

- 用户必须通过 UserProfile 或 UserTenantRelation 关联到租户
- 登录时使用 custom_login 视图 (/login/)
- 路由逻辑在 views_custom_login.py 中实现
""")

print("="*80)
print("测试建议:")
print("="*80)
print("""
1. 创建测试用户并分配不同数量的公司:
   - 用户A: 只属于鼎策 -> 应自动跳转到 /dingce/
   - 用户B: 属于鼎策和晟昌 -> 应显示公司选择界面
   - 用户C: 超级管理员 -> 应跳转到 /root/

2. 测试步骤:
   a. 使用 Django shell 创建测试用户
   b. 为用户分配不同的租户关系
   c. 尝试登录并观察跳转行为
""")

print("="*80)
