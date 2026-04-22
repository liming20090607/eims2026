"""
检查所有数据库中的人员编号情况
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connections

print("=" * 80)
print("检查所有数据库中的员工编号情况")
print("=" * 80)

databases = ['default', 'dingce', 'shengchang', 'jiachengda']
db_names = {
    'default': '系统默认库',
    'dingce': '广西鼎策',
    'shengchang': '广西盛昌',
    'jiachengda': '广西嘉诚达'
}

for db_name in databases:
    print(f"\n{'='*80}")
    print(f"数据库: {db_names.get(db_name, db_name)} ({db_name})")
    print(f"{'='*80}")
    
    try:
        with connections[db_name].cursor() as cursor:
            # 查询所有员工
            cursor.execute("""
                SELECT id, personnel_code, name, gender, tenant_id, is_deleted
                FROM eims_app_employee
                WHERE is_deleted = 0
                ORDER BY id
            """)
            
            employee_list = cursor.fetchall()
            
            print(f"\n总共有 {len(employee_list)} 条员工记录:")
            print(f"{'ID':<5} {'人员编号':<15} {'姓名':<10} {'性别':<6}")
            print("-" * 50)
            
            no_code_employees = []
            for emp in employee_list:
                eid, code, name, gender, tenant_id, is_deleted = emp
                code_display = code if code else "(空)"
                gender_display = '男' if gender == 0 else ('女' if gender == 1 else '其他')
                print(f"{eid:<5} {code_display:<15} {name:<10} {gender_display:<6}")
                
                if not code or code.strip() == '':
                    no_code_employees.append(emp)
            
            print(f"\n没有编号的员工: {len(no_code_employees)} 人")
            
            if no_code_employees:
                print("\n需要编号的员工:")
                for emp in no_code_employees:
                    eid, code, name, gender, tenant_id, is_deleted = emp
                    gender_display = '男' if gender == 0 else ('女' if gender == 1 else '其他')
                    print(f"  ID={eid}, 姓名={name}, 性别={gender_display}")
            
            # 检查重复
            cursor.execute("""
                SELECT name, COUNT(*) as cnt, GROUP_CONCAT(id) as ids
                FROM eims_app_employee
                WHERE is_deleted = 0
                GROUP BY name
                HAVING cnt > 1
            """)
            
            duplicates = cursor.fetchall()
            
            if duplicates:
                print(f"\n⚠️ 发现 {len(duplicates)} 个重复姓名:")
                for dup in duplicates:
                    name, cnt, ids = dup
                    print(f"  姓名: {name}, 重复 {cnt} 次, IDs: {ids}")
            else:
                print(f"\n✓ 没有重复姓名")
                
    except Exception as e:
        print(f"错误: {e}")
