import os
import sys
import django

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_local_mysql')
django.setup()

from django.db import connection

cursor = connection.cursor()

# 需要添加 tenant_id 的所有表
tables = [
    'eims_app_projectdetail',
    'eims_app_contract',
    'eims_app_personnel',
    'eims_app_employee',
    'eims_app_department',
    'eims_app_notice',
    'eims_app_filemanage',
    'eims_app_outputpayment',
    'eims_app_personnelallocation',
    'eims_app_personnelcertificate',
    'eims_app_projectdynamic',
    'eims_app_archiveapproval',
    'eims_app_contractapproval',
    'eims_app_sealapproval',
]

print("=== 批量添加 tenant_id 字段 ===\n")

for table in tables:
    try:
        cursor.execute(f"""
            ALTER TABLE {table} 
            ADD COLUMN tenant_id INT NULL
        """)
        connection.commit()
        print(f"✓ {table}: 已添加 tenant_id")
    except Exception as e:
        if "Duplicate column name" in str(e) or "1060" in str(e):
            print(f"  {table}: tenant_id 已存在，跳过")
        else:
            print(f"✗ {table}: 错误 - {e}")

# 验证 ProjectDetail 表
print("\n验证 ProjectDetail 表:")
cursor.execute("DESCRIBE eims_app_projectdetail")
columns = cursor.fetchall()
for col in columns:
    if col[0] == 'tenant_id':
        print(f"  ✓ tenant_id 字段存在 ({col[1]})")
        break
else:
    print("  ✗ tenant_id 字段不存在")

print("\n✅ 批量添加完成！")
