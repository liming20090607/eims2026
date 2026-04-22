import os
import sys
import django

sys.path.insert(0, 'e:/')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection

print("=" * 80)
print("修复员工编号并清理重复记录（修正版）")
print("=" * 80)

cursor = connection.cursor()

# Define the corrections needed
# 鼎策 employees (tenant_id=1): DCRY-XXX
dingce_employees = [
    {'name': '秦林', 'gender': 1},      # 男
    {'name': '桂华', 'gender': 1},      # 男
    {'name': '王敏志', 'gender': 1},    # 男
    {'name': '林漓', 'gender': 1},      # 男
    {'name': '方永明', 'gender': 1},    # 男
    {'name': '唐薇薇', 'gender': 2},    # 女
]

# 盛昌 employees (tenant_id=2): SCRY-XXX
shengchang_employees = [
    {'name': '宋弦弦', 'gender': 1},    # 男
]

print("\n1. 获取当前最大编号（包括已删除的记录）:")
print("-" * 80)

# Get max DCRY number (including deleted)
cursor.execute("""
    SELECT MAX(CAST(SUBSTRING(personnel_code, 6) AS UNSIGNED)) as max_num
    FROM eims_app_employee
    WHERE personnel_code LIKE 'DCRY-%'
""")
result = cursor.fetchone()
max_dcry = result[0] if result[0] else 0
print(f"   当前最大 DCRY 编号（含已删除）: DCRY-{max_dcry:03d}")

# Get max SCRY number (including deleted)
cursor.execute("""
    SELECT MAX(CAST(SUBSTRING(personnel_code, 6) AS UNSIGNED)) as max_num
    FROM eims_app_employee
    WHERE personnel_code LIKE 'SCRY-%'
""")
result = cursor.fetchone()
max_scry = result[0] if result[0] else 0
print(f"   当前最大 SCRY 编号（含已删除）: SCRY-{max_scry:03d}")

# Start from next number
next_dcry = max_dcry + 1
next_scry = max_scry + 1

print(f"\n   下一个可用 DCRY: DCRY-{next_dcry:03d}")
print(f"   下一个可用 SCRY: SCRY-{next_scry:03d}")

# First, delete ALL duplicate/deleted records to free up codes
print(f"\n2. 清理重复和已删除记录:")
print("-" * 80)

all_employees = dingce_employees + shengchang_employees
for emp in all_employees:
    name = emp['name']
    
    # Find all records for this person
    cursor.execute("""
        SELECT id, personnel_code, is_deleted
        FROM eims_app_employee
        WHERE name = %s
        ORDER BY is_deleted, id
    """, [name])
    
    records = cursor.fetchall()
    
    if len(records) > 1:
        print(f"   {name}: 发现 {len(records)} 条记录，开始清理...")
        
        # Keep the first active record, delete all others
        active_record = None
        deleted_records = []
        
        for rec in records:
            if not rec[2]:  # is_deleted = 0
                if active_record is None:
                    active_record = rec
                else:
                    # Duplicate active record, delete it
                    cursor.execute("DELETE FROM eims_app_employee WHERE id = %s", [rec[0]])
                    print(f"     删除重复活动记录: ID={rec[0]}, code={rec[1]}")
            else:
                deleted_records.append(rec)
        
        # Delete all deleted records to free up their codes
        for rec in deleted_records:
            cursor.execute("DELETE FROM eims_app_employee WHERE id = %s", [rec[0]])
            print(f"     删除已删除记录: ID={rec[0]}, code={rec[1]}")

print("\n3. 处理鼎策公司员工 (6人):")
print("-" * 80)

dingce_updates = []
for emp in dingce_employees:
    name = emp['name']
    gender = emp['gender']
    
    # Check if active record exists
    cursor.execute("""
        SELECT id, personnel_code, tenant_id
        FROM eims_app_employee
        WHERE name = %s AND is_deleted = 0
    """, [name])
    
    existing = cursor.fetchone()
    
    if existing:
        # Update existing record
        new_code = f"DCRY-{next_dcry:03d}"
        cursor.execute("""
            UPDATE eims_app_employee 
            SET personnel_code = %s, tenant_id = 1, update_time = NOW()
            WHERE id = %s
        """, [new_code, existing[0]])
        dingce_updates.append(f"✓ 更新: ID={existing[0]}, {name}: {existing[1]} -> {new_code}, tenant_id=1")
        next_dcry += 1
    else:
        # Create new record
        new_code = f"DCRY-{next_dcry:03d}"
        cursor.execute("""
            SELECT MAX(id) FROM eims_app_employee
        """)
        max_id = cursor.fetchone()[0] or 0
        new_id = max_id + 1
        
        cursor.execute("""
            INSERT INTO eims_app_employee 
            (id, personnel_code, name, gender, mobile, tenant_id, is_deleted, create_time, update_time,
             id_card, native_place, ethnic, education, address, home_phone, emergency_contact, 
             emergency_phone, wechat, email, admin_position, tech_position, 
             professional_qualification, professional_title, job_qualification, operator, remark)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW(),
             '', '', '', '', '', '', '', '', '', NULL, '', '', '', '', '', 'system', '')
        """, [new_id, new_code, name, gender, '', 1, 0])
        dingce_updates.append(f"✓ 新建: ID={new_id}, {name}: {new_code}, tenant_id=1")
        next_dcry += 1

for update_msg in dingce_updates:
    print(f"   {update_msg}")

print(f"\n4. 处理盛昌公司员工 (1人):")
print("-" * 80)

shengchang_updates = []
for emp in shengchang_employees:
    name = emp['name']
    gender = emp['gender']
    
    # Check if active record exists
    cursor.execute("""
        SELECT id, personnel_code, tenant_id
        FROM eims_app_employee
        WHERE name = %s AND is_deleted = 0
    """, [name])
    
    existing = cursor.fetchone()
    
    if existing:
        # Update existing record
        new_code = f"SCRY-{next_scry:03d}"
        cursor.execute("""
            UPDATE eims_app_employee 
            SET personnel_code = %s, tenant_id = 2, update_time = NOW()
            WHERE id = %s
        """, [new_code, existing[0]])
        shengchang_updates.append(f"✓ 更新: ID={existing[0]}, {name}: {existing[1]} -> {new_code}, tenant_id=2")
        next_scry += 1
    else:
        # Create new record
        new_code = f"SCRY-{next_scry:03d}"
        cursor.execute("""
            SELECT MAX(id) FROM eims_app_employee
        """)
        max_id = cursor.fetchone()[0] or 0
        new_id = max_id + 1
        
        cursor.execute("""
            INSERT INTO eims_app_employee 
            (id, personnel_code, name, gender, mobile, tenant_id, is_deleted, create_time, update_time,
             id_card, native_place, ethnic, education, address, home_phone, emergency_contact, 
             emergency_phone, wechat, email, admin_position, tech_position, 
             professional_qualification, professional_title, job_qualification, operator, remark)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW(),
             '', '', '', '', '', '', '', '', '', NULL, '', '', '', '', '', 'system', '')
        """, [new_id, new_code, name, gender, '', 2, 0])
        shengchang_updates.append(f"✓ 新建: ID={new_id}, {name}: {new_code}, tenant_id=2")
        next_scry += 1

for update_msg in shengchang_updates:
    print(f"   {update_msg}")

# Final summary
print("\n" + "=" * 80)
print("最终结果预览:")
print("=" * 80)

cursor.execute("""
    SELECT id, personnel_code, name, tenant_id, gender
    FROM eims_app_employee
    WHERE name IN %s AND is_deleted = 0
    ORDER BY tenant_id, name
""", [tuple([e['name'] for e in dingce_employees + shengchang_employees])])

final_records = cursor.fetchall()
print(f"\n{'ID':<5} {'编号':<15} {'姓名':<10} {'公司':<20} {'性别'}")
print("-" * 70)

for rec in final_records:
    company = "广西鼎策工程顾问" if rec[3] == 1 else "广西晟昌工程科技" if rec[3] == 2 else "其他"
    gender = "男" if rec[4] == 1 else "女" if rec[4] == 2 else "其他"
    print(f"{rec[0]:<5} {rec[1]:<15} {rec[2]:<10} {company:<20} {gender}")

confirm = input("\n\n确认提交所有更改到数据库? (y/n): ").strip().lower()
if confirm == 'y':
    connection.commit()
    print("✓ 数据库已更新!")
else:
    connection.rollback()
    print("✗ 已回滚，未做任何更改")

print("\n" + "=" * 80)
print("完成!")
print("=" * 80)
