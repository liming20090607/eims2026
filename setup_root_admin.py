"""
Root超级管理员初始化脚本
Complete setup script for Root super admin and system configuration
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth.models import User
from django.db import connections

def create_root_superadmin():
    """创建Root超级管理员"""
    print("\n" + "="*70)
    print("创建Root超级管理员")
    print("="*70)
    
    # Check if admin user already exists
    try:
        admin = User.objects.using('root_admin').get(username='admin')
        print(f"[OK] 用户 'admin' 已存在 (ID: {admin.id})")
        if admin.is_superuser:
            print("[OK] 已是超级管理员")
        else:
            admin.is_superuser = True
            admin.is_staff = True
            admin.save(using='root_admin')
            print("[OK] 已升级为超级管理员")
    except User.DoesNotExist:
        # Create admin user
        admin = User.objects.using('root_admin').create_superuser(
            username='admin',
            email='admin@eims.com',
            password='Admin@123456'
        )
        print(f"[OK] 创建超级管理员 'admin' (ID: {admin.id})")
        print("  密码: Admin@123456")
    
    # Create root user
    try:
        root = User.objects.using('root_admin').get(username='root')
        print(f"[OK] 用户 'root' 已存在 (ID: {root.id})")
    except User.DoesNotExist:
        root = User.objects.using('root_admin').create_superuser(
            username='root',
            email='root@eims.com',
            password='Root@123456'
        )
        print(f"[OK] 创建超级管理员 'root' (ID: {root.id})")
        print("  密码: Root@123456")
    
    return admin

def init_tenants():
    """初始化租户数据"""
    print("\n" + "="*70)
    print("初始化租户数据")
    print("="*70)
    
    from eims_app.models.model_tenant import Tenant
    
    tenants_data = [
        {
            'code': 'dingce',
            'name': '广西鼎策工程顾问有限责任公司',
            'short_name': '鼎策',
            'contact_person': '管理员',
            'contact_phone': '13800000001',
            'address': '广西南宁市',
        },
        {
            'code': 'shengchang',
            'name': '广西晟昌工程科技有限责任公司',
            'short_name': '晟昌',
            'contact_person': '管理员',
            'contact_phone': '13800000002',
            'address': '广西南宁市',
        },
        {
            'code': 'jiachengda',
            'name': '广西嘉诚达工程造价咨询有限公司',
            'short_name': '嘉诚达',
            'contact_person': '管理员',
            'contact_phone': '13800000003',
            'address': '广西南宁市',
        },
    ]
    
    for tenant_data in tenants_data:
        tenant, created = Tenant.objects.using('root_admin').get_or_create(
            code=tenant_data['code'],
            defaults=tenant_data
        )
        if created:
            print(f"[OK] 创建租户: {tenant.name}")
        else:
            print(f"[OK] 租户已存在: {tenant.name} (ID: {tenant.id})")

def init_tenant_modules():
    """初始化业务模块"""
    print("\n" + "="*70)
    print("初始化业务模块")
    print("="*70)
    
    from eims_app.models.model_tenant_module import TenantModule, TenantModulePermission
    from eims_app.models.model_tenant import Tenant
    
    modules_data = [
        {'code': 'personnel', 'name': '人员花名册', 'icon': 'bi-people', 'sort_order': 1},
        {'code': 'project', 'name': '项目台账', 'icon': 'bi-clipboard-data', 'sort_order': 2},
        {'code': 'contract', 'name': '合同管理', 'icon': 'bi-file-earmark-text', 'sort_order': 3},
        {'code': 'notice', 'name': '通知公告', 'icon': 'bi-megaphone', 'sort_order': 4},
        {'code': 'file', 'name': '文件管理', 'icon': 'bi-folder', 'sort_order': 5},
        {'code': 'approval', 'name': '审批流程', 'icon': 'bi-check-circle', 'sort_order': 6},
    ]
    
    for module_data in modules_data:
        module, created = TenantModule.objects.using('root_admin').get_or_create(
            code=module_data['code'],
            defaults=module_data
        )
        if created:
            print(f"[OK] 创建模块: {module.name}")
        else:
            print(f"[OK] 模块已存在: {module.name}")
    
    # Enable all modules for all tenants
    tenants = Tenant.objects.using('root_admin').all()
    modules = TenantModule.objects.using('root_admin').all()
    
    print("\n为所有租户启用所有模块:")
    for tenant in tenants:
        for module in modules:
            perm, created = TenantModulePermission.objects.using('root_admin').get_or_create(
                tenant=tenant,
                module=module,
                defaults={'is_enabled': True}
            )
            if created:
                print(f"  [OK] {tenant.short_name} - {module.name}: 已启用")

def init_departments():
    """为每个公司初始化基础部门（使用租户前缀）"""
    print("\n" + "="*70)
    print("初始化基础部门")
    print("="*70)
    
    from eims_app.models.model_department import Department
    from eims_app.models.model_tenant import Tenant
    
    # 部门模板（不含前缀）
    departments_template = [
        {'code_suffix': 'GLB', 'department_name': '管理部', 'order': 1},
        {'code_suffix': 'JSB', 'department_name': '技术部', 'order': 2},
        {'code_suffix': 'CWB', 'department_name': '财务部', 'order': 3},
        {'code_suffix': 'RZB', 'department_name': '人事部', 'order': 4},
        {'code_suffix': 'YWB', 'department_name': '业务部', 'order': 5},
    ]
    
    # 租户前缀映射
    tenant_prefixes = {
        'dingce': 'DCE',
        'shengchang': 'SC',
        'jiachengda': 'JCD',
    }
    
    tenants = Tenant.objects.using('root_admin').all()
    
    for tenant in tenants:
        prefix = tenant_prefixes.get(tenant.code, tenant.code.upper()[:3])
        print(f"\n为 {tenant.short_name} ({tenant.code}) 创建部门:")
        
        for dept_template in departments_template:
            # 生成带前缀的部门编号
            department_code = f"{prefix}-{dept_template['code_suffix']}"
            
            try:
                dept, created = Department.objects.using('root_admin').get_or_create(
                    tenant=tenant,
                    department_code=department_code,
                    defaults={
                        'department_name': dept_template['department_name'],
                        'order': dept_template['order'],
                        'status': 'active'
                    }
                )
                if created:
                    print(f"  [OK] 创建部门: {dept.department_name} ({department_code})")
                else:
                    print(f"  [OK] 部门已存在: {dept.department_name} ({department_code})")
            except Exception as e:
                if 'Duplicate entry' in str(e):
                    print(f"  [SKIP] 跳过（部门编号已存在）: {department_code}")
                else:
                    raise

def init_sample_data():
    """为每个公司加载示例数据（员工、项目、合同等）"""
    print("\n" + "="*70)
    print("加载示例数据")
    print("="*70)
    
    from eims_app.models.model_tenant import Tenant
    from eims_app.models.model_employee import Employee
    from eims_app.models.model_project_detail import ProjectDetail
    from eims_app.models.model_contract import Contract
    from eims_app.models.model_department import Department
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    tenants = Tenant.objects.using('root_admin').all()
    
    # 有效的数据库连接（排除开发者等特殊租户）
    valid_databases = ['dingce', 'shengchang', 'jiachengda']
    
    for tenant in tenants:
        # 跳过没有对应数据库的租户
        if tenant.code not in valid_databases:
            print(f"\n[SKIP] 跳过 {tenant.short_name} ({tenant.code}) - 无对应数据库")
            continue
        
        print(f"\n为 {tenant.short_name} ({tenant.code}) 加载示例数据:")
        
        # 1. 创建示例员工
        # 使用与部门相同的前缀映射
        prefix_map = {
            'dingce': 'DCE',
            'shengchang': 'SC',
            'jiachengda': 'JCD',
        }
        prefix = prefix_map.get(tenant.code, tenant.code.upper()[:3])
        
        employees_data = [
            {'employee_code': f'{prefix}001', 'name': '张三', 'gender': 1, 'id_card': '450100199001010001', 'mobile': '13800001001', 'department_code': f'{prefix}-GLB'},
            {'employee_code': f'{prefix}002', 'name': '李四', 'gender': 1, 'id_card': '450100199001010002', 'mobile': '13800001002', 'department_code': f'{prefix}-JSB'},
            {'employee_code': f'{prefix}003', 'name': '王五', 'gender': 2, 'id_card': '450100199001010003', 'mobile': '13800001003', 'department_code': f'{prefix}-CWB'},
        ]
        
        for emp_data in employees_data:
            try:
                # 查找对应的部门
                dept = Department.objects.using('root_admin').filter(
                    tenant=tenant,
                    department_code=emp_data['department_code']
                ).first()
                
                if dept:
                    emp, created = Employee.objects.using(tenant.code).get_or_create(
                        employee_code=emp_data['employee_code'],
                        defaults={
                            'name': emp_data['name'],
                            'gender': emp_data['gender'],
                            'id_card': emp_data['id_card'],
                            'mobile': emp_data['mobile']
                        }
                    )
                    if created:
                        print(f"  [OK] 创建员工: {emp.name} ({emp.employee_code})")
                    else:
                        print(f"  [SKIP] 员工已存在: {emp.name}")
                else:
                    print(f"  [ERROR] 找不到部门: {emp_data['department_code']}")
            except Exception as e:
                print(f"  [ERROR] 创建员工失败: {emp_data['name']} - {str(e)}")
        
        # 2. 创建示例项目
        projects_data = [
            {'project_code': f'{prefix}P001', 'project_name': f'{tenant.short_name}监理项目A', 'contract_category': 'supervision', 'project_status': 'ongoing', 'contract_amount': 500000.00},
            {'project_code': f'{prefix}P002', 'project_name': f'{tenant.short_name}监理项目B', 'contract_category': 'supervision', 'project_status': 'planning', 'contract_amount': 300000.00},
        ]
        
        for proj_data in projects_data:
            try:
                proj, created = ProjectDetail.objects.using(tenant.code).get_or_create(
                    project_code=proj_data['project_code'],
                    defaults={
                        'project_name': proj_data['project_name'],
                        'contract_category': proj_data['contract_category'],
                        'project_status': proj_data['project_status'],
                        'contract_amount': proj_data['contract_amount'],
                        'contract_status': 'unsigned'
                    }
                )
                if created:
                    print(f"  [OK] 创建项目: {proj.project_name} ({proj.project_code})")
                else:
                    print(f"  [SKIP] 项目已存在: {proj.project_name}")
            except Exception as e:
                print(f"  [ERROR] 创建项目失败: {proj_data['project_name']} - {str(e)}")
        
        # 3. 创建示例合同
        contracts_data = [
            {'contract_code': f'{prefix}C001', 'contract_name': f'{tenant.short_name}监理合同A', 'contract_type': 'supervision', 'contract_amount': 500000.00},
            {'contract_code': f'{prefix}C002', 'contract_name': f'{tenant.short_name}咨询合同B', 'contract_type': 'consulting', 'contract_amount': 300000.00},
        ]
        
        for cont_data in contracts_data:
            try:
                cont, created = Contract.objects.using(tenant.code).get_or_create(
                    contract_code=cont_data['contract_code'],
                    defaults={
                        'contract_name': cont_data['contract_name'],
                        'contract_type': cont_data['contract_type'],
                        'contract_amount': cont_data['contract_amount'],
                        'status': 'draft'
                    }
                )
                if created:
                    print(f"  [OK] 创建合同: {cont.contract_name} ({cont.contract_code})")
                else:
                    print(f"  [SKIP] 合同已存在: {cont.contract_name}")
            except Exception as e:
                print(f"  [ERROR] 创建合同失败: {cont_data['contract_name']} - {str(e)}")

def show_summary():
    """显示配置总结"""
    print("\n" + "="*70)
    print("配置完成总结")
    print("="*70)
    
    print("\n[INFO] Root超级管理员账号:")
    print("  用户名: admin")
    print("  密码: Admin@123456")
    print("  权限: 超级管理员 (可访问所有系统)")
    
    print("\n  用户名: root")
    print("  密码: Root@123456")
    print("  权限: 超级管理员 (可访问所有系统)")
    
    print("\n[INFO] 系统访问地址:")
    print("  智能路由入口: http://127.0.0.1:8000/")
    print("  鼎策系统: http://127.0.0.1:8000/dingce/")
    print("  晟昌系统: http://127.0.0.1:8000/shengchang/")
    print("  嘉诚达系统: http://127.0.0.1:8000/jiachengda/")
    print("  Root后台: http://127.0.0.1:8000/root/")
    
    print("\n[INFO] 数据库架构:")
    print("  eims_root → 用户认证 + 租户管理 + 模块配置")
    print("  eims_dingce → 鼎策公司业务数据")
    print("  eims_shengchang → 晟昌公司业务数据")
    print("  eims_jiachengda → 嘉诚达公司业务数据")
    
    print("\n[WARNING] 安全建议:")
    print("  1. 首次登录后立即修改默认密码")
    print("  2. 生产环境使用HTTPS")
    print("  3. 定期备份数据库")
    
    print("\n" + "="*70)

def main():
    print("="*70)
    print("Root超级管理员及系统配置初始化")
    print("="*70)
    
    try:
        # Step 1: Create Root super admin
        admin = create_root_superadmin()
        
        # Step 2: Initialize tenants
        init_tenants()
        
        # Step 3: Initialize modules
        init_tenant_modules()
        
        # Step 4: Initialize departments
        init_departments()
        
        # Step 5: Load sample data
        init_sample_data()
        
        # Step 6: Show summary
        show_summary()
        
        print("\n[SUCCESS] 所有配置完成!")
        return 0
        
    except Exception as e:
        print(f"\n❌ 配置失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
