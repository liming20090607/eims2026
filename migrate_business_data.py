"""
完整业务数据迁移脚本
迁移员工、人员花名册、部门、项目等业务数据到MySQL
"""
import os
import sys
import django
import sqlite3
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.contrib.auth import get_user_model
from eims_app.models.model_tenant import Tenant
from eims_app.models.model_employee import Employee
from eims_app.models.model_personnel import Personnel
from eims_app.models.model_department import Department

User = get_user_model()

# 找到最新的备份文件
backup_dir = 'backup'
backups = [f for f in os.listdir(backup_dir) if f.endswith('.sqlite3')]
backups.sort(reverse=True)
latest_backup = os.path.join(backup_dir, backups[0])

print(f"{'='*70}")
print(f"完整业务数据迁移")
print(f"源文件: {latest_backup}")
print(f"{'='*70}\n")

# 连接SQLite
sqlite_conn = sqlite3.connect(latest_backup)
sqlite_cursor = sqlite_conn.cursor()

# 统计信息
stats = {
    'departments': {'created': 0, 'skipped': 0},
    'employees': {'created': 0, 'skipped': 0},
    'personnel': {'created': 0, 'skipped': 0},
    'errors': []
}

def migrate_departments():
    """迁移部门数据"""
    print("[1/4] 迁移部门数据...")
    
    sqlite_cursor.execute("SELECT * FROM eims_app_department;")
    departments = sqlite_cursor.fetchall()
    
    sqlite_cursor.execute("PRAGMA table_info(eims_app_department);")
    columns = [col[1] for col in sqlite_cursor.fetchall()]
    
    for row in departments:
        dept_data = dict(zip(columns, row))
        
        try:
            # 检查是否有部门名称
            dept_name = dept_data.get('department_name') or dept_data.get('name')
            if not dept_name:
                stats['departments']['skipped'] += 1
                continue
            
            dept_code = dept_data.get('department_code') or dept_data.get('code', '')
            
            dept, created = Department.objects.using('default').get_or_create(
                department_code=dept_code if dept_code else dept_name,
                defaults={
                    'department_name': dept_name,
                    'tenant': None,  # 稍后分配
                    'manager_name': dept_data.get('manager_name', ''),
                    'contact_phone': dept_data.get('contact_phone', ''),
                    'contact_email': dept_data.get('contact_email', ''),
                    'description': dept_data.get('description', ''),
                    'status': dept_data.get('status', 'active'),
                }
            )
            
            if created:
                stats['departments']['created'] += 1
                if stats['departments']['created'] <= 5:
                    print(f"  ✓ 创建部门: {dept.department_name}")
            else:
                stats['departments']['skipped'] += 1
                
        except Exception as e:
            error_msg = f"迁移部门失败: {e}"
            stats['errors'].append(error_msg)
    
    print(f"  完成: {stats['departments']['created']} 创建, {stats['departments']['skipped']} 跳过\n")


def migrate_employees():
    """迁移员工主数据"""
    print("[2/4] 迁移员工主数据...")
    
    sqlite_cursor.execute("SELECT * FROM eims_app_employee;")
    employees = sqlite_cursor.fetchall()
    
    sqlite_cursor.execute("PRAGMA table_info(eims_app_employee);")
    columns = [col[1] for col in sqlite_cursor.fetchall()]
    
    for row in employees:
        emp_data = dict(zip(columns, row))
        
        try:
            # 检查是否已存在
            emp_code = emp_data.get('employee_code')
            if not emp_code:
                stats['employees']['skipped'] += 1
                continue
                
            if Employee.objects.using('default').filter(employee_code=emp_code).exists():
                stats['employees']['skipped'] += 1
                continue
            
            employee = Employee(
                employee_code=emp_code,
                name=emp_data.get('name', ''),
                gender=emp_data.get('gender', 0),
                id_card=emp_data.get('id_card', ''),
                native_place=emp_data.get('native_place', ''),
                ethnic=emp_data.get('ethnic', 'han'),
                education=emp_data.get('education', 'bachelor'),
                mobile=emp_data.get('phone', '') or emp_data.get('mobile', ''),
                email=emp_data.get('email', ''),
                address=emp_data.get('address', ''),
                emergency_contact=emp_data.get('emergency_contact', ''),
                emergency_phone=emp_data.get('emergency_phone', ''),
                entry_time=emp_data.get('entry_date') or emp_data.get('entry_time'),
                work_status='在职',
                tenant=None,  # 稍后分配
                remark=emp_data.get('remark', ''),
            )
            employee.save(using='default')
            
            stats['employees']['created'] += 1
            if stats['employees']['created'] <= 5:
                print(f"  ✓ 创建员工: {employee.name} ({employee.employee_code})")
                
        except Exception as e:
            error_msg = f"迁移员工 {emp_data.get('employee_code')} 失败: {e}"
            stats['errors'].append(error_msg)
    
    print(f"  完成: {stats['employees']['created']} 创建, {stats['employees']['skipped']} 跳过\n")


def migrate_personnel():
    """迁移人员花名册"""
    print("[3/4] 迁移人员花名册...")
    
    sqlite_cursor.execute("SELECT * FROM eims_app_personnel;")
    personnel_list = sqlite_cursor.fetchall()
    
    sqlite_cursor.execute("PRAGMA table_info(eims_app_personnel);")
    columns = [col[1] for col in sqlite_cursor.fetchall()]
    
    count = 0
    for row in personnel_list:
        pers_data = dict(zip(columns, row))
        
        try:
            # 检查是否已存在
            pers_code = pers_data.get('personnel_code')
            if not pers_code:
                stats['personnel']['skipped'] += 1
                continue
                
            if Personnel.objects.using('default').filter(personnel_code=pers_code).exists():
                stats['personnel']['skipped'] += 1
                continue
            
            # 尝试关联员工
            employee = None
            emp_id = pers_data.get('employee_id')
            if emp_id:
                try:
                    employee = Employee.objects.using('default').get(id=emp_id)
                except Employee.DoesNotExist:
                    pass
            
            personnel = Personnel(
                personnel_code=pers_code,
                project_code=pers_data.get('project_code', ''),
                name=pers_data.get('name', ''),
                gender=pers_data.get('gender', 0),
                position=pers_data.get('position', ''),
                phone=pers_data.get('phone', ''),
                email=pers_data.get('email', ''),
                entry_time=pers_data.get('entry_time'),
                leave_time=pers_data.get('leave_time'),
                employee=employee,
                tenant=None,  # 稍后分配
                remark=pers_data.get('remark', ''),
            )
            personnel.save(using='default')
            
            stats['personnel']['created'] += 1
            count += 1
            if count <= 5:
                print(f"  ✓ 创建人员: {personnel.name} ({personnel.personnel_code})")
                
        except Exception as e:
            error_msg = f"迁移人员 {pers_data.get('personnel_code')} 失败: {e}"
            stats['errors'].append(error_msg)
    
    print(f"  完成: {stats['personnel']['created']} 创建, {stats['personnel']['skipped']} 跳过\n")


def verify_tenants():
    """验证公司信息"""
    print("[4/4] 验证公司信息...")
    
    tenants = Tenant.objects.using('default').all()
    print(f"\n  当前系统中的公司:")
    for tenant in tenants:
        user_count = tenant.usertenantrelation_set.count()
        print(f"    • {tenant.name} ({tenant.code}) - {user_count} 个用户")
    
    # 确保三家公司都存在
    required_companies = [
        ('dingce', '广西鼎策工程顾问有限责任公司', '鼎策'),
        ('shengchang', '广西晟昌工程科技有限责任公司', '晟昌'),
        ('jiachengda', '广西嘉诚达工程造价咨询有限公司', '嘉诚达'),
    ]
    
    for code, name, short_name in required_companies:
        tenant, created = Tenant.objects.using('default').get_or_create(
            code=code,
            defaults={
                'name': name,
                'short_name': short_name,
                'is_active': True,
            }
        )
        if created:
            print(f"  ✓ 创建公司: {name}")
        else:
            print(f"  ~ 公司已存在: {name}")
    
    print()


def print_summary():
    """打印迁移总结"""
    print(f"\n{'='*70}")
    print(f"迁移总结")
    print(f"{'='*70}")
    print(f"部门:       {stats['departments']['created']} 创建, {stats['departments']['skipped']} 跳过")
    print(f"员工主数据: {stats['employees']['created']} 创建, {stats['employees']['skipped']} 跳过")
    print(f"人员花名册: {stats['personnel']['created']} 创建, {stats['personnel']['skipped']} 跳过")
    
    if stats['errors']:
        print(f"\n错误 ({len(stats['errors'])}):")
        for error in stats['errors'][:10]:
            print(f"  - {error}")
        if len(stats['errors']) > 10:
            print(f"  ... 还有 {len(stats['errors']) - 10} 个错误")
    
    print(f"{'='*70}\n")


if __name__ == '__main__':
    try:
        verify_tenants()
        migrate_departments()
        migrate_employees()
        migrate_personnel()
        print_summary()
        
        print("\n✓ 业务数据迁移完成!")
        print("\n下一步:")
        print("1. 登录超级管理员账号查看迁移的数据")
        print("2. 在 /root/ 后台管理中可以查看所有公司和人员")
        print("3. 可以通过切换公司来管理不同公司的数据")
        
    except Exception as e:
        print(f"\n✗ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        sqlite_conn.close()
