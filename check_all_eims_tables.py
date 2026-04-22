"""
直接查询数据库中所有 eims_app 开头的表
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection

print("=" * 80)
print("数据库中所有 eims_app 表")
print("=" * 80)

with connection.cursor() as cursor:
    cursor.execute("SHOW TABLES LIKE 'eims_app_%'")
    tables = cursor.fetchall()
    
    print(f"\n共找到 {len(tables)} 个表:\n")
    for i, table in enumerate(tables, 1):
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"{i:3d}. {table_name:<50} ({count} 条记录)")

print("\n" + "=" * 80)
