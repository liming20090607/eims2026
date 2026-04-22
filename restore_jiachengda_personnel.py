#!/usr/bin/env python
"""
从eims_root恢复嘉诚达的完整人员数据
"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

import pymysql

print("=" * 70)
print("从eims_root恢复嘉诚达的完整人员数据")
print("=" * 70)

# 连接eims_root数据库
conn_root = pymysql.connect(
    host='localhost', port=3306, user='root', password='root123',
    database='eims_root', charset='utf8mb4'
)
cursor_root = conn_root.cursor()

# 连接eims_jiachengda数据库
conn_jcd = pymysql.connect(
    host='localhost', port=3306, user='root', password='root123',
    database='eims_jiachengda', charset='utf8mb4'
)
cursor_jcd = conn_jcd.cursor()

# 从eims_root获取嘉诚达(tenant_id=4)的完整人员信息
print("\n--- 步骤1: 从eims_root获取嘉诚达人员 ---")
cursor_root.execute("""
    SELECT id, personnel_code, name, gender, department, position, phone, 
           email, entry_time, leave_time, operator, remark, employee_id,
           project_id, project_code, project2_id, project_code2, project3_id, 
           project_code3, project4_id, project_code4, project5_id, project_code5,
           tenant_id
    FROM eims_app_personnel 
    WHERE tenant_id = 4 AND is_deleted = 0
    ORDER BY personnel_code
""")
root_personnel = cursor_root.fetchall()
print(f"eims_root中嘉诚达人员: {len(root_personnel)} 人")
for row in root_personnel[:5]:
    print(f"  {row[1]}: {row[2] or 'NULL'} (部门: {row[4] or 'NULL'})")

if len(root_personnel) > 5:
    print(f"  ... 还有 {len(root_personnel) - 5} 人")

# 查看当前eims_jiachengda中的JCDRY-人员
print("\n--- 步骤2: eims_jiachengda当前JCDRY-人员 ---")
cursor_jcd.execute("""
    SELECT id, personnel_code, name, department FROM eims_app_personnel 
    WHERE personnel_code LIKE 'JCDRY%' AND is_deleted = 0
""")
current_jcd = cursor_jcd.fetchall()
print(f"当前JCDRY-人员: {len(current_jcd)} 人")
for row in current_jcd:
    print(f"  ID={row[0]}, {row[1]}: '{row[2]}' (部门: {row[3]})")

# 从eims_root恢复数据到eims_jiachengda
print("\n--- 步骤3: 恢复数据 ---")
for root_row in root_personnel:
    pcode = root_row[1]
    if not pcode.startswith('JCDRY'):
        continue
    
    # 查找eims_jiachengda中对应的人员
    cursor_jcd.execute("""
        SELECT id FROM eims_app_personnel 
        WHERE personnel_code = %s AND is_deleted = 0
    """, (pcode,))
    jcd_rec = cursor_jcd.fetchone()
    
    if jcd_rec:
        jcd_id = jcd_rec[0]
        # 更新记录
        cursor_jcd.execute("""
            UPDATE eims_app_personnel 
            SET name = %s, gender = %s, department = %s, position = %s,
                phone = %s, email = %s, entry_time = %s, leave_time = %s,
                operator = %s, remark = %s, employee_id = %s,
                project_id = %s, project_code = %s,
                project2_id = %s, project_code2 = %s,
                project3_id = %s, project_code3 = %s,
                project4_id = %s, project_code4 = %s,
                project5_id = %s, project_code5 = %s
            WHERE id = %s
        """, (
            root_row[2], root_row[3], root_row[4], root_row[5],  # name, gender, dept, pos
            root_row[6], root_row[7], root_row[8], root_row[9],  # phone, email, entry, leave
            root_row[10], root_row[11], root_row[12],             # operator, remark, emp_id
            root_row[13], root_row[14],                           # project1
            root_row[15], root_row[16],                           # project2
            root_row[17], root_row[18],                           # project3
            root_row[19], root_row[20],                           # project4
            root_row[21], root_row[22],                           # project5
            jcd_id
        ))
        print(f"  更新: {pcode} -> {root_row[2] or 'NULL'}")
    else:
        # 插入新记录
        cursor_jcd.execute("""
            INSERT INTO eims_app_personnel (personnel_code, name, gender, department, position,
                phone, email, entry_time, leave_time, operator, remark, employee_id,
                project_id, project_code, project2_id, project_code2, project3_id, project_code3,
                project4_id, project_code4, project5_id, project_code5, tenant_id,
                is_deleted, create_time, update_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, NOW(), NOW())
        """, (
            root_row[1], root_row[2], root_row[3], root_row[4], root_row[5],
            root_row[6], root_row[7], root_row[8], root_row[9], root_row[10],
            root_row[11], root_row[12], root_row[13], root_row[14],
            root_row[15], root_row[16], root_row[17], root_row[18],
            root_row[19], root_row[20], root_row[21], root_row[22],
            root_row[23]  # tenant_id
        ))
        print(f"  插入: {pcode} -> {root_row[2] or 'NULL'}")

conn_jcd.commit()

# 验证结果
print("\n--- 步骤4: 验证结果 ---")
cursor_jcd.execute("""
    SELECT personnel_code, name, department, position 
    FROM eims_app_personnel 
    WHERE is_deleted = 0 AND personnel_code LIKE 'JCDRY%'
    ORDER BY personnel_code
""")
for row in cursor_jcd.fetchall():
    print(f"  {row[0]}: {row[1] or 'NULL'} (部门: {row[2] or 'NULL'}, 岗位: {row[3] or 'NULL'})")

cursor_jcd.execute("SELECT COUNT(*) FROM eims_app_personnel WHERE is_deleted = 0")
print(f"\n嘉诚达总人数: {cursor_jcd.fetchone()[0]}")

cursor_root.close()
conn_root.close()
cursor_jcd.close()
conn_jcd.close()

print("\n完成!")
