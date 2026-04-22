#!/usr/bin/env python
"""
修复嘉诚达人员姓名数据
从原始数据恢复JCDRY-人员的姓名
"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

import pymysql

print("=" * 70)
print("修复嘉诚达人员姓名数据")
print("=" * 70)

conn_jcd = pymysql.connect(
    host='localhost', port=3306, user='root', password='root123',
    database='eims_jiachengda', charset='utf8mb4'
)
cursor_jcd = conn_jcd.cursor()

# 原始数据（从default数据库迁移前的数据）
original_data = {
    'JCDRY-110': {'name': '黎绍昆', 'gender': 0},
    'JCDRY-001': {'name': '秦有林', 'gender': 0},  # 秦有林是嘉诚达的
    'JCDRY-002': {'name': '潘金莲', 'gender': 1},
    'JCDRY-003': {'name': '吴松', 'gender': 0},
    'JCDRY-004': {'name': '李逵', 'gender': 0},
    'JCDRY-005': {'name': '刘备', 'gender': 0},
}

print("\n--- 修复前 ---")
cursor_jcd.execute("""
    SELECT id, personnel_code, name, department 
    FROM eims_app_personnel 
    WHERE personnel_code LIKE 'JCDRY%' AND is_deleted = 0
    ORDER BY personnel_code
""")
for row in cursor_jcd.fetchall():
    print(f"  ID={row[0]}, {row[1]}: '{row[2]}' (部门: {row[3]})")

# 更新姓名
print("\n--- 更新姓名 ---")
for pcode, data in original_data.items():
    cursor_jcd.execute("""
        UPDATE eims_app_personnel 
        SET name = %s, gender = %s
        WHERE personnel_code = %s AND is_deleted = 0
    """, (data['name'], data['gender'], pcode))
    print(f"  {pcode} -> {data['name']}")

conn_jcd.commit()

# 验证结果
print("\n--- 修复后 ---")
cursor_jcd.execute("""
    SELECT personnel_code, name, gender, department, position 
    FROM eims_app_personnel 
    WHERE personnel_code LIKE 'JCDRY%' AND is_deleted = 0
    ORDER BY personnel_code
""")
for row in cursor_jcd.fetchall():
    gender_str = '男' if row[2] == 0 else '女' if row[2] == 1 else '未知'
    print(f"  {row[0]}: {row[1]} ({gender_str}, 部门: {row[3]}, 岗位: {row[4]})")

cursor_jcd.close()
conn_jcd.close()

print("\n完成!")
