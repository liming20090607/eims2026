"""
修复嘉诚达公司员工编号：将旧格式编号统一为JCDRY-XXX格式
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connections

print("=" * 80)
print("修复嘉诚达公司 (jiachengda) 员工编号格式")
print("=" * 80)

with connections['jiachengda'].cursor() as cursor:
    # 1. 查询所有使用旧格式编号的员工
    print("\n1. 查询使用旧格式编号的员工:")
    cursor.execute("""
        SELECT id, personnel_code, name, gender
        FROM eims_app_employee
        WHERE is_deleted = 0
        AND tenant_id IS NOT NULL
        AND (personnel_code NOT LIKE 'JCDRY-%' OR personnel_code IS NULL OR personnel_code = '')
        ORDER BY id
    """)
    
    old_format_employees = cursor.fetchall()
    
    if old_format_employees:
        print(f"\n   发现 {len(old_format_employees)} 个使用旧格式编号的员工:\n")
        print(f"   {'ID':<5} {'旧编号':<15} {'姓名':<10} {'性别':<6}")
        print("   " + "-" * 50)
        
        for emp in old_format_employees:
            eid, code, name, gender = emp
            code_display = code if code else "(空)"
            gender_display = '男' if gender == 0 else ('女' if gender == 1 else '其他')
            print(f"   {eid:<5} {code_display:<15} {name:<10} {gender_display:<6}")
    else:
        print("   ✓ 所有员工都使用JCDRY格式编号")
    
    # 2. 获取当前最大JCDRY编号
    cursor.execute("""
        SELECT MAX(CAST(SUBSTRING(personnel_code, 7) AS UNSIGNED)) as max_num
        FROM eims_app_employee
        WHERE is_deleted = 0
        AND tenant_id IS NOT NULL
        AND personnel_code LIKE 'JCDRY-%'
    """)
    
    result = cursor.fetchone()
    max_jcdry_num = result[0] if result[0] else 0
    
    print(f"\n2. 当前编号状态:")
    print(f"   最大JCDRY编号: JCDRY-{max_jcdry_num:03d}")
    print(f"   下一个可用编号: JCDRY-{max_jcdry_num + 1:03d}")
    
    # 3. 检查重复姓名
    print(f"\n3. 检查重复姓名:")
    cursor.execute("""
        SELECT name, COUNT(*) as cnt, GROUP_CONCAT(id) as ids
        FROM eims_app_employee
        WHERE is_deleted = 0
        AND tenant_id IS NOT NULL
        GROUP BY name
        HAVING cnt > 1
    """)
    
    duplicates = cursor.fetchall()
    
    if duplicates:
        print(f"   ⚠️ 发现 {len(duplicates)} 个重复姓名:")
        for dup in duplicates:
            name, cnt, ids = dup
            print(f"   - 姓名: {name}, 重复 {cnt} 次, IDs: {ids}")
        
        print("\n   建议：删除重复记录，保留ID最小的")
        confirm_delete = input("   是否删除重复记录? (y/n): ").strip().lower()
        
        if confirm_delete == 'y':
            for dup in duplicates:
                name, cnt, ids = dup
                id_list = [int(x) for x in ids.split(',')]
                id_list.sort()
                keep_id = id_list[0]
                delete_ids = id_list[1:]
                
                print(f"\n   保留: ID={keep_id} ({name})")
                for del_id in delete_ids:
                    cursor.execute("DELETE FROM eims_app_employee WHERE id = %s", [del_id])
                    print(f"   删除: ID={del_id} ({name})")
            
            connections['jiachengda'].commit()
            print("\n   ✓ 重复记录已删除")
            
            # 重新查询旧格式编号的员工
            cursor.execute("""
                SELECT id, personnel_code, name, gender
                FROM eims_app_employee
                WHERE is_deleted = 0
                AND tenant_id IS NOT NULL
                AND (personnel_code NOT LIKE 'JCDRY-%' OR personnel_code IS NULL OR personnel_code = '')
                ORDER BY id
            """)
            old_format_employees = cursor.fetchall()
    else:
        print("   ✓ 没有重复姓名")
    
    # 4. 为旧格式编号的员工分配新编号
    if old_format_employees:
        print(f"\n4. 编号分配方案:")
        print(f"   需要为 {len(old_format_employees)} 个员工重新分配JCDRY格式编号\n")
        
        next_num = max_jcdry_num + 1
        assignments = []
        
        for i, emp in enumerate(old_format_employees, 1):
            eid, old_code, name, gender = emp
            new_code = f"JCDRY-{next_num + i - 1:03d}"
            assignments.append((eid, old_code, name, new_code))
            print(f"   ID={eid}, {name}: {old_code or '(空)'} -> {new_code}")
        
        # 确认执行
        confirm = input(f"\n   是否执行编号更新? (y/n): ").strip().lower()
        
        if confirm == 'y':
            print("\n   开始更新编号...")
            for eid, old_code, name, new_code in assignments:
                cursor.execute(
                    "UPDATE eims_app_employee SET personnel_code = %s WHERE id = %s",
                    [new_code, eid]
                )
                print(f"   ✓ {name} (ID={eid}): {old_code or '(空)'} -> {new_code}")
            
            connections['jiachengda'].commit()
            print(f"\n   ✓ 成功更新 {len(assignments)} 个员工编号!")
        else:
            print("\n   已取消操作")
    else:
        print(f"\n4. ✓ 所有员工都已有JCDRY格式编号，无需更新")

print("\n" + "=" * 80)
print("修复完成!")
print("=" * 80)

