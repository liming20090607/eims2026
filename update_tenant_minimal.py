"""
极简版：仅更新公司名称和创建丙公司测试数据
"""
import os
import sys
import django

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Tenant, Department, Employee, ProjectDetail, Contract, Notice
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


def create_test_data_for_c():
    """为丙公司创建测试数据"""
    print("=" * 60)
    print("步骤2: 为丙公司创建测试数据")
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
        ('PRJ_C001', '南宁某小区造价咨询项目', 500000),
        ('PRJ_C002', '柳州商业综合体造价咨询', 800000),
    ]
    
    for code, name, amount in test_projects:
        proj, created = ProjectDetail.objects.get_or_create(
            tenant=tenant_c,
            project_code=code,
            defaults={
                'project_name': name,
                'contract_code': 'CON_' + code.replace('PRJ_', ''),
                'contract_amount': amount,
                'contract_category': 'cost_consulting',
            }
        )
        if created:
            print(f"  ✅ {name}")
    
    # 创建测试合同
    print("\n📄 创建测试合同...")
    test_contracts = [
        ('CON_C001', '南宁小区造价咨询合同', 500000),
    ]
    
    for code, name, amount in test_contracts:
        contract, created = Contract.objects.get_or_create(
            tenant=tenant_c,
            contract_code=code,
            defaults={
                'contract_name': name,
                'contract_amount': amount,
                'signing_time': datetime.now().date() - timedelta(days=30),
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
                'notice_type': '通知',
                'notice_status': '已发布',
                'notice_content': f'这是{title}的测试内容',
                'publish_person': '系统管理员',
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
    
    # 2. 为丙公司创建测试数据
    create_test_data_for_c()
    
    print("=" * 60)
    print("🎉 所有操作完成！")
    print("=" * 60)
    print("\n现在您可以登录系统测试：")
    print("1. 甲公司：广西鼎策工程顾问有限责任公司（原有数据）")
    print("2. 乙公司：广西晟昌工程科技有限责任公司（需要手动添加数据）")
    print("3. 丙公司：广西嘉诚达工程造价咨询有限公司（测试数据）")
    print("=" * 60 + "\n")
