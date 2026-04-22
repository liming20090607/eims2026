"""
检查嘉诚达公司 Personnel 表的数据
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connections

print("=" * 80)
print("检查嘉诚达公司 (jiachengda) Personnel 表数据")
print("=" * 80)

with connections['jiachengda'].cursor() as cursor:
    # 1. 检查表结构
    print("\n1. 检查 eims_app_personnel 表结构:")
    cursor.execute("SHOW COLUMNS FROM eims_app_personnel LIKE '%code%'")
    code_columns = cursor.fetchall()
    print(f"   找到 {len(code_columns)} 个编号相关字段:")
    for col in code_columns:
        print(f"   - {col[0]} ({col[1]})")
    
    # 2. 查询所有 Personnel 记录
    print("\n2. 查询所有 Personnel 数据:")
    cursor.execute("""
        SELECT id, personnel_code, name, gender, department, tenant_id, is_deleted
        FROM eims_app_personnel
        WHERE is_deleted = 0
        ORDER BY id
    """)
    
    personnel_list = cursor.fetchall()
    
    print(f"\n   总共有 {len(personnel_list)} 条 Personnel 记录:\n")
    print(f"   {'ID':<5} {'personnel_code':<15} {'姓名':<10} {'性别':<6} {'部门':<20}")
    print("   " + "-" * 70)
    
    no_code_personnel = []
    for p in personnel_list:
        pid, code, name, gender, dept, tenant_id, is_deleted = p
        code_display = code if code else "(空)"
        gender_display = '男' if gender == 0 else ('女' if gender == 1 else '其他')
        dept_display = dept if dept else "-"
        print(f"   {pid:<5} {code_display:<15} {name:<10} {gender_display:<6} {dept_display:<20}")
        
        if not code or code.strip() == '':
            no_code_personnel.append(p)
    
    # 3. 检查重复
    print(f"\n3. 检查重复姓名:")
    cursor.execute("""
        SELECT name, COUNT(*) as cnt, GROUP_CONCAT(id) as ids
        FROM eims_app_personnel
        WHERE is_deleted = 0
        GROUP BY name
        HAVING cnt > 1
    """)
    
    duplicates = cursor.fetchall()
    
    if duplicates:
        print(f"   ⚠️ 发现 {len(duplicates)} 个重复姓名:")
        for dup in duplicates:
            name, cnt, ids = dup
            print(f"   - 姓名: {name}, 重复 {cnt} 次, IDs: {ids}")
    else:
        print("   ✓ 没有发现重复姓名")
    
    # 4. 编号方案
    print(f"\n4. Personnel 编号方案:")
    
    cursor.execute("""
        SELECT MAX(CAST(SUBSTRING(personnel_code, 7) AS UNSIGNED)) as max_num
        FROM eims_app_personnel
        WHERE is_deleted = 0
        AND personnel_code LIKE 'JCDRY-%'
    """)
    
    result = cursor.fetchone()
    max_num = result[0] if result[0] else 0
    next_num = max_num + 1
    
    print(f"   当前最大编号: JCDRY-{max_num:03d}")
    print(f"   下一个可用编号: JCDRY-{next_num:03d}")
    
    if no_code_personnel:
        print(f"\n   需要为 {len(no_code_personnel)} 个 Personnel 记录分配编号:")
        assignments = []
        for i, p in enumerate(no_code_personnel, 1):
            pid, code, name, gender, dept, tenant_id, is_deleted = p
            new_code = f"JCDRY-{next_num + i - 1:03d}"
            assignments.append((pid, name, new_code))
            print(f"   - ID={pid}, {name} -> {new_code}")
        
        confirm = input(f"\n   是否执行编号分配? (y/n): ").strip().lower()
        
        if confirm == 'y':
            print("\n   开始分配编号...")
            for pid, name, new_code in assignments:
                cursor.execute(
                    "UPDATE eims_app_personnel SET personnel_code = %s WHERE id = %s",
                    [new_code, pid]
                )
                print(f"   ✓ {name} (ID={pid}) -> {new_code}")
            
            connections['jiachengda'].commit()
            print(f"\n   ✓ 成功分配 {len(assignments)} 个编号!")
        else:
            print("\n   已取消操作")
    else:
        print("   ✓ 所有 Personnel 记录都已有编号")

print("\n" + "=" * 80)
print("检查完成!")
print("=" * 80)
