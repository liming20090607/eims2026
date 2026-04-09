"""
更新租户公司名称并复制/创建测试数据
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

from eims_app.models import (
    Tenant, ProjectDetail, Personnel, Employee, Contract,
    Department, Notice, FileManage, PersonnelCertificate,
    PersonnelAllocation, ProjectDynamic, OutputPayment,
    ContractApproval, ArchiveApproval, SealApproval
)
from django.utils import timezone
from datetime import datetime, timedelta
import random

def update_tenant_names():
    """更新租户公司的全称"""
    print("=" * 60)
    print("更新租户公司名称")
    print("=" * 60)
    
    # 更新甲公司
    try:
        tenant_a = Tenant.objects.get(code='COMPANY_A')
        tenant_a.name = '广西鼎策工程顾问有限责任公司'
        tenant_a.full_name = '广西鼎策工程顾问有限责任公司'
        tenant_a.save()
        print("✅ 甲公司名称已更新：广西鼎策工程顾问有限责任公司")
    except Tenant.DoesNotExist:
        print("⚠️  甲公司不存在，请先创建")
    
    # 更新乙公司
    try:
        tenant_b = Tenant.objects.get(code='COMPANY_B')
        tenant_b.name = '广西晟昌工程科技有限责任公司'
        tenant_b.full_name = '广西晟昌工程科技有限责任公司'
        tenant_b.save()
        print("✅ 乙公司名称已更新：广西晟昌工程科技有限责任公司")
    except Tenant.DoesNotExist:
        print("⚠️  乙公司不存在，请先创建")
    
    # 更新丙公司
    try:
        tenant_c = Tenant.objects.get(code='COMPANY_C')
        tenant_c.name = '广西嘉诚达工程造价咨询有限公司'
        tenant_c.full_name = '广西嘉诚达工程造价咨询有限公司'
        tenant_c.save()
        print("✅ 丙公司名称已更新：广西嘉诚达工程造价咨询有限公司")
    except Tenant.DoesNotExist:
        print("⚠️  丙公司不存在，请先创建")
    
    print()


def duplicate_data_to_tenant_b():
    """将甲公司的数据复制到乙公司（简化版）"""
    print("=" * 60)
    print("将甲公司数据复制到乙公司")
    print("=" * 60)
    
    try:
        tenant_a = Tenant.objects.get(code='COMPANY_A')
        tenant_b = Tenant.objects.get(code='COMPANY_B')
    except Tenant.DoesNotExist:
        print("❌ 租户不存在，无法复制数据")
        return
    
    # 1. 复制部门
    print("\n📋 复制部门数据...")
    departments_a = Department.objects.filter(tenant=tenant_a, is_deleted=False)
    dept_map = {}  # 旧ID -> 新ID映射
    
    for dept in departments_a:
        try:
            new_dept = Department(
                tenant=tenant_b,
                department_code=dept.department_code + '_B',  # 避免唯一性冲突
                department_name=dept.department_name,
                department_type=dept.department_type,
                parent_department=None,  # 暂时不复制层级关系
                manager_name=dept.manager_name,
                contact_phone=dept.contact_phone,
                contact_email=dept.contact_email,
                description=dept.description,
                responsibilities=dept.responsibilities,
                status=dept.status,
                established_date=dept.established_date,
                order=dept.order,
                operator=dept.operator,
                is_deleted=dept.is_deleted,
            )
            new_dept.save()
            dept_map[dept.id] = new_dept.id
            print(f"  - 部门: {dept.department_name}")
        except Exception as e:
            print(f"  ⚠️ 跳过部门 {dept.department_name}: {str(e)}")
    
    # 2. 复制员工
    print("\n👤 复制员工数据...")
    employees_a = Employee.objects.filter(tenant=tenant_a, is_deleted=False)
    employee_map = {}
    
    for emp in employees_a:
        new_emp = Employee(
            tenant=tenant_b,
            employee_code=emp.employee_code,
            name=emp.name,
            gender=emp.gender,
            id_card=emp.id_card,
            native_place=emp.native_place,
            ethnic=emp.ethnic,
            education=emp.education,
            admin_position=emp.admin_position,
            tech_position=emp.tech_position,
            professional_qualification=emp.professional_qualification,
            professional_title=emp.professional_title,
            job_qualification=emp.job_qualification,
            mobile=emp.mobile,
            home_phone=emp.home_phone,
            address=emp.address,
            emergency_contact=emp.emergency_contact,
            emergency_phone=emp.emergency_phone,
            wechat=emp.wechat,
            email=emp.email,
            entry_time=emp.entry_time,
            leave_time=emp.leave_time,
            remark=emp.remark,
            operator=emp.operator,
            is_deleted=emp.is_deleted,
        )
        new_emp.save()
        employee_map[emp.id] = new_emp.id
        print(f"  - 员工: {emp.name}")
    
    # 3. 复制人员
    print("\n👥 复制人员数据...")
    personnel_a = Personnel.objects.filter(tenant=tenant_a, is_deleted=False)
    personnel_map = {}
    
    for p in personnel_a:
        new_p = Personnel(
            tenant=tenant_b,
            personnel_code=p.personnel_code,
            name=p.name,
            gender=p.gender,
            department=p.department,
            position=p.position,
            phone=p.phone,
            email=p.email,
            entry_time=p.entry_time,
            leave_time=p.leave_time,
            employee_id=employee_map.get(p.employee_id) if p.employee_id else None,
            project_code=p.project_code,
            project_code2=p.project_code2,
            project_code3=p.project_code3,
            project_code4=p.project_code4,
            project_code5=p.project_code5,
            remark=p.remark,
            operator=p.operator,
            is_deleted=p.is_deleted,
        )
        new_p.save()
        personnel_map[p.id] = new_p.id
        print(f"  - 人员: {p.name}")
    
    # 4. 复制项目台账
    print("\n📁 复制项目台账数据...")
    projects_a = ProjectDetail.objects.filter(tenant=tenant_a, is_deleted=False)
    
    for proj in projects_a:
        new_proj = ProjectDetail(
            tenant=tenant_b,
            project_code=proj.project_code,
            project_name=proj.project_name,
            # 复制其他字段...
            party_a=proj.party_a,
            party_b=proj.party_b,
            contract_amount=proj.contract_amount,
            project_address=proj.project_address,
            start_date=proj.start_date,
            end_date=proj.end_date,
            status=proj.status,
            remark=proj.remark,
            operator=proj.operator,
            is_deleted=proj.is_deleted,
        )
        new_proj.save()
        print(f"  - 项目: {proj.project_name}")
    
    # 5. 复制合同
    print("\n📄 复制合同数据...")
    contracts_a = Contract.objects.filter(tenant=tenant_a, is_deleted=False)
    
    for contract in contracts_a:
        new_contract = Contract(
            tenant=tenant_b,
            contract_code=contract.contract_code,
            contract_name=contract.contract_name,
            party_a=contract.party_a,
            party_b=contract.party_b,
            amount=contract.amount,
            sign_date=contract.sign_date,
            status=contract.status,
            remark=contract.remark,
            operator=contract.operator,
            is_deleted=contract.is_deleted,
        )
        new_contract.save()
        print(f"  - 合同: {contract.contract_name}")
    
    # 6. 复制其他数据（通知公告、文件等）
    print("\n📢 复制通知公告...")
    notices_a = Notice.objects.filter(tenant=tenant_a, is_deleted=False)
    for notice in notices_a:
        new_notice = Notice(
            tenant=tenant_b,
            notice_title=notice.notice_title,
            notice_type=notice.notice_type,
            notice_status=notice.notice_status,
            keywords=notice.keywords,
            notice_content=notice.notice_content,
            publish_person=notice.publish_person,
            upload_person=notice.upload_person,
            is_deleted=notice.is_deleted,
        )
        new_notice.save()
    
    print(f"✅ 成功复制 {notices_a.count()} 条通知公告")
    
    # 7. 复制人员证书
    print("\n📜 复制人员证书...")
    certs_a = PersonnelCertificate.objects.filter(tenant=tenant_a, is_deleted=False)
    for cert in certs_a:
        new_cert = PersonnelCertificate(
            tenant=tenant_b,
            personnel_code=cert.personnel_code,
            certificate_type=cert.certificate_type,
            certificate_name=cert.certificate_name,
            certificate_code=cert.certificate_code,
            issuing_authority=cert.issuing_authority,
            issue_date=cert.issue_date,
            expiry_date=cert.expiry_date,
            operator=cert.operator,
            is_deleted=cert.is_deleted,
        )
        new_cert.save()
    
    print(f"✅ 成功复制 {certs_a.count()} 条人员证书")
    
    print("\n" + "=" * 60)
    print("✅ 乙公司数据复制完成！")
    print("=" * 60)
    print()


def create_test_data_for_tenant_c():
    """为丙公司创建测试数据"""
    print("=" * 60)
    print("为丙公司创建测试数据")
    print("=" * 60)
    
    try:
        tenant_c = Tenant.objects.get(code='COMPANY_C')
    except Tenant.DoesNotExist:
        print("❌ 丙公司不存在，请先创建")
        return
    
    # 1. 创建测试部门
    print("\n🏢 创建测试部门...")
    test_departments = [
        {'code': 'DEPT_C001', 'name': '造价咨询部', 'type': '业务部门'},
        {'code': 'DEPT_C002', 'name': '工程管理部', 'type': '业务部门'},
        {'code': 'DEPT_C003', 'name': '财务部', 'type': '职能部门'},
        {'code': 'DEPT_C004', 'name': '综合办公室', 'type': '职能部门'},
    ]
    
    for dept_data in test_departments:
        dept, created = Department.objects.get_or_create(
            tenant=tenant_c,
            department_code=dept_data['code'],
            defaults={
                'department_name': dept_data['name'],
                'department_type': dept_data['type'],
                'status': 'active',
                'operator': 'system',
            }
        )
        if created:
            print(f"  - 创建部门: {dept_data['name']}")
    
    # 2. 创建测试员工
    print("\n👤 创建测试员工...")
    test_employees = [
        {'code': 'EMP_C001', 'name': '李明', 'gender': 0, 'mobile': '13800138001', 'position': '造价工程师'},
        {'code': 'EMP_C002', 'name': '王芳', 'gender': 1, 'mobile': '13800138002', 'position': '项目经理'},
        {'code': 'EMP_C003', 'name': '张伟', 'gender': 0, 'mobile': '13800138003', 'position': '财务主管'},
        {'code': 'EMP_C004', 'name': '刘洋', 'gender': 0, 'mobile': '13800138004', 'position': '技术员'},
        {'code': 'EMP_C005', 'name': '陈静', 'gender': 1, 'mobile': '13800138005', 'position': '行政助理'},
    ]
    
    for emp_data in test_employees:
        emp, created = Employee.objects.get_or_create(
            tenant=tenant_c,
            employee_code=emp_data['code'],
            defaults={
                'name': emp_data['name'],
                'gender': emp_data['gender'],
                'mobile': emp_data['mobile'],
                'admin_position': emp_data['position'],
                'education': 'bachelor',
                'entry_time': datetime.now().date() - timedelta(days=random.randint(30, 365)),
                'operator': 'system',
            }
        )
        if created:
            print(f"  - 创建员工: {emp_data['name']}")
    
    # 3. 创建测试项目
    print("\n📁 创建测试项目...")
    test_projects = [
        {'code': 'PRJ_C001', 'name': '南宁某小区造价咨询项目', 'party_a': '南宁某房地产公司', 'amount': 500000},
        {'code': 'PRJ_C002', 'name': '柳州某商业综合体造价咨询', 'party_a': '柳州某商业集团', 'amount': 800000},
        {'code': 'PRJ_C003', 'name': '桂林某学校建设项目', 'party_a': '桂林市教育局', 'amount': 1200000},
    ]
    
    for proj_data in test_projects:
        proj, created = ProjectDetail.objects.get_or_create(
            tenant=tenant_c,
            project_code=proj_data['code'],
            defaults={
                'project_name': proj_data['name'],
                'party_a': proj_data['party_a'],
                'contract_amount': proj_data['amount'],
                'project_address': '广西',
                'status': 'ongoing',
                'operator': 'system',
            }
        )
        if created:
            print(f"  - 创建项目: {proj_data['name']}")
    
    # 4. 创建测试合同
    print("\n📄 创建测试合同...")
    test_contracts = [
        {'code': 'CON_C001', 'name': '南宁小区造价咨询合同', 'party_a': '南宁某房地产公司', 'amount': 500000},
        {'code': 'CON_C002', 'name': '柳州商业综合体造价合同', 'party_a': '柳州某商业集团', 'amount': 800000},
    ]
    
    for contract_data in test_contracts:
        contract, created = Contract.objects.get_or_create(
            tenant=tenant_c,
            contract_code=contract_data['code'],
            defaults={
                'contract_name': contract_data['name'],
                'party_a': contract_data['party_a'],
                'amount': contract_data['amount'],
                'sign_date': datetime.now().date() - timedelta(days=random.randint(10, 60)),
                'status': 'active',
                'operator': 'system',
            }
        )
        if created:
            print(f"  - 创建合同: {contract_data['name']}")
    
    # 5. 创建测试通知公告
    print("\n📢 创建测试通知公告...")
    test_notices = [
        {'title': '关于2026年春节放假的通知', 'type': 'notice', 'status': 'published'},
        {'title': '公司年度总结会议通知', 'type': 'notice', 'status': 'published'},
        {'title': '安全生产培训通知', 'type': 'notice', 'status': 'draft'},
    ]
    
    for notice_data in test_notices:
        notice, created = Notice.objects.get_or_create(
            tenant=tenant_c,
            notice_title=notice_data['title'],
            defaults={
                'notice_type': notice_data['type'],
                'notice_status': notice_data['status'],
                'notice_content': f'这是{notice_data["title"]}的测试内容',
                'publish_person': '系统管理员',
                'upload_person': '系统管理员',
            }
        )
        if created:
            print(f"  - 创建通知: {notice_data['title']}")
    
    # 6. 创建测试人员证书
    print("\n📜 创建测试人员证书...")
    test_certs = [
        {'personnel_code': 'EMP_C001', 'name': '一级造价工程师', 'code': 'CERT_C001'},
        {'personnel_code': 'EMP_C002', 'name': '一级建造师', 'code': 'CERT_C002'},
        {'personnel_code': 'EMP_C001', 'name': '咨询工程师', 'code': 'CERT_C003'},
    ]
    
    for cert_data in test_certs:
        cert, created = PersonnelCertificate.objects.get_or_create(
            tenant=tenant_c,
            certificate_code=cert_data['code'],
            defaults={
                'personnel_code': cert_data['personnel_code'],
                'certificate_name': cert_data['name'],
                'certificate_type': 'professional',
                'issuing_authority': '住房和城乡建设部',
                'issue_date': datetime.now().date() - timedelta(days=365),
                'expiry_date': datetime.now().date() + timedelta(days=365*4),
                'operator': 'system',
            }
        )
        if created:
            print(f"  - 创建证书: {cert_data['name']}")
    
    print("\n" + "=" * 60)
    print("✅ 丙公司测试数据创建完成！")
    print("=" * 60)
    print()


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("开始更新租户数据")
    print("=" * 60 + "\n")
    
    # 1. 更新公司名称
    update_tenant_names()
    
    # 2. 复制甲公司数据到乙公司
    duplicate_data_to_tenant_b()
    
    # 3. 为丙公司创建测试数据
    create_test_data_for_tenant_c()
    
    print("\n" + "=" * 60)
    print("🎉 所有操作完成！")
    print("=" * 60)
    print("\n现在您可以：")
    print("1. 登录系统查看甲公司数据")
    print("2. 切换到乙公司查看复制的数据")
    print("3. 切换到丙公司查看测试数据")
    print("=" * 60 + "\n")
