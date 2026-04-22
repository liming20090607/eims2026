import os
import sys
import django

# Fix Python path
sys.path.insert(0, 'e:/')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection

print("=" * 80)
print("同步 Personnel 表数据到 Employee 表")
print("=" * 80)

cursor = connection.cursor()

# Get all active Personnel records
cursor.execute("""
    SELECT id, personnel_code, name, gender, department
    FROM eims_app_personnel
    WHERE tenant_id IS NOT NULL 
    AND is_deleted = 0
    ORDER BY id
""")

personnel_records = cursor.fetchall()
print(f"\n找到 {len(personnel_records)} 条有效的 Personnel 记录\n")

# Get existing Employee names and codes
cursor.execute("""
    SELECT name, personnel_code
    FROM eims_app_employee
    WHERE tenant_id IS NOT NULL 
    AND is_deleted = 0
""")

existing_employees = {row[0]: row[1] for row in cursor.fetchall()}
print(f"现有 {len(existing_employees)} 个 Employee 记录\n")

# Find Personnel not in Employee table
missing_employees = []
for pid, pcode, pname, pgender, pdept in personnel_records:
    if pname not in existing_employees:
        missing_employees.append((pid, pcode, pname, pgender, pdept))

print(f"发现 {len(missing_employees)} 个在 Personnel 中但不在 Employee 中的员工:\n")
print(f"{'PID':<5} {'编号':<15} {'姓名':<10} {'性别':<6} {'部门'}")
print("-" * 60)

for pid, pcode, pname, pgender, pdept in missing_employees:
    gender_str = "男" if pgender == 1 else "女" if pgender == 2 else "其他"
    print(f"{pid:<5} {str(pcode):<15} {pname:<10} {gender_str:<6} {str(pdept or '')}")

if not missing_employees:
    print("\n✓ 所有 Personnel 都已在 Employee 表中")
else:
    print(f"\n是否将这些员工添加到 Employee 表? (y/n): ", end='')
    response = input().strip().lower()
    
    if response == 'y':
        # Get next available ID
        cursor.execute("SELECT MAX(id) FROM eims_app_employee")
        max_id = cursor.fetchone()[0] or 0
        next_id = max_id + 1
        
        # Get max JCDRY number
        cursor.execute("""
            SELECT MAX(CAST(SUBSTRING(personnel_code, 7) AS UNSIGNED)) as max_num
            FROM eims_app_employee
            WHERE personnel_code LIKE 'JCDRY-%'
        """)
        result = cursor.fetchone()
        max_jcdry = result[0] if result[0] else 0
        next_jcdry_num = max_jcdry + 1
        
        print(f"\n开始添加 {len(missing_employees)} 个员工...\n")
        
        added_count = 0
        for pid, pcode, pname, pgender, pdept in missing_employees:
            # Use Personnel's code if it's JCDRY format, otherwise generate new
            if pcode and str(pcode).startswith('JCDRY-'):
                new_code = pcode
            else:
                new_code = f"JCDRY-{next_jcdry_num:03d}"
                next_jcdry_num += 1
            
            try:
                cursor.execute("""
                    INSERT INTO eims_app_employee 
                    (id, personnel_code, name, gender, mobile, tenant_id, is_deleted, create_time, update_time,
                     id_card, native_place, ethnic, education, address, home_phone, emergency_contact, 
                     emergency_phone, wechat, email, admin_position, tech_position, 
                     professional_qualification, professional_title, job_qualification, operator, remark)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW(),
                     '', '', '', '', '', '', '', '', '', NULL, '', '', '', '', '', 'system', '')
                """, [next_id, new_code, pname, pgender, '', 3, 0])  # tenant_id=3 for jiachengda, mobile=''
                
                print(f"  ✓ 添加: ID={next_id}, 编号={new_code}, 姓名={pname}, 性别={'男' if pgender==1 else '女' if pgender==2 else '其他'}")
                next_id += 1
                added_count += 1
            except Exception as e:
                print(f"  ✗ 失败: {pname} - {str(e)}")
        
        print(f"\n成功添加 {added_count} 个员工到 Employee 表")
        
        confirm = input("\n确认提交数据库更改? (y/n): ").strip().lower()
        if confirm == 'y':
            connection.commit()
            print("✓ 数据库已更新!")
        else:
            connection.rollback()
            print("✗ 已回滚，未做任何更改")

print("\n" + "=" * 80)
print("完成!")
print("=" * 80)
