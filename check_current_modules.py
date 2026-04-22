"""
检查当前模块配置和导航结构
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_tenant_module import TenantModule
from eims_app.models.model_tenant import Tenant

print("="*80)
print("当前业务模块配置")
print("="*80)

modules = TenantModule.objects.all().order_by('sort_order')
print(f"\n共有 {modules.count()} 个模块:\n")

for module in modules:
    print(f"  {module.sort_order}. {module.name:15} (代码: {module.code:15}) 图标: {module.icon:20} {'✓ 启用' if module.is_active else '✗ 禁用'}")

print("\n" + "="*80)
print("租户配置")
print("="*80)

tenants = Tenant.objects.all()
print(f"\n共有 {tenants.count()} 个租户:\n")

for tenant in tenants:
    print(f"  - {tenant.name} (代码: {tenant.code})")

print("\n" + "="*80)
print("建议的导航结构")
print("="*80)
print("""
【Root超级管理员后台】(/root/)
├── 首页
├── 系统导航
├── 组织管理
│   ├── 模块导航
│   ├── 部门管理
│   ├── 角色配置
│   └── 审批管理
├── 人证管理
│   ├── 模块导航
│   ├── 人员花名册
│   ├── 人员证书
│   ├── 可视化分配
│   └── 人员去向
├── 审批流程
│   ├── 我的待审批
│   ├── 合同审批
│   ├── 用印审批
│   └── 归档审批
├── 合同管理
├── 项目管理
├── 产值回款
├── 工程监理（一级模块）
│   ├── 项目管理
│   ├── 合同管理
│   └── 产值回款
├── 文件管理
│   ├── 文件列表
│   ├── 批量上传
│   └── 版本管理
├── 通知公告
│   ├── 通知列表
│   └── 批量上传
└── 后台管理
    ├── Django 后台
    └── 用户账号管理

【租户公司系统】(/dingce/, /shengchang/, /jiachengda/)
├── 首页
├── 系统导航
├── 人证管理（仅超级管理员）
├── 审批流程
│   ├── 我的待审批
│   ├── 合同审批
│   ├── 用印审批
│   └── 归档审批
├── 工程监理（按模块权限显示）
│   ├── 项目管理
│   ├── 合同管理
│   └── 产值回款
├── 文件管理
│   ├── 文件列表
│   ├── 批量上传（仅超级管理员）
│   └── 版本管理（仅超级管理员）
├── 通知公告
│   ├── 通知列表
│   └── 批量上传
└── 后台管理（仅管理员/超级管理员）
    ├── Django 后台
    └── 用户账号管理
""")
