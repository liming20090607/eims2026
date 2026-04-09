import os
import sys
import django

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection

cursor = connection.cursor()

# 检查 tenant_id 字段是否存在
cursor.execute("""
    SELECT COUNT(*) 
    FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'eims_app_userprofile' 
    AND COLUMN_NAME = 'tenant_id'
""")
exists = cursor.fetchone()[0]

if exists:
    print("✓ tenant_id 字段已存在")
else:
    print("正在添加 tenant_id 字段...")
    cursor.execute("""
        ALTER TABLE eims_app_userprofile 
        ADD COLUMN tenant_id INT NULL
    """)
    connection.commit()
    print("✓ tenant_id 字段已添加")

# 验证
cursor.execute("DESCRIBE eims_app_userprofile")
columns = cursor.fetchall()
print("\nUserProfile 表字段:")
for col in columns:
    print(f"  - {col[0]}")
