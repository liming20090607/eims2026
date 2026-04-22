#!/usr/bin/env python
"""
检查eims_jiachengda数据库中的Employee表数据
"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

import pymysql

print("=" * 70)
print("检查eims_jiachengda数据库中的Employee表数据")
print("=" * 70)

conn_jcd = pymysql.connect(
    host='localhost', port=3306, user='root', password='root123',
    database='eims_jiachengda', charset='utf8mb4'
)
cursor_jcd = conn_jcd.cursor()

# 检查Employee表结构
print("\n--- Employee表结构 ---")
cursor_jcd.execute("DESCRIBE eims_app_employee")
columns = cursor_jcd.fetchall()
for col in columns:
    print(f"  {col[0]}: {col[1]}")

# 查看所有Employee记录
print("\n--- Employee记录 ---")
cursor_jcd.execute("SELECT * FROM eims_app_employee WHERE is_deleted = 0")
emps = cursor_jcd.fetchall()
print(f"总记录数: {len(emps)}")
for row in emps:
    print(f"  {row}")

# 检查Personnel表中的employee_id关联
print("\n--- Personnel与Employee关联 ---")
cursor_jcd.execute("""
    SELECT p.id, p.personnel_code, p.name, p.employee_id, p.department, p.position
    FROM eims_app_personnel p
    WHERE p.is_deleted = 0
    ORDER BY p.personnel_code
""")
personnels = cursor_jcd.fetchall()
for row in personnels:
    print(f"  Personnel ID={row[0]}, {row[1]}: name='{row[2]}', employee_id={row[3]}, dept={row[4]}, pos={row[5]}")

cursor_jcd.close()
conn_jcd.close()

print("\n完成!")
