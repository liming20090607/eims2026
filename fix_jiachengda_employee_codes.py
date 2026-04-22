"""
检查并自动编号嘉诚达公司的员工（修复花名册中编号为空的问题）
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connections

print("=" * 80)
print("检查嘉诚达公司 (jiachengda) 员工编号情况")
print("=" * 80)

with connections['jiachengda'].cursor() as cursor:
    # 1. 检查表结构
    print("\n1. 检查 eims_app_employee 表结构:")
    cursor.execute("SHOW COLUMNS FROM eims_app_employee LIKE '%code%'")
    code_columns = cursor.fetchall()
    print(f"   找到 {len(code_columns)} 个编号相关字段:")
    for col in code_columns:
        print(f"   - {col[0]} ({col[1]})")
    
    # 2. 查询所有员工
    print("\n2. 查询所有员工数据:")
    cursor.execute("""
        SELECT id, personnel_code, name, gender, tenant_id, is_deleted
        FROM eims_app_employee
        WHERE is_deleted = 0
        AND tenant_id IS NOT NULL
        ORDER BY id
    """)
    
    employee_list = cursor.fetchall()
    
    print(f"\n   总共有 {len(employee_list)} 条员工记录:\n")
    print(f"   {'ID':<5} {'personnel_code':<20} {'姓名':<10} {'性别':<6}")
    print("   " + "-" * 60)
    
    no_code_employees = []
    for emp in employee_list:
        eid, code, name, gender, tenant_id, is_deleted = emp
        code_display = code if code else "(空)"
        gender_display = '男' if gender == 0 else ('女' if gender == 1 else '其他')
        print(f"   {eid:<5} {code_display:<20} {name:<10} {gender_display:<6}")
        
        # 检查是否没有编号
        if not code or code.strip() == '':
            no_code_employees.append(emp)
    
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
        
        # 询问是否删除重复记录
        print("\n   建议保留最早的记录（ID最小的），删除其他重复记录")
        confirm_delete = input("\n   是否删除重复记录（保留ID最小的）? (y/n): ").strip().lower()
        
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
    else:
        print("   ✓ 没有发现重复姓名")
    
    # 4. 为没有编号的员工分配编号
    print(f"\n4. 编号分配方案:")
    
    # 获取当前最大编号
    cursor.execute("""
        SELECT MAX(CAST(SUBSTRING(personnel_code, 7) AS UNSIGNED)) as max_num
        FROM eims_app_employee
        WHERE is_deleted = 0
        AND tenant_id IS NOT NULL
        AND personnel_code LIKE 'JCDRY-%'
    """)
    
    result = cursor.fetchone()
    max_num = result[0] if result[0] else 0
    next_num = max_num + 1
    
    print(f"   当前最大编号: JCDRY-{max_num:03d}")
    print(f"   下一个可用编号: JCDRY-{next_num:03d}")
    
    if no_code_employees:
        print(f"\n   需要为 {len(no_code_employees)} 个员工分配编号:")
        assignments = []
        for i, emp in enumerate(no_code_employees, 1):
            eid, code, name, gender, tenant_id, is_deleted = emp
            new_code = f"JCDRY-{next_num + i - 1:03d}"
            assignments.append((eid, name, new_code))
            print(f"   - ID={eid}, {name} -> {new_code}")
        
        # 询问是否执行
        confirm = input(f"\n   是否执行编号分配? (y/n): ").strip().lower()
        
        if confirm == 'y':
            print("\n   开始分配编号...")
            for eid, name, new_code in assignments:
                cursor.execute(
                    "UPDATE eims_app_employee SET personnel_code = %s WHERE id = %s",
                    [new_code, eid]
                )
                print(f"   ✓ {name} (ID={eid}) -> {new_code}")
            
            connections['jiachengda'].commit()
            print(f"\n   ✓ 成功分配 {len(assignments)} 个编号!")
        else:
            print("\n   已取消操作")
    else:
        print("   ✓ 所有员工都已有编号，无需分配")

print("\n" + "=" * 80)
print("检查完成!")
print("=" * 80)

