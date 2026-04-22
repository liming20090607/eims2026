"""修复陈连华的登录问题"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth.models import User
from eims_app.models import UserProfile, Tenant, Personnel

print("="*80)
print("修复陈连华的登录问题")
print("="*80)

# 查找陈连华的人员记录
personnel = Personnel.objects.filter(name='陈连华', tenant_id=4).first()
if not personnel:
    personnel = Personnel.objects.filter(name='陈连华').first()

if not personnel:
    print("未找到陈连华的人员记录")
    sys.exit(1)

print(f"\n人员记录: ID={personnel.id} 姓名={personnel.name} 编号={personnel.personnel_code}")
print(f"  部门: {personnel.department}")
print(f"  租户ID: {personnel.tenant_id}")

# 获取租户
tenant = Tenant.objects.get(id=personnel.tenant_id)
print(f"  租户: {tenant.name} (代码:{tenant.code})")

# 查找或创建User账户
# 尝试多种方式查找用户
user = None

# 方法1: 通过人员编号查找用户名
possible_usernames = [
    personnel.personnel_code,
    personnel.personnel_code.replace('-', '').lower(),
    'chenlianhua',
    'clh',
    personnel.personnel_code.lower(),
]

for username in possible_usernames:
    try:
        user = User.objects.get(username=username)
        print(f"\n✓ 找到用户: {user.username}")
        break
    except User.DoesNotExist:
        pass

if not user:
    print("\n未找到匹配的User账户，尝试通过部门人员创建...")
    # 检查是否已经有人用他的名字创建了用户
    users_with_same_name = User.objects.filter(
        first_name='陈连华'
    ) | User.objects.filter(
        last_name='陈连华'
    )
    if users_with_same_name.exists():
        user = users_with_same_name.first()
        print(f"✓ 找到同名用户: {user.username}")
    else:
        # 需要创建一个新用户
        print("\n需要创建新用户账户。以下信息供您参考：")
        print(f"  建议用户名: {personnel.personnel_code.lower().replace('-', '')}")
        print(f"  建议密码: 默认密码（需管理员设置）")
        print(f"  租户: {tenant.name}")
        
        # 自动创建用户
        username = personnel.personnel_code.lower().replace('-', '')
        user = User.objects.create_user(
            username=username,
            first_name='陈连华',
            email='',
            password='123456'  # 默认密码
        )
        print(f"\n✓ 已创建用户: {user.username}")

# 关联UserProfile
profile, created = UserProfile.objects.get_or_create(user=user)
print(f"\nUserProfile: {'已创建' if created else '已存在'}")
print(f"  当前租户: {profile.tenant}")

# 同步租户信息
if profile.tenant_id != personnel.tenant_id:
    profile.tenant = tenant
    profile.save(update_fields=['tenant'])
    print(f"  ✓ 已同步租户: {tenant.name}")
else:
    print(f"  ✓ 租户已正确: {tenant.name}")

print("\n" + "="*80)
print("修复完成！")
print("="*80)
print(f"\n登录信息:")
print(f"  用户名: {user.username}")
print(f"  密码: 123456 (默认密码，请登录后修改)")
print(f"  公司: {tenant.name}")
