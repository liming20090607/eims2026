import os
import sys
import django

sys.path.insert(0, 'e:/')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection

print("=" * 80)
print("同步员工数据到 Personnel 表（简化版）")
print("=" * 80)

cursor = connection.cursor()

# List of employees to sync
employees_to_sync = [
    {'name': '秦林', 'code': 'DCRY-021', 'tenant_id': 1, 'gender': 1},
    {'name': '桂华', 'code': 'DCRY-022', 'tenant_id': 1, 'gender': 1},
    {'name': '王敏志', 'code': 'DCRY-023', 'tenant_id': 1, 'gender': 1},
    {'name': '林漓', 'code': 'DCRY-024', 'tenant_id': 1, 'gender': 1},
    {'name': '方永明', 'code': 'DCRY-025', 'tenant_id': 1, 'gender': 1},
    {'name': '唐薇薇', 'code': 'DCRY-026', 'tenant_id': 1, 'gender': 2},
    {'name': '宋弦弦', 'code': 'SCRY-006', 'tenant_id': 2, 'gender': 1},
]

print("\n同步数据到 Personnel 表:")
print("-" * 80)

for emp in employees_to_sync:
    name = emp['name']
    code = emp['code']
    tenant_id = emp['tenant_id']
    gender = emp['gender']
    
    # Check if active record exists
    cursor.execute("""
        SELECT id, personnel_code, tenant_id
        FROM eims_app_personnel
        WHERE name = %s AND is_deleted = 0
    """, [name])
    
    existing = cursor.fetchone()
    
    if existing:
        # Update existing record
        cursor.execute("""
            UPDATE eims_app_personnel
            SET personnel_code = %s, tenant_id = %s, gender = %s, update_time = NOW()
            WHERE id = %s
        """, [code, tenant_id, gender, existing[0]])
        print(f"✓ 更新: ID={existing[0]}, {name}: {existing[1]} -> {code}, tenant_id={tenant_id}")
    else:
        # Create new record - insert only required fields
        cursor.execute("""
            SELECT MAX(id) FROM eims_app_personnel
        """)
        max_id = cursor.fetchone()[0] or 0
        new_id = max_id + 1
        
        # Get employee_id from Employee table
        cursor.execute("""
            SELECT id FROM eims_app_employee
            WHERE name = %s AND personnel_code = %s AND is_deleted = 0
        """, [name, code])
        emp_result = cursor.fetchone()
        employee_id = emp_result[0] if emp_result else None
        
        # Use raw SQL with all default values
        sql = f"""
            INSERT INTO eims_app_personnel
            (id, personnel_code, name, gender, project_code, project_code2, project_code3, 
             project_code4, project_code5, department, position, phone, email, 
             entry_time, leave_time, operator, remark, employee_id, project_id, 
             project2_id, project3_id, project4_id, project5_id, tenant_id, is_deleted, 
             create_time, update_time)
            VALUES ({new_id}, '{code}', '{name}', {gender}, '', '', '', '', '', '', '', '', NULL,
             NULL, NULL, 'system', '', {str(employee_id) if employee_id else 'NULL'}, NULL, 
             NULL, NULL, NULL, NULL, NULL, {tenant_id}, 0, NOW(), NOW())
        """
        
        try:
            cursor.execute(sql)
            print(f"✓ 新建: ID={new_id}, {name}: {code}, tenant_id={tenant_id}")
        except Exception as e:
            print(f"✗ 失败: {name} - {str(e)}")

# Final verification
print("\n" + "=" * 80)
print("Personnel 表最终结果:")
print("=" * 80)

cursor.execute("""
    SELECT p.id, p.personnel_code, p.name, p.gender, p.tenant_id
    FROM eims_app_personnel p
    WHERE p.name IN ('秦林', '桂华', '王敏志', '林漓', '方永明', '唐薇薇', '宋弦弦')
    AND p.is_deleted = 0
    ORDER BY p.tenant_id, p.name
""")

final_records = cursor.fetchall()
print(f"\n{'ID':<5} {'编号':<15} {'姓名':<10} {'性别':<6} {'公司'}")
print("-" * 70)

for rec in final_records:
    company = "广西鼎策工程顾问" if rec[4] == 1 else "广西晟昌工程科技" if rec[4] == 2 else "其他"
    gender = "男" if rec[3] == 1 else "女" if rec[3] == 2 else "其他"
    print(f"{rec[0]:<5} {rec[1]:<15} {rec[2]:<10} {gender:<6} {company}")

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
