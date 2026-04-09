"""
检查并修复租户数据问题
"""
import os
import sys
import django

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Tenant, ProjectDetail, Employee, Department, Contract, Notice
from django.contrib.sessions.models import Session

def check_tenant_data():
    """检查各租户的数据"""
    print("=" * 60)
    print("检查各租户数据")
    print("=" * 60)
    
    tenants = Tenant.objects.all()
    
    for tenant in tenants:
        print(f"\n{tenant.name} (ID={tenant.id}, Code={tenant.code}):")
        
        # 统计各类数据
        projects = ProjectDetail.objects.filter(tenant=tenant).count()
        employees = Employee.objects.filter(tenant=tenant).count()
        departments = Department.objects.filter(tenant=tenant).count()
        contracts = Contract.objects.filter(tenant=tenant).count()
        notices = Notice.objects.filter(tenant=tenant).count()
        
        print(f"  - 项目: {projects}")
        print(f"  - 员工: {employees}")
        print(f"  - 部门: {departments}")
        print(f"  - 合同: {contracts}")
        print(f"  - 通知: {notices}")
        
        # 显示项目名称
        if projects > 0:
            proj_list = ProjectDetail.objects.filter(tenant=tenant)[:3]
            print(f"  项目示例:")
            for p in proj_list:
                print(f"    - {p.project_name}")


def check_sessions():
    """检查活跃会话"""
    print("\n" + "=" * 60)
    print("检查活跃会话")
    print("=" * 60)
    
    sessions = Session.objects.filter(expire_date__gte=django.utils.timezone.now())
    print(f"活跃会话数: {sessions.count()}")
    
    for session in sessions[:5]:  # 只显示前5个
        data = session.get_decoded()
        print(f"\nSession Key: {session.session_key[:20]}...")
        print(f"  - tenant_id: {data.get('tenant_id', '未设置')}")
        print(f"  - user_id: {data.get('_auth_user_id', '未登录')}")
        
        if data.get('tenant_id'):
            try:
                tenant = Tenant.objects.get(id=data['tenant_id'])
                print(f"  - 当前公司: {tenant.name}")
            except Tenant.DoesNotExist:
                print(f"  - ⚠️ 租户ID {data['tenant_id']} 不存在!")


def fix_orphaned_data():
    """修复没有租户的数据"""
    print("\n" + "=" * 60)
    print("修复孤立数据")
    print("=" * 60)
    
    # 查找tenant为None的项目
    orphaned_projects = ProjectDetail.objects.filter(tenant=None)
    if orphaned_projects.exists():
        print(f"\n发现 {orphaned_projects.count()} 个没有租户的项目")
        default_tenant = Tenant.objects.get(code='COMPANY_A')
        count = orphaned_projects.update(tenant=default_tenant)
        print(f"✅ 已将 {count} 个项目分配到甲公司")
    else:
        print("\n✅ 没有孤立的项目数据")
    
    # 查找tenant为None的员工
    orphaned_employees = Employee.objects.filter(tenant=None)
    if orphaned_employees.exists():
        print(f"\n发现 {orphaned_employees.count()} 个没有租户的员工")
        default_tenant = Tenant.objects.get(code='COMPANY_A')
        count = orphaned_employees.update(tenant=default_tenant)
        print(f"✅ 已将 {count} 名员工分配到甲公司")
    else:
        print("\n✅ 没有孤立的员工数据")


if __name__ == '__main__':
    check_tenant_data()
    check_sessions()
    fix_orphaned_data()
    
    print("\n" + "=" * 60)
    print("检查完成！")
    print("=" * 60)
