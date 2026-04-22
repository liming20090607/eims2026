"""
检查嘉诚达公司的员工数据（花名册），找出没有编号的员工
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connections

print("=" * 80)
print("检查嘉诚达公司 (jiachengda) 员工数据 - 花名册")
print("=" * 80)

with connections['jiachengda'].cursor() as cursor:
    # 查询所有员工
    cursor.execute("""
        SELECT id, personnel_code, name, gender, tenant_id, is_deleted
        FROM eims_app_employee
        WHERE is_deleted = 0
        AND tenant_id IS NOT NULL
        ORDER BY id
    """)
    
    employee_list = cursor.fetchall()
    
    print(f"\n总共有 {len(employee_list)} 条员工记录:\n")
    print(f"{'ID':<5} {'人员编号':<15} {'姓名':<10} {'性别':<6}")
    print("-" * 60)
    
    for emp in employee_list:
        eid, code, name, gender, tenant_id, is_deleted = emp
        code_display = code if code else "(无编号)"
        gender_display = '男' if gender == 0 else ('女' if gender == 1 else '其他')
        print(f"{eid:<5} {code_display:<15} {name:<10} {gender_display:<6}")
    
    # 检查没有编号的员工
    no_code_employees = [emp for emp in employee_list if not emp[1]]
    
    print(f"\n" + "=" * 80)
    print(f"没有编号的员工: {len(no_code_employees)} 人")
    print("=" * 80)
    
    if no_code_employees:
        for emp in no_code_employees:
            eid, code, name, gender, tenant_id, is_deleted = emp
            gender_display = '男' if gender == 0 else ('女' if gender == 1 else '其他')
            print(f"  ID={eid}, 姓名={name}, 性别={gender_display}")
    
    # 检查是否有重复姓名
    print(f"\n" + "=" * 80)
    print("检查重复姓名:")
    print("=" * 80)
    
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
        print(f"发现 {len(duplicates)} 个重复姓名:\n")
        for dup in duplicates:
            name, cnt, ids = dup
            print(f"  姓名: {name}, 重复次数: {cnt}, IDs: {ids}")
    else:
        print("  没有发现重复姓名")
    
    # 获取下一个可用的编号
    print(f"\n" + "=" * 80)
    print("编号方案:")
    print("=" * 80)
    
    cursor.execute("""
        SELECT MAX(CAST(SUBSTRING(personnel_code, 7) AS UNSIGNED)) as max_num
        FROM eims_app_employee
        WHERE is_deleted = 0
        AND tenant_id IS NOT NULL
        AND personnel_code LIKE 'JCDRY-___'
    """)
    
    result = cursor.fetchone()
    max_num = result[0] if result[0] else 0
    next_num = max_num + 1
    
    print(f"  当前最大编号: JCDRY-{max_num:03d}")
    print(f"  下一个可用编号: JCDRY-{next_num:03d}")
    print(f"\n  需要为 {len(no_code_employees)} 个员工分配编号:")
    
    assignments = []
    for i, emp in enumerate(no_code_employees, 1):
        eid, code, name, gender, tenant_id, is_deleted = emp
        new_code = f"JCDRY-{next_num + i - 1:03d}"
        assignments.append((eid, name, new_code))
        print(f"    ID={eid}, {name} -> {new_code}")
    
    # 询问是否执行
    print(f"\n" + "=" * 80)
    if len(assignments) > 0:
        confirm = input("是否执行编号分配? (y/n): ").strip().lower()
        
        if confirm == 'y':
            print("\n开始分配编号...")
            for eid, name, new_code in assignments:
                cursor.execute(
                    "UPDATE eims_app_employee SET personnel_code = %s WHERE id = %s",
                    [new_code, eid]
                )
                print(f"  ✓ {name} (ID={eid}) -> {new_code}")
            
            # 提交事务
            connections['jiachengda'].commit()
            print(f"\n✓ 成功分配 {len(assignments)} 个编号!")
        else:
            print("\n已取消操作")
    else:
        print("  所有员工都已有编号，无需分配")
