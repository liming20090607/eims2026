"""
简化版：更新租户公司名称并复制测试数据
"""
import os
import sys
import django

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Tenant, Department, Employee, Personnel, ProjectDetail, Contract, Notice
from django.utils import timezone
from datetime import datetime, timedelta
import random

def update_tenant_names():
    """更新租户公司的全称"""
    print("=" * 60)
    print("步骤1: 更新租户公司名称")
    print("=" * 60)
    
    updates = [
        ('COMPANY_A', '广西鼎策工程顾问有限责任公司'),
        ('COMPANY_B', '广西晟昌工程科技有限责任公司'),
        ('COMPANY_C', '广西嘉诚达工程造价咨询有限公司'),
    ]
    
    for code, name in updates:
        try:
            tenant = Tenant.objects.get(code=code)
            tenant.name = name
            tenant.full_name = name
            tenant.save()
            print(f"✅ {code}: {name}")
        except Tenant.DoesNotExist:
            print(f"⚠️  {code} 不存在")
    
    print()


def copy_departments_to_b():
    """复制部门到乙公司"""
    print("=" * 60)
    print("步骤2: 复制部门到乙公司")
    print("=" * 60)
    
    try:
        tenant_a = Tenant.objects.get(code='COMPANY_A')
        tenant_b = Tenant.objects.get(code='COMPANY_B')
    except Tenant.DoesNotExist:
        print("❌ 租户不存在")
        return
    
    departments_a = Department.objects.filter(tenant=tenant_a, is_deleted=False)
    count = 0
    
    for dept in departments_a:
        # 检查是否已存在
        if Department.objects.filter(tenant=tenant_b, department_code=dept.department_code).exists():
            print(f"  ⏭️  跳过已存在: {dept.department_name}")
            continue
        
        try:
            new_dept = Department.objects.create(
                tenant=tenant_b,
                department_code=dept.department_code,
                department_name=dept.department_name,
                department_type=dept.department_type,
                manager_name=dept.manager_name or '',
                contact_phone=dept.contact_phone or '',
                contact_email=dept.contact_email or '',
                description=dept.description or '',
                responsibilities=dept.responsibilities or '',
                status=dept.status,
                established_date=dept.established_date,
                order=dept.order,
            )
            count += 1
            print(f"  ✅ {dept.department_name}")
        except Exception as e:
            print(f"  ❌ {dept.department_name}: {str(e)[:50]}")
    
    print(f"\n共复制 {count} 个部门\n")


def copy_employees_to_b():
    """复制员工到乙公司"""
    print("=" * 60)
    print("步骤3: 复制员工到乙公司")
    print("=" * 60)
    
    try:
        tenant_a = Tenant.objects.get(code='COMPANY_A')
        tenant_b = Tenant.objects.get(code='COMPANY_B')
    except Tenant.DoesNotExist:
        print("❌ 租户不存在")
        return
    
    employees_a = Employee.objects.filter(tenant=tenant_a, is_deleted=False)
    count = 0
    
    for emp in employees_a:
        # 检查是否已存在
        if Employee.objects.filter(tenant=tenant_b, employee_code=emp.employee_code).exists():
            print(f"  ⏭️  跳过已存在: {emp.name}")
            continue
        
        try:
            new_emp = Employee.objects.create(
                tenant=tenant_b,
                employee_code=emp.employee_code,
                name=emp.name,
                gender=emp.gender,
                id_card=emp.id_card or '',
                native_place=emp.native_place or '',
                ethnic=emp.ethnic or '',
                education=emp.education or '',
                admin_position=emp.admin_position or '',
                tech_position=emp.tech_position or '',
                professional_qualification=emp.professional_qualification or '',
                professional_title=emp.professional_title or '',
                job_qualification=emp.job_qualification or '',
                mobile=emp.mobile or '',
                home_phone=emp.home_phone or '',
                address=emp.address or '',
                emergency_contact=emp.emergency_contact or '',
                emergency_phone=emp.emergency_phone or '',
                wechat=emp.wechat or '',
                email=emp.email or '',
                entry_time=emp.entry_time,
                leave_time=emp.leave_time,
                remark=emp.remark or '',
            )
            count += 1
            print(f"  ✅ {emp.name}")
        except Exception as e:
            print(f"  ❌ {emp.name}: {str(e)[:50]}")
    
    print(f"\n共复制 {count} 名员工\n")


def create_test_data_for_c():
    """为丙公司创建测试数据"""
    print("=" * 60)
    print("步骤4: 为丙公司创建测试数据")
    print("=" * 60)
    
    try:
        tenant_c = Tenant.objects.get(code='COMPANY_C')
    except Tenant.DoesNotExist:
        print("❌ 丙公司不存在")
        return
    
    # 创建测试部门
    print("\n📋 创建测试部门...")
    test_depts = [
        ('DEPT_C001', '造价咨询部', 'functional'),
        ('DEPT_C002', '工程管理部', 'functional'),
        ('DEPT_C003', '财务部', 'functional'),
    ]
    
    for code, name, dtype in test_depts:
        dept, created = Department.objects.get_or_create(
            tenant=tenant_c,
            department_code=code,
            defaults={
                'department_name': name,
                'department_type': dtype,
                'status': 'active',
            }
        )
        if created:
            print(f"  ✅ {name}")
    
    # 创建测试员工
    print("\n👤 创建测试员工...")
    test_emps = [
        ('EMP_C001', '李明', 0, '13800138001', '造价工程师'),
        ('EMP_C002', '王芳', 1, '13800138002', '项目经理'),
        ('EMP_C003', '张伟', 0, '13800138003', '财务主管'),
    ]
    
    for code, name, gender, mobile, position in test_emps:
        emp, created = Employee.objects.get_or_create(
            tenant=tenant_c,
            employee_code=code,
            defaults={
                'name': name,
                'gender': gender,
                'mobile': mobile,
                'admin_position': position,
                'education': 'bachelor',
                'entry_time': datetime.now().date() - timedelta(days=random.randint(30, 365)),
            }
        )
        if created:
            print(f"  ✅ {name}")
    
    # 创建测试项目
    print("\n📁 创建测试项目...")
    test_projects = [
        ('PRJ_C001', '南宁某小区造价咨询项目', '南宁某房地产公司', 500000),
        ('PRJ_C002', '柳州商业综合体造价咨询', '柳州某商业集团', 800000),
    ]
    
    for code, name, party_a, amount in test_projects:
        proj, created = ProjectDetail.objects.get_or_create(
            tenant=tenant_c,
            project_code=code,
            defaults={
                'project_name': name,
                'party_a': party_a,
                'contract_amount': amount,
                'project_address': '广西',
                'status': 'ongoing',
            }
        )
        if created:
            print(f"  ✅ {name}")
    
    # 创建测试合同
    print("\n📄 创建测试合同...")
    test_contracts = [
        ('CON_C001', '南宁小区造价咨询合同', '南宁某房地产公司', 500000),
    ]
    
    for code, name, party_a, amount in test_contracts:
        contract, created = Contract.objects.get_or_create(
            tenant=tenant_c,
            contract_code=code,
            defaults={
                'contract_name': name,
                'party_a': party_a,
                'amount': amount,
                'sign_date': datetime.now().date() - timedelta(days=30),
                'status': 'active',
            }
        )
        if created:
            print(f"  ✅ {name}")
    
    # 创建测试通知
    print("\n📢 创建测试通知...")
    test_notices = [
        '关于2026年春节放假的通知',
        '公司年度总结会议通知',
    ]
    
    for title in test_notices:
        notice, created = Notice.objects.get_or_create(
            tenant=tenant_c,
            notice_title=title,
            defaults={
                'notice_type': 'notice',
                'notice_status': 'published',
                'notice_content': f'这是{title}的测试内容',
                'publish_person': '系统管理员',
                'upload_person': '系统管理员',
            }
        )
        if created:
            print(f"  ✅ {title}")
    
    print("\n")


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("开始更新租户数据")
    print("=" * 60 + "\n")
    
    # 1. 更新公司名称
    update_tenant_names()
    
    # 2. 复制部门到乙公司
    copy_departments_to_b()
    
    # 3. 复制员工到乙公司
    copy_employees_to_b()
    
    # 4. 为丙公司创建测试数据
    create_test_data_for_c()
    
    print("=" * 60)
    print("🎉 所有操作完成！")
    print("=" * 60)
    print("\n现在您可以登录系统测试：")
    print("1. 甲公司：广西鼎策工程顾问有限责任公司（原有数据）")
    print("2. 乙公司：广西晟昌工程科技有限责任公司（复制的数据）")
    print("3. 丙公司：广西嘉诚达工程造价咨询有限公司（测试数据）")
    print("=" * 60 + "\n")
