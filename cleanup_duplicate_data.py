import os
import sys
import django

sys.path.insert(0, 'e:/')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection

print("=" * 80)
print("清理嘉诚达数据库中的重复和错误数据")
print("=" * 80)

cursor = connection.cursor()

# 1. Check for admin duplicates
print("\n1. 检查 admin 重复记录:")
cursor.execute("""
    SELECT id, personnel_code, name, tenant_id, is_deleted
    FROM eims_app_employee
    WHERE name = 'admin' AND is_deleted = 0
    ORDER BY id
""")
admin_records = cursor.fetchall()
print(f"   找到 {len(admin_records)} 条 admin 记录:\n")
for rec in admin_records:
    print(f"   ID={rec[0]}, 编号={rec[1]}, 租户ID={rec[3]}")

# Keep only the JCDRY-006 one (tenant_id=3), delete others
if len(admin_records) > 1:
    print("\n   建议保留 JCDRY-006 (嘉诚达)，删除其他:")
    to_delete = [r[0] for r in admin_records if r[1] != 'JCDRY-006']
    to_keep = [r[0] for r in admin_records if r[1] == 'JCDRY-006']
    print(f"   保留: {to_keep}")
    print(f"   删除: {to_delete}")
    
    confirm = input("\n   是否删除这些重复的 admin 记录? (y/n): ").strip().lower()
    if confirm == 'y':
        for eid in to_delete:
            # Soft delete by setting is_deleted=1
            cursor.execute("UPDATE eims_app_employee SET is_deleted = 1 WHERE id = %s", [eid])
            print(f"   ✓ 软删除 Employee ID={eid}")
        
        # Also soft delete corresponding Personnel records
        cursor.execute("UPDATE eims_app_personnel SET is_deleted = 1 WHERE name = 'admin' AND personnel_code NOT IN ('JCDRY-006') AND is_deleted = 0")
        deleted_count = cursor.rowcount
        print(f"   ✓ 软删除 {deleted_count} 条 Personnel 记录")

# 2. Check for non-JCDRY codes in jiachengda tenant
print("\n\n2. 检查非 JCDRY 格式的编号:")
cursor.execute("""
    SELECT id, personnel_code, name
    FROM eims_app_employee
    WHERE tenant_id = 3 
    AND is_deleted = 0
    AND personnel_code NOT LIKE 'JCDRY-%'
    ORDER BY id
""")
non_jcdry = cursor.fetchall()
print(f"   找到 {len(non_jcdry)} 条非 JCDRY 格式的记录:\n")
for rec in non_jcdry:
    print(f"   ID={rec[0]}, 编号={rec[1]}, 姓名={rec[2]}")

if non_jcdry:
    print("\n   这些记录的 tenant_id=3 (嘉诚达) 但编号不是 JCDRY 格式")
    print("   可能原因: 数据迁移时未正确过滤")
    
    action = input("\n   如何处理? (1=软删除, 2=更改为正确的租户, 3=跳过): ").strip()
    
    if action == '1':
        for eid, code, name in non_jcdry:
            cursor.execute("UPDATE eims_app_employee SET is_deleted = 1 WHERE id = %s", [eid])
            print(f"   ✓ 软删除 Employee ID={eid}, 编号={code}")
        
        # Also delete from Personnel
        codes_to_delete = [r[1] for r in non_jcdry]
        placeholders = ','.join(['%s'] * len(codes_to_delete))
        cursor.execute(f"UPDATE eims_app_personnel SET is_deleted = 1 WHERE personnel_code IN ({placeholders}) AND is_deleted = 0", codes_to_delete)
        print(f"   ✓ 软删除对应的 Personnel 记录")
    
    elif action == '2':
        print("\n   需要将这些记录分配到正确的租户:")
        print("   - DCRY-XXX -> dingce (tenant_id=1)")
        print("   - SCRY-XXX -> shengchang (tenant_id=2)")
        
        confirm = input("\n   确认执行? (y/n): ").strip().lower()
        if confirm == 'y':
            for eid, code, name in non_jcdry:
                if code.startswith('DCRY-'):
                    new_tenant = 1  # dingce
                elif code.startswith('SCRY-'):
                    new_tenant = 2  # shengchang
                else:
                    continue
                
                cursor.execute("UPDATE eims_app_employee SET tenant_id = %s WHERE id = %s", [new_tenant, eid])
                print(f"   ✓ 更新 Employee ID={eid}, {code} -> tenant_id={new_tenant}")
                
                # Update Personnel too
                cursor.execute("UPDATE eims_app_personnel SET tenant_id = %s WHERE personnel_code = %s AND is_deleted = 0", [new_tenant, code])
                print(f"   ✓ 更新 Personnel {code} -> tenant_id={new_tenant}")

# Commit or rollback
confirm_final = input("\n\n确认提交所有更改到数据库? (y/n): ").strip().lower()
if confirm_final == 'y':
    connection.commit()
    print("✓ 数据库已更新!")
else:
    connection.rollback()
    print("✗ 已回滚，未做任何更改")

print("\n" + "=" * 80)
print("完成!")
print("=" * 80)

