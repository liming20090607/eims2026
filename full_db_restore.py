import pymysql
import subprocess
import sys
import os

sys.path.insert(0, 'e:\\')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EIMS2026.settings')

print("=" * 60)
print("🔄 完整数据库重建流程")
print("=" * 60)

# Step 1: 重建数据库
print("\n1️⃣ 重建数据库...")
conn = pymysql.connect(host='127.0.0.1', user='root', password='mysql2026!', charset='utf8mb4')
cursor = conn.cursor()
cursor.execute('DROP DATABASE IF EXISTS eims2026_dev')
cursor.execute('CREATE DATABASE eims2026_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
conn.close()
print("   ✅ 数据库已重建")

# Step 2: 临时禁用外键检查，应用 migrations
print("\n2️⃣ 应用 migrations（禁用外键检查）...")

# 先禁用外键检查
conn = pymysql.connect(host='127.0.0.1', user='root', password='mysql2026!', database='eims2026_dev', charset='utf8mb4')
cursor = conn.cursor()
cursor.execute('SET FOREIGN_KEY_CHECKS=0')
conn.commit()
conn.close()

# 应用基础 migrations（跳过有问题的 eims_app）
result = subprocess.run(
    [sys.executable, 'manage.py', 'migrate', '--run-syncdb'],
    capture_output=True,
    text=True,
    cwd='e:\\EIMS2026'
)
if 'OK' in result.stdout or result.returncode == 0:
    print("   ✅ 基础 migrations 已应用")
else:
    print(f"   ⚠️ {result.stderr[:200]}")

# 重新启用外键检查
conn = pymysql.connect(host='127.0.0.1', user='root', password='mysql2026!', database='eims2026_dev', charset='utf8mb4')
cursor = conn.cursor()
cursor.execute('SET FOREIGN_KEY_CHECKS=1')
conn.commit()
conn.close()

# Step 3: Fake eims_app migrations
print("\n3️⃣ Fake eims_app migrations...")
result = subprocess.run(
    [sys.executable, 'manage.py', 'migrate', 'eims_app', '--fake'],
    capture_output=True,
    text=True,
    cwd='e:\\EIMS2026'
)
print(f"   ✅ {result.stdout.count('FAKED')} migrations faked")

# Step 4: 从 JSON 备份加载数据
print("\n4️⃣ 从 JSON 备份加载数据...")
result = subprocess.run(
    [sys.executable, 'manage.py', 'loaddata', 'sqlite_backup.json'],
    capture_output=True,
    text=True,
    cwd='e:\\EIMS2026'
)
if result.returncode == 0:
    print("   ✅ 数据加载成功")
else:
    print(f"   ⚠️ {result.stderr[:200]}")

# Step 5: 创建 admin 用户和租户
print("\n5️⃣ 创建 admin 用户和租户...")
import django
django.setup()

from django.contrib.auth.models import User
from eims_app.models import Tenant
from datetime import datetime

# 创建 admin
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@eims.com', 'Admin@123')
    print("   ✅ admin 用户已创建")
else:
    admin = User.objects.get(username='admin')
    admin.set_password('Admin@123')
    admin.save()
    print("   ✅ admin 密码已重置")

# 创建租户
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
tenants_data = [
    ('dingce', '鼎策工程咨询', '鼎策'),
    ('shengchang', '晟昌工程科技', '晟昌'),
    ('jiachengda', '嘉诚达造价咨询', '嘉诚达'),
    ('root_admin', 'Root管理后台', 'Root'),
]

for code, name, short in tenants_data:
    Tenant.objects.get_or_create(
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

# Step 6: 验证
print("\n6️⃣ 验证数据库...")
conn = pymysql.connect(host='127.0.0.1', user='root', password='mysql2026!', database='eims2026_dev', charset='utf8mb4')
cursor = conn.cursor()
cursor.execute('SHOW TABLES')
tables = [t[0] for t in cursor.fetchall()]
print(f"   📊 表数量: {len(tables)}")

key_tables = {
    'eims_app_costprojectunified': '造价项目统一表',
    'eims_app_costprojectinfo': '造价项目信息表',
    'eims_app_tenant': '租户表',
    'auth_user': '用户表',
    'eims_app_department': '部门表',
    'eims_app_role': '角色表',
}

all_ok = True
for table, desc in key_tables.items():
    found = table in tables
    if not found:
        all_ok = False
    print(f"   {'✅' if found else '❌'} {table} ({desc})")

conn.close()

print("\n" + "=" * 60)
if all_ok:
    print("✅ 数据库重建完成！所有关键表已创建")
else:
    print("⚠️ 部分表缺失，请检查 migrations")
print("=" * 60)
