"""
部门管理系统 - 快速部署脚本
自动完成数据库迁移和初始化
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Department, DepartmentRole, ApprovalChain
from django.contrib.auth.models import User

def create_departments():
    """创建示例部门"""
    print("=" * 60)
    print("开始创建部门数据...")
    print("=" * 60)
    
    departments = [
        # (编号，名称，类型，负责人，职能描述)
        ('DEPT001', '工程部', 'functional', '张三', '负责公司工程项目的管理和实施'),
        ('DEPT002', '技术部', 'functional', '李四', '负责技术支持和研发工作'),
        ('DEPT003', '质量部', 'functional', '王五', '负责质量管理和监督'),
        ('DEPT004', '安全部', 'functional', '赵六', '负责安全生产管理'),
        ('DEPT005', '物资部', 'functional', '孙七', '负责物资采购和管理'),
        ('DEPT006', '财务部', 'functional', '周八', '负责财务管理和会计核算'),
        ('DEPT007', '综合办', 'functional', '吴九', '负责行政和人力资源工作'),
        ('DEPT008', '市场部', 'functional', '郑十', '负责市场开拓和客户关系'),
    ]
    
    for code, name, dept_type, manager, desc in departments:
        dept, created = Department.objects.get_or_create(
            department_code=code,
            defaults={
                'department_name': name,
                'department_type': dept_type,
                'manager_name': manager,
                'description': desc,
                'responsibilities': f'负责{name}相关工作',
                'status': 'active',
                'order': int(code[-3:]),
            }
        )
        if created:
            print(f"✅ 创建部门：{dept.department_name}")
        else:
            print(f"✓  部门已存在：{dept.department_name}")
    
    print("=" * 60)


def create_approval_chains():
    """创建示例审批链"""
    print("\n开始创建审批链配置...")
    print("=" * 60)
    
    try:
        eng_dept = Department.objects.get(department_code='DEPT001')
        hr_dept = Department.objects.get(department_code='DEPT007')
        finance_dept = Department.objects.get(department_code='DEPT006')
    except Department.DoesNotExist:
        print("⚠️ 请先运行部门创建")
        return
    
    chains = [
        {
            'name': '人员分配审批流程',
            'business_type': 'personnel_allocate',
            'chain_type': 'sequential',
            'level_1_dept': eng_dept,
            'level_1_role': '部门经理',
            'level_2_dept': hr_dept,
            'level_2_role': '人事经理',
            'cross_depts': [finance_dept],
        },
        {
            'name': '人员调动审批流程',
            'business_type': 'personnel_transfer',
            'chain_type': 'sequential',
            'level_1_dept': eng_dept,
            'level_1_role': '部门经理',
            'level_2_dept': hr_dept,
            'level_2_role': '人事总监',
            'need_cross': True,
            'cross_depts': [finance_dept],
        },
    ]
    
    for chain_data in chains:
        cross_depts = chain_data.pop('cross_depts', [])
        need_cross = chain_data.pop('need_cross', False)
        
        chain = ApprovalChain.objects.create(
            name=chain_data['name'],
            business_type=chain_data['business_type'],
            chain_type=chain_data['chain_type'],
            level_1_department=chain_data['level_1_dept'],
            level_1_role=chain_data['level_1_role'],
            level_2_department=chain_data.get('level_2_dept'),
            level_2_role=chain_data.get('level_2_role', ''),
            need_cross_department=need_cross,
            is_active=True,
        )
        
        # 添加协同部门
        chain.cross_departments.set(cross_depts)
        
        print(f"✅ 创建审批链：{chain.name}")
    
    print("=" * 60)


def show_statistics():
    """显示统计信息"""
    print("\n" + "=" * 60)
    print("系统数据统计")
    print("=" * 60)
    
    dept_count = Department.objects.filter(is_deleted=False).count()
    role_count = DepartmentRole.objects.filter(is_deleted=False).count()
    chain_count = ApprovalChain.objects.filter(is_deleted=False).count()
    
    print(f"部门数量：{dept_count}")
    print(f"角色配置：{role_count}")
    print(f"审批链：{chain_count}")
    
    print("\n部门列表:")
    for dept in Department.objects.filter(status='active').order_by('order'):
        print(f"  - {dept.department_name} ({dept.manager_name or '未设置'})")
    
    print("=" * 60)


if __name__ == '__main__':
    print("\n" + "🚀" * 30)
    print("部门管理系统 - 初始化部署")
    print("🚀" * 30 + "\n")
    
    # 创建部门
    create_departments()
    
    # 创建审批链
    create_approval_chains()
    
    # 显示统计
    show_statistics()
    
    print("\n✅ 初始化完成！")
    print("\n访问地址:")
    print("  部门管理：http://localhost:8000/departments/")
    print("  角色配置：http://localhost:8000/department-roles/")
    print("  审批链：http://localhost:8000/approval-chains/")
    print("\n" + "=" * 60 + "\n")
