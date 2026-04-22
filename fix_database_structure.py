"""
修复数据库 - 使用 Django ORM 同步所有表结构
"""
import os
import sys
import django

sys.path.insert(0, 'e:\\')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EIMS2026.settings')

# 必须先导入 pymysql 并安装为 MySQLdb
import pymysql
pymysql.install_as_MySQLdb()

django.setup()

from django.core.management import call_command
from django.db import connection
import pymysql

print("=" * 60)
print("🔧 数据库结构修复工具")
print("=" * 60)

# 1. 先 fake 所有 eims_app migrations
print("\n1️⃣ 准备 migrations 状态...")
call_command('migrate', 'eims_app', '--fake', verbosity=0)
print("   ✅ eims_app migrations 已标记为已应用")

# 2. 使用 Django 的 schema editor 创建所有缺失的表
print("\n2️⃣ 使用 Django ORM 创建所有表...")

from django.apps import apps

# 获取所有 eims_app 的模型
eims_models = apps.get_app_config('eims_app').get_models()
print(f"   找到 {len(list(eims_models))} 个模型")

# 重新获取（因为上面迭代了一次）
eims_models = apps.get_app_config('eims_app').get_models()

# 对每个模型，尝试创建表
for model in eims_models:
    table_name = model._meta.db_table
    try:
        # 检查表是否存在
        with connection.cursor() as cursor:
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            if cursor.fetchone():
                print(f"   ℹ️ {table_name} 已存在")
                continue
        
        # 创建表
        from django.db import connection
        schema_editor = connection.schema_editor()
        schema_editor.create_model(model)
        print(f"   ✅ 创建 {table_name}")
    except Exception as e:
        print(f"   ⚠️ {table_name}: {str(e)[:50]}")

# 3. 验证关键表
print("\n3️⃣ 验证关键表...")
key_tables = [
    'eims_app_costprojectunified',
    'eims_app_costprojectinfo', 
    'eims_app_costconsultingreminder',
    'eims_app_tenant',
    'eims_app_department',
    'eims_app_role',
    'eims_app_userprofile',
    'eims_app_approvalchain',
]

with connection.cursor() as cursor:
    cursor.execute("SHOW TABLES")
    existing_tables = [row[0] for row in cursor.fetchall()]

all_ok = True
for table in key_tables:
    if table in existing_tables:
        print(f"   ✅ {table}")
    else:
        print(f"   ❌ {table} 缺失")
        all_ok = False

# 4. 创建 admin 用户和租户
print("\n4️⃣ 创建 admin 用户和租户...")
from django.contrib.auth.models import User
from eims_app.models import Tenant
from datetime import datetime

# 创建或更新 admin
if User.objects.filter(username='admin').exists():
    admin = User.objects.get(username='admin')
    admin.set_password('Admin@123')
    admin.is_superuser = True
    admin.is_staff = True
    admin.is_active = True
    admin.save()
    print("   ✅ admin 用户已更新")
else:
    User.objects.create_superuser('admin', 'admin@eims.com', 'Admin@123')
    print("   ✅ admin 用户已创建")

# 创建租户
now = datetime.now()
tenants = [
    ('dingce', '鼎策工程咨询', '鼎策'),
    ('shengchang', '晟昌工程科技', '晟昌'),
    ('jiachengda', '嘉诚达造价咨询', '嘉诚达'),
    ('root_admin', 'Root管理后台', 'Root'),
]

for code, name, short in tenants:
    Tenant.objects.update_or_create(
        code=code,
        defaults={
            'name': name,
            'short_name': short,
            'is_active': True,
            'logo': '',
            'contact_person': '',
            'contact_phone': '',
            'contact_email': '',
            'address': '',
            'project_code_prefix': '',
            'description': '',
            'remark': '',
            'create_time': now,
            'update_time': now,
        }
    )
    print(f"   ✅ 租户: {name}")

print("\n" + "=" * 60)
if all_ok:
    print("✅ 数据库修复完成！")
else:
    print("⚠️ 部分表仍有问题")
print("=" * 60)
