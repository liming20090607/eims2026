import os
import sys
import django

sys.path.insert(0, 'e:/')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection

print("=" * 80)
print("修复苏晓霞的人员编号冲突")
print("=" * 80)

cursor = connection.cursor()

# Check current status
cursor.execute("SELECT id, personnel_code, name FROM eims_app_personnel WHERE name = '苏晓霞' AND is_deleted = 0")
personnel_record = cursor.fetchone()
print(f"\nPersonnel 表中的记录: ID={personnel_record[0]}, 编号={personnel_record[1]}, 姓名={personnel_record[2]}")

# Get max JCDRY number
cursor.execute("""
    SELECT MAX(CAST(SUBSTRING(personnel_code, 7) AS UNSIGNED)) as max_num
    FROM eims_app_employee
    WHERE personnel_code LIKE 'JCDRY-%'
""")
result = cursor.fetchone()
max_jcdry = result[0] if result[0] else 0
new_code = f"JCDRY-{max_jcdry + 1:03d}"

print(f"当前最大JCDRY编号: JCDRY-{max_jcdry:03d}")
print(f"新编号: {new_code}")

# Update Personnel table
cursor.execute("""
    UPDATE eims_app_personnel 
    SET personnel_code = %s 
    WHERE name = '苏晓霞' AND is_deleted = 0
""", [new_code])

print(f"\n✓ Personnel 表已更新: 苏晓霞 -> {new_code}")

# Insert into Employee table
cursor.execute("SELECT MAX(id) FROM eims_app_employee")
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
""", [new_id, new_code, '苏晓霞', 1, '', 3, 0])  # gender=1 for male based on Personnel data

print(f"✓ Employee 表已添加: ID={new_id}, 编号={new_code}, 姓名=苏晓霞")

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
