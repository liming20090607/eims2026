import os
import sys
import django

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_local_mysql')
django.setup()

from django.db import connection

cursor = connection.cursor()

# 直接添加 tenant_id 字段（如果不存在的话）
print("正在检查并添加 tenant_id 字段...")
try:
    cursor.execute("""
        ALTER TABLE eims_app_userprofile 
        ADD COLUMN tenant_id INT NULL
    """)
    connection.commit()
    print("✓ tenant_id 字段已添加")
except Exception as e:
    if "Duplicate column name" in str(e) or "1060" in str(e):
        print("✓ tenant_id 字段已存在，跳过")
    else:
        print(f"✗ 错误: {e}")
        raise

# 验证字段
cursor.execute("DESCRIBE eims_app_userprofile")
columns = cursor.fetchall()
print("\nUserProfile 表字段:")
for col in columns:
    marker = " <-- 新字段" if col[0] == 'tenant_id' else ""
    print(f"  - {col[0]} ({col[1]}){marker}")

# 检查 Tenant 表
cursor.execute("SELECT COUNT(*) as cnt FROM eims_app_tenant")
tenant_count = cursor.fetchone()[0]
print(f"\nTenant 表记录数: {tenant_count}")

if tenant_count > 0:
    cursor.execute("SELECT id, name, code FROM eims_app_tenant")
    for row in cursor.fetchall():
        print(f"  - ID: {row[0]}, Name: {row[1]}, Code: {row[2]}")

print("\n✅ 完成！")
