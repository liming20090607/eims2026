import os
import sys
import django

sys.path.insert(0, 'e:/')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection

print("=" * 80)
print("检查需要修复编号的员工记录")
print("=" * 80)

cursor = connection.cursor()

# Check specific employees mentioned
employees_to_check = ['秦林', '桂华', '王敏志', '林漓', '方永明', '唐薇薇', '宋弦弦']

cursor.execute("""
    SELECT id, personnel_code, name, tenant_id, is_deleted
    FROM eims_app_employee
    WHERE name IN %s
    ORDER BY name, id
""", [tuple(employees_to_check)])

records = cursor.fetchall()
print(f"\n找到 {len(records)} 条记录:\n")
print(f"{'ID':<5} {'编号':<20} {'姓名':<10} {'租户ID':<10} {'状态'}")
print("-" * 70)

for rec in records:
    status = "已删除" if rec[4] else "正常"
    print(f"{rec[0]:<5} {str(rec[1] or 'None'):<20} {rec[2]:<10} {str(rec[3] or 'None'):<10} {status}")

# Check for duplicates
print("\n" + "=" * 80)
print("检查重复姓名:")
print("=" * 80)

for name in employees_to_check:
    cursor.execute("""
        SELECT COUNT(*) 
        FROM eims_app_employee 
        WHERE name = %s AND is_deleted = 0
    """, [name])
    count = cursor.fetchone()[0]
    if count > 1:
        print(f"⚠ {name}: {count} 条记录（需要清理）")
    elif count == 1:
        print(f"✓ {name}: 1 条记录")
    else:
        print(f"✗ {name}: 0 条记录（缺失）")

print("\n" + "=" * 80)
