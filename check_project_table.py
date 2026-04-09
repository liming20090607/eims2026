"""检查数据库中是否存在 eims_app_project 表"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# 检查所有包含 project 的表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%project%'")
tables = cursor.fetchall()

print("数据库中所有包含 'project' 的表:")
for table in tables:
    print(f"  - {table[0]}")

# 检查是否有 eims_app_project 表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='eims_app_project'")
if cursor.fetchone():
    print("\n✓ eims_app_project 表存在")
else:
    print("\n✗ eims_app_project 表不存在!")
    print("  这解释了为什么访问 /admin/eims_app/project/ 会报错")

# 检查 eims_app_projectdetail 表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='eims_app_projectdetail'")
if cursor.fetchone():
    print("✓ eims_app_projectdetail 表存在")
else:
    print("✗ eims_app_projectdetail 表不存在!")

conn.close()
