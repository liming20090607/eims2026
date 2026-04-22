import os
import sys

sys.path.insert(0, 'e:\\')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EIMS2026.settings')

import django
django.setup()

import pymysql

# 连接到 MySQL
conn = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='mysql2026!',
    database='eims2026_dev',
    charset='utf8mb4'
)

cursor = conn.cursor()

# 检查并添加 project_code_prefix 字段
try:
    cursor.execute("""
        ALTER TABLE eims_app_tenant 
        ADD COLUMN project_code_prefix VARCHAR(50) DEFAULT '' 
        AFTER is_active
    """)
    print("✅ Added project_code_prefix column")
except Exception as e:
    if 'Duplicate column name' in str(e):
        print("ℹ️ project_code_prefix column already exists")
    else:
        print(f"❌ Error: {e}")

# 检查并添加 description 字段
try:
    cursor.execute("""
        ALTER TABLE eims_app_tenant 
        ADD COLUMN description TEXT 
        AFTER project_code_prefix
    """)
    print("✅ Added description column")
except Exception as e:
    if 'Duplicate column name' in str(e):
        print("ℹ️ description column already exists")
    else:
        print(f"❌ Error: {e}")

# 检查并添加 created_at 字段
try:
    cursor.execute("""
        ALTER TABLE eims_app_tenant 
        ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP 
        AFTER description
    """)
    print("✅ Added created_at column")
except Exception as e:
    if 'Duplicate column name' in str(e):
        print("ℹ️ created_at column already exists")
    else:
        print(f"❌ Error: {e}")

# 检查并添加 updated_at 字段
try:
    cursor.execute("""
        ALTER TABLE eims_app_tenant 
        ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP 
        AFTER created_at
    """)
    print("✅ Added updated_at column")
except Exception as e:
    if 'Duplicate column name' in str(e):
        print("ℹ️ updated_at column already exists")
    else:
        print(f"❌ Error: {e}")

# 创建租户
tenants = [
    ('dingce', '鼎策工程咨询', True),
    ('shengchang', '晟昌工程科技', True),
    ('jiachengda', '嘉诚达造价咨询', True),
    ('root_admin', 'Root 管理后台', True),
]

for code, name, is_active in tenants:
    try:
        cursor.execute("""
            INSERT INTO eims_app_tenant (code, name, is_active) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE name=VALUES(name)
        """, (code, name, is_active))
        print(f"✅ Tenant created/updated: {name} ({code})")
    except Exception as e:
        print(f"⚠️ Tenant {code}: {e}")

conn.commit()
conn.close()

print("\n" + "="*60)
print("✅ Database schema fixed and tenants created!")
print("="*60)
