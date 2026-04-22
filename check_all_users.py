"""
检查并显示所有数据库中的用户数据
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import connections
from eims_app.models.model_user import UserProfile, UserTenantRelation
from eims_app.models.model_tenant import Tenant

User = get_user_model()

databases = ['default', 'dingce', 'shengchang', 'jiachengda', 'root_admin']

print("="*80)
print("检查所有数据库中的用户数据")
print("="*80)

for db in databases:
    print(f"\n{'='*80}")
    print(f"数据库: {db}")
    print("="*80)
    
    try:
        with connections[db].cursor() as cursor:
            # Check if tables exist
            cursor.execute("SHOW TABLES LIKE 'auth_user'")
            if cursor.fetchone():
                cursor.execute("SELECT COUNT(*) FROM auth_user")
                user_count = cursor.fetchone()[0]
                print(f"  ✓ auth_user 表存在，用户数: {user_count}")
                
                if user_count > 0:
                    cursor.execute("SELECT id, username, email, is_superuser, is_active FROM auth_user")
                    users = cursor.fetchall()
                    print(f"\n  用户列表:")
                    for u in users:
                        print(f"    - ID:{u[0]} 用户名:{u[1]} 邮箱:{u[2]} 超管:{u[3]} 活跃:{u[4]}")
            else:
                print(f"  ✗ auth_user 表不存在")
            
            # Check Tenant table
            cursor.execute("SHOW TABLES LIKE 'eims_app_tenant'")
            if cursor.fetchone():
                cursor.execute("SELECT COUNT(*) FROM eims_app_tenant")
                tenant_count = cursor.fetchone()[0]
                print(f"\n  ✓ eims_app_tenant 表存在，租户数: {tenant_count}")
                
                if tenant_count > 0:
                    cursor.execute("SELECT id, code, name, short_name FROM eims_app_tenant")
                    tenants = cursor.fetchall()
                    print(f"\n  租户列表:")
                    for t in tenants:
                        print(f"    - ID:{t[0]} 代码:{t[1]} 名称:{t[2]} 简称:{t[3]}")
            else:
                print(f"\n  ✗ eims_app_tenant 表不存在")
            
            # Check UserProfile table
            cursor.execute("SHOW TABLES LIKE 'eims_app_userprofile'")
            if cursor.fetchone():
                cursor.execute("SELECT COUNT(*) FROM eims_app_userprofile")
                profile_count = cursor.fetchone()[0]
                print(f"\n  ✓ eims_app_userprofile 表存在，资料数: {profile_count}")
            else:
                print(f"\n  ✗ eims_app_userprofile 表不存在")
            
            # Check UserTenantRelation table
            cursor.execute("SHOW TABLES LIKE 'eims_app_usertenantrelation'")
            if cursor.fetchone():
                cursor.execute("SELECT COUNT(*) FROM eims_app_usertenantrelation")
                relation_count = cursor.fetchone()[0]
                print(f"  ✓ eims_app_usertenantrelation 表存在，关联数: {relation_count}")
            else:
                print(f"  ✗ eims_app_usertenantrelation 表不存在")
                
    except Exception as e:
        print(f"  ✗ 错误: {str(e)}")

print("\n" + "="*80)
print("检查当前 default 数据库（eims_root）中的用户数据")
print("="*80)

# Check current users in default database
users = User.objects.all()
print(f"\n当前系统中的用户总数: {users.count()}")

for user in users:
    print(f"\n  用户名: {user.username}")
    print(f"    邮箱: {user.email}")
    print(f"    超管: {user.is_superuser}")
    print(f"    活跃: {user.is_active}")
    
    # Check profile
    try:
        profile = user.profile
        print(f"    姓名: {profile.real_name}")
        print(f"    默认公司: {profile.tenant.name if profile.tenant else '无'}")
    except:
        print(f"    资料: 无")
    
    # Check tenant relations
    relations = UserTenantRelation.objects.filter(user=user)
    if relations.exists():
        print(f"    关联租户: {[r.tenant.name for r in relations]}")
    else:
        print(f"    关联租户: 无")

print("\n" + "="*80)
