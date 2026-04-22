#!/usr/bin/env python
"""
修复MySQL数据库中的人员数据
"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

import pymysql

print("=" * 70)
print("修复MySQL数据库中的人员数据")
print("=" * 70)

# 连接eims_root数据库，查找完整的人员信息
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

# 连接eims_dingce数据库
conn_dc = pymysql.connect(
    host='localhost', port=3306, user='root', password='root123',
    database='eims_dingce', charset='utf8mb4'
)
cursor_dc = conn_dc.cursor()

# 1. 从eims_root中获取嘉诚达的人员信息（tenant_id=4）
print("\n--- 步骤1: 从eims_root获取嘉诚达人员信息 ---")
cursor_root.execute("""
    SELECT personnel_code, name, department, position, gender, phone, tenant_id
    FROM eims_app_personnel 
    WHERE tenant_id = 4 AND is_deleted = 0
    ORDER BY personnel_code
""")
jiachengda_from_root = cursor_root.fetchall()
print(f"eims_root中嘉诚达人员: {len(jiachengda_from_root)} 人")
for row in jiachengda_from_root[:5]:
    print(f"  {row[0]}: {row[1]} (部门: {row[2]})")

# 2. 查看eims_jiachengda中当前的人员
print("\n--- 步骤2: eims_jiachengda当前人员 ---")
cursor_jcd.execute("""
    SELECT id, personnel_code, name, department, tenant_id
    FROM eims_app_personnel 
    WHERE is_deleted = 0
    ORDER BY personnel_code
""")
current_jcd = cursor_jcd.fetchall()
print(f"eims_jiachengda中人员: {len(current_jcd)} 人")
for row in current_jcd:
    print(f"  ID={row[0]}, {row[1]}: {row[2] or 'NULL'} (部门: {row[3]}, tenant: {row[4]})")

# 3. 修复eims_jiachengda中的JCDRY-记录（name为NULL的）
print("\n--- 步骤3: 修复eims_jiachengda中name为NULL的JCDRY-记录 ---")
cursor_jcd.execute("""
    SELECT id, personnel_code FROM eims_app_personnel 
    WHERE personnel_code LIKE 'JCDRY%' AND (name IS NULL OR name = '') AND is_deleted = 0
""")
null_name_records = cursor_jcd.fetchall()
for rec_id, pcode in null_name_records:
    # 从root数据库中查找对应的人员
    cursor_root.execute("""
        SELECT name, department, position, gender, phone FROM eims_app_personnel
        WHERE personnel_code = %s AND is_deleted = 0
    """, (pcode,))
    root_rec = cursor_root.fetchone()
    if root_rec:
        cursor_jcd.execute("""
            UPDATE eims_app_personnel 
            SET name = %s, department = %s, position = %s, gender = %s, phone = %s
            WHERE id = %s
        """, (root_rec[0], root_rec[1], root_rec[2], root_rec[3], root_rec[4], rec_id))
        print(f"  修复: {pcode} -> {root_rec[0]}")
    else:
        print(f"  警告: {pcode} 在root中未找到")

conn_jcd.commit()

# 4. 删除eims_jiachengda中属于鼎策的人员（RY001-012等）
print("\n--- 步骤4: 删除eims_jiachengda中属于鼎策的人员 ---")
cursor_jcd.execute("""
    SELECT id, personnel_code, name FROM eims_app_personnel 
    WHERE personnel_code LIKE 'RY%' AND tenant_id = 4 AND is_deleted = 0
""")
dc_in_jcd = cursor_jcd.fetchall()
if dc_in_jcd:
    print(f"发现 {len(dc_in_jcd)} 个属于鼎策的人员在嘉诚达数据库中:")
    for rec_id, pcode, name in dc_in_jcd:
        print(f"  删除: ID={rec_id}, {pcode}: {name}")
    # 软删除（设置is_deleted=1）
    codes_to_delete = [r[1] for r in dc_in_jcd]
    cursor_jcd.execute("""
        UPDATE eims_app_personnel SET is_deleted = 1
        WHERE personnel_code IN (%s)
    """ % ','.join(['%s'] * len(codes_to_delete)), codes_to_delete)
    conn_jcd.commit()
else:
    print("未发现需要删除的记录")

# 5. 检查eims_dingce中的JCDRY-人员并删除
print("\n--- 步骤5: 清理eims_dingce中的嘉诚达人员 ---")
cursor_dc.execute("""
    SELECT id, personnel_code, name FROM eims_app_personnel 
    WHERE personnel_code LIKE 'JCDRY%' AND is_deleted = 0
""")
jcd_in_dc = cursor_dc.fetchall()
if jcd_in_dc:
    print(f"发现 {len(jcd_in_dc)} 个嘉诚达人员在鼎策数据库中:")
    for rec_id, pcode, name in jcd_in_dc:
        print(f"  删除: ID={rec_id}, {pcode}: {name}")
    codes_to_delete = [r[1] for r in jcd_in_dc]
    cursor_dc.execute("""
        UPDATE eims_app_personnel SET is_deleted = 1
        WHERE personnel_code IN (%s)
    """ % ','.join(['%s'] * len(codes_to_delete)), codes_to_delete)
    conn_dc.commit()
else:
    print("未发现需要删除的记录")

# 6. 验证结果
print("\n--- 步骤6: 验证修复结果 ---")
cursor_jcd.execute("SELECT COUNT(*) FROM eims_app_personnel WHERE is_deleted = 0")
print(f"eims_jiachengda人员: {cursor_jcd.fetchone()[0]}")

cursor_jcd.execute("""
    SELECT personnel_code, name, department FROM eims_app_personnel 
    WHERE is_deleted = 0 ORDER BY personnel_code
""")
for row in cursor_jcd.fetchall():
    print(f"  {row[0]}: {row[1] or 'NULL'} (部门: {row[2] or 'NULL'})")

cursor_dc.execute("SELECT COUNT(*) FROM eims_app_personnel WHERE is_deleted = 0")
print(f"\neims_dingce人员: {cursor_dc.fetchone()[0]}")

cursor_root.close()
conn_root.close()
cursor_jcd.close()
conn_jcd.close()
cursor_dc.close()
conn_dc.close()

print("\n完成!")

