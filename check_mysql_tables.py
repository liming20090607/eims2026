import os
import sys
import django

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_local_mysql')
django.setup()

from django.db import connection

cursor = connection.cursor()

# List all eims_app tables
cursor.execute("SHOW TABLES LIKE 'eims_app_%'")
tables = cursor.fetchall()

print("=== MySQL 数据库中的 eims_app 表 ===\n")
for row in tables:
    table_name = row[0]
    # Check if tenant_id exists
    cursor.execute(f"DESCRIBE {table_name}")
    columns = cursor.fetchall()
    has_tenant = any(col[0] == 'tenant_id' for col in columns)
    marker = " [NO tenant_id]" if not has_tenant else ""
    print(f"  {table_name}{marker}")

print("\n✅ 检查完成！")
