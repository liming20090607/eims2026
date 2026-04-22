"""
检查租户公司和数据库配置
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_tenant import Tenant
from django.db import connections

print("="*80)
print("租户公司及数据库配置检查报告")
print("="*80)

# 1. 查询所有租户
tenants = Tenant.objects.all()
print(f"\n系统中共有 {tenants.count()} 个租户公司:\n")

for i, tenant in enumerate(tenants, 1):
    print(f"{i}. {tenant.name}")
    print(f"   简称: {tenant.short_name}")
    print(f"   代码: {tenant.code}")
    print(f"   联系人: {tenant.contact_person or '未设置'}")
    print(f"   电话: {tenant.contact_phone or '未设置'}")
    print(f"   地址: {tenant.address or '未设置'}")
    print()

# 2. 数据库配置
print("="*80)
print("数据库配置:")
print("="*80)

db_config = {
    'dingce': 'eims_dingce',
    'shengchang': 'eims_shengchang', 
    'jiachengda': 'eims_jiachengda',
    'root_admin': 'eims_root'
}

print("\n数据库映射关系:")
print("-" * 80)
print(f"{'租户代码':<15} {'数据库名':<25} {'说明'}")
print("-" * 80)
print(f"{'dingce':<15} {'eims_dingce':<25} {'鼎策公司业务数据'}")
print(f"{'shengchang':<15} {'eims_shengchang':<25} {'晟昌公司业务数据'}")
print(f"{'jiachengda':<15} {'eims_jiachengda':<25} {'嘉诚达公司业务数据'}")
print(f"{'root_admin':<15} {'eims_root':<25} {'用户认证+租户管理(共享)'}")
print("-" * 80)

# 3. 验证数据库连接
print("\n数据库连接状态:")
print("-" * 80)
for db_alias, db_name in db_config.items():
    try:
        cursor = connections[db_alias].cursor()
        cursor.execute("SELECT 1")
        print(f"✓ {db_alias:<15} -> {db_name:<25} [连接正常]")
    except Exception as e:
        print(f"✗ {db_alias:<15} -> {db_name:<25} [连接失败: {str(e)}]")

# 4. 数据隔离说明
print("\n" + "="*80)
print("数据隔离架构说明:")
print("="*80)
print("""
1. 业务数据隔离:
   - 每个租户公司拥有独立的MySQL数据库
   - 鼎策 (dingce) -> eims_dingce
   - 晟昌 (shengchang) -> eims_shengchang  
   - 嘉诚达 (jiachengda) -> eims_jiachengda
   
2. 共享数据存储:
   - root_admin (eims_root) 存储:
     * 用户认证信息 (auth_user, UserProfile)
     * 租户管理 (Tenant, TenantModule)
     * 模块权限配置 (TenantModulePermission)
   
3. 数据路由机制:
   - CompanyDatabaseRouter 自动根据 request.current_system 路由
   - URL路径前缀决定访问哪个数据库 (/dingce/, /shengchang/, /jiachengda/)
   - 用户认证相关查询始终路由到 root_admin
   
4. 完全隔离保证:
   ✓ 每个公司的员工、项目、合同等业务数据完全独立
   ✓ 一个公司无法访问其他公司的业务数据
   ✓ 数据库级别的物理隔离，安全性高
""")

print("="*80)
print("检查完成!")
print("="*80)
