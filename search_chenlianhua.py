"""查找所有包含陈连华的记录"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth.models import User
from eims_app.models import UserProfile, Tenant, Personnel

print("="*80)
print("全面搜索陈连华")
print("="*80)

# 1. 搜索所有用户
print("\n1. 所有用户:")
for user in User.objects.all()[:20]:
    print(f"  ID:{user.id} 用户名:{user.username} 姓:{user.last_name} 名:{user.first_name} 邮箱:{user.email}")

# 2. 搜索人员记录
print("\n2. 所有人员记录（包含陈）:")
for p in Personnel.objects.filter(name__icontains='陈')[:10]:
    print(f"  ID:{p.id} 姓名:{p.name} 编号:{p.personnel_code} 部门:{p.department} 租户ID:{p.tenant_id}")

# 3. 搜索所有UserProfile
print("\n3. UserProfile关联:")
for up in UserProfile.objects.select_related('user', 'tenant').all()[:10]:
    print(f"  用户:{up.user.username} 姓名:{up.user.get_full_name()} 租户:{up.tenant.name if up.tenant else None}")

# 4. 查看嘉诚达租户信息
print("\n4. 嘉诚达租户:")
jiachengda = Tenant.objects.filter(code='jiachengda').first()
if jiachengda:
    print(f"  ID:{jiachengda.id} 名称:{jiachengda.name}")
    print(f"  关联的UserProfile数量: {UserProfile.objects.filter(tenant=jiachengda).count()}")
