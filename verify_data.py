"""
验证所有基础数据是否已加载
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_tenant import Tenant
from eims_app.models.model_department import Department
from eims_app.models.model_employee import Employee
from eims_app.models.model_project_detail import ProjectDetail
from eims_app.models.model_contract import Contract

def verify_data():
    print("="*70)
    print("验证基础数据")
    print("="*70)
    
    tenants = ['dingce', 'shengchang', 'jiachengda']
    
    for tenant_code in tenants:
        print(f"\n{tenant_code.upper()} 数据库:")
        
        # 1. 部门（在root_admin中）
        tenant = Tenant.objects.using('root_admin').filter(code=tenant_code).first()
        if tenant:
            depts = Department.objects.using('root_admin').filter(tenant=tenant).count()
            print(f"  部门数量: {depts}")
        
        # 2. 员工
        emp_count = Employee.objects.using(tenant_code).count()
        print(f"  员工数量: {emp_count}")
        
        # 3. 项目
        proj_count = ProjectDetail.objects.using(tenant_code).count()
        print(f"  项目数量: {proj_count}")
        
        # 4. 合同
        cont_count = Contract.objects.using(tenant_code).count()
        print(f"  合同数量: {cont_count}")
        
        # 显示示例数据
        if emp_count > 0:
            emps = Employee.objects.using(tenant_code).all()[:3]
            print(f"    示例员工: {', '.join([e.name for e in emps])}")
        
        if proj_count > 0:
            projs = ProjectDetail.objects.using(tenant_code).all()[:2]
            print(f"    示例项目: {', '.join([p.project_name for p in projs])}")
        
        if cont_count > 0:
            conts = Contract.objects.using(tenant_code).all()[:2]
            print(f"    示例合同: {', '.join([c.contract_name for c in conts])}")
    
    print("\n" + "="*70)

if __name__ == '__main__':
    verify_data()
