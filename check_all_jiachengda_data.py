import os
import sys
import django

# Fix Python path
sys.path.insert(0, 'e:/')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection

print("=" * 80)
print("检查嘉诚达公司所有员工记录")
print("=" * 80)

cursor = connection.cursor()

# Check Employee table
cursor.execute("""
    SELECT id, personnel_code, name, gender, mobile, is_deleted
    FROM eims_app_employee
    WHERE tenant_id IS NOT NULL
    ORDER BY id
""")

employees = cursor.fetchall()
print(f"\nEmployee 表 (花名册) - 共 {len(employees)} 条记录:\n")
print(f"{'ID':<4} {'编号':<15} {'姓名':<10} {'性别':<6} {'手机':<15} {'删除状态'}")
print("-" * 70)

for emp in employees:
    eid, code, name, gender, mobile, is_deleted = emp
    gender_str = "男" if gender == 1 else "女" if gender == 2 else "其他"
    deleted_str = "已删除" if is_deleted else "正常"
    print(f"{eid:<4} {str(code):<15} {name:<10} {gender_str:<6} {str(mobile or ''):<15} {deleted_str}")

# Check Personnel table
cursor.execute("""
    SELECT id, personnel_code, name, gender, department, project_id, is_deleted
    FROM eims_app_personnel
    WHERE tenant_id IS NOT NULL
    ORDER BY id
""")

personnel = cursor.fetchall()
print(f"\n\nPersonnel 表 (人员去向) - 共 {len(personnel)} 条记录:\n")
print(f"{'ID':<4} {'编号':<15} {'姓名':<10} {'性别':<6} {'部门':<15} {'项目':<20} {'删除状态'}")
print("-" * 90)

for per in personnel:
    pid, code, name, gender, dept, proj, is_deleted = per
    gender_str = "男" if gender == 1 else "女" if gender == 2 else "其他"
    deleted_str = "已删除" if is_deleted else "正常"
    print(f"{pid:<4} {str(code):<15} {name:<10} {gender_str:<6} {str(dept or ''):<15} {str(proj or ''):<20} {deleted_str}")

# Check for duplicates
print("\n\n" + "=" * 80)
print("检查重复记录:")
print("=" * 80)

cursor.execute("""
    SELECT name, COUNT(*) as cnt
    FROM eims_app_employee
    WHERE tenant_id IS NOT NULL AND is_deleted = 0
    GROUP BY name
    HAVING COUNT(*) > 1
""")

dup_employees = cursor.fetchall()
if dup_employees:
    print(f"\nEmployee 表中发现 {len(dup_employees)} 个重复姓名:")
    for name, cnt in dup_employees:
        print(f"  - {name}: {cnt} 条记录")
else:
    print("\n✓ Employee 表中没有重复姓名")

cursor.execute("""
    SELECT name, COUNT(*) as cnt
    FROM eims_app_personnel
    WHERE tenant_id IS NOT NULL AND is_deleted = 0
    GROUP BY name
    HAVING COUNT(*) > 1
""")

dup_personnel = cursor.fetchall()
if dup_personnel:
    print(f"\nPersonnel 表中发现 {len(dup_personnel)} 个重复姓名:")
    for name, cnt in dup_personnel:
        print(f"  - {name}: {cnt} 条记录")
else:
    print("✓ Personnel 表中没有重复姓名")

print("\n" + "=" * 80)
print("检查完成!")
print("=" * 80)
