"""
子模块数据初始化脚本
根据侧边栏菜单结构，为所有一级模块创建对应的子模块定义
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_tenant_module import TenantModule
from eims_app.models.model_sub_module import SubModule

# 定义所有一级模块及其子模块结构
SUBMODULES_CONFIG = [
    {
        'module_code': 'supervision',
        'module_name': '工程监理',
        'submodules': [
            {'code': 'project', 'name': '项目管理', 'icon': 'bi-kanban', 'url_name': 'eims_app:project_list', 'url_pattern': '/project/', 'sort_order': 1},
            {'code': 'contract', 'name': '合同管理', 'icon': 'bi-file-earmark-text', 'url_name': 'eims_app:contract_list', 'url_pattern': '/contract/', 'sort_order': 2},
            {'code': 'output_payment', 'name': '产值回款', 'icon': 'bi-cash-stack', 'url_name': 'eims_app:output_payment_list', 'url_pattern': '/output-payment/', 'sort_order': 3},
        ]
    },
    {
        'module_code': 'cost',
        'module_name': '造价咨询',
        'submodules': [
            {'code': 'cost_project', 'name': '项目管理', 'icon': 'bi-kanban', 'url_name': 'eims_app:cost_project_ledger_list', 'url_pattern': '/cost/project/', 'sort_order': 1},
            {'code': 'cost_contract', 'name': '合同管理', 'icon': 'bi-file-earmark-text', 'url_name': 'eims_app:cost_contract_management_list', 'url_pattern': '/cost/contract/', 'sort_order': 2},
            {'code': 'cost_output_payment', 'name': '产值回款', 'icon': 'bi-cash-stack', 'url_name': 'eims_app:cost_output_payment_list', 'url_pattern': '/cost/output-payment/', 'sort_order': 3},
        ]
    },
    {
        'module_code': 'approval',
        'module_name': '审批流程',
        'submodules': [
            {'code': 'my_pending_approvals', 'name': '我的待审批', 'icon': 'bi-clock-history', 'url_name': 'eims_app:my_pending_approvals', 'url_pattern': '/my-pending-approvals/', 'sort_order': 1},
            {'code': 'contract_approval', 'name': '合同审批', 'icon': 'bi-file-earmark-check', 'url_name': 'eims_app:contract_approval_chain', 'url_pattern': '/contract-approval/', 'sort_order': 2},
            {'code': 'seal_approval', 'name': '用印审批', 'icon': 'bi-stamp', 'url_name': 'eims_app:seal_approval_chain', 'url_pattern': '/seal-approval/', 'sort_order': 3},
            {'code': 'archive_approval', 'name': '归档审批', 'icon': 'bi-archive', 'url_name': 'eims_app:archive_approval_chain', 'url_pattern': '/archive-approval/', 'sort_order': 4},
        ]
    },
    {
        'module_code': 'preparation',
        'module_name': '项目前期',
        'submodules': [
            {'code': 'preparation_list', 'name': '前期项目', 'icon': 'bi-clipboard-data', 'url_name': 'eims_app:module_preparation', 'url_pattern': '/module/preparation/', 'sort_order': 1},
        ]
    },
    {
        'module_code': 'bidding',
        'module_name': '招标投标',
        'submodules': [
            {'code': 'bidding_list', 'name': '招标项目', 'icon': 'bi-trophy', 'url_name': 'eims_app:module_bidding', 'url_pattern': '/module/bidding/', 'sort_order': 1},
        ]
    },
    {
        'module_code': 'design',
        'module_name': '工程设计',
        'submodules': [
            {'code': 'design_list', 'name': '设计项目', 'icon': 'bi-palette', 'url_name': 'eims_app:module_design', 'url_pattern': '/module/design/', 'sort_order': 1},
        ]
    },
    {
        'module_code': 'construction',
        'module_name': '工程施工',
        'submodules': [
            {'code': 'construction_list', 'name': '施工项目', 'icon': 'bi-hammer', 'url_name': 'eims_app:module_construction', 'url_pattern': '/module/construction/', 'sort_order': 1},
        ]
    },
    {
        'module_code': 'completion',
        'module_name': '竣工验收',
        'submodules': [
            {'code': 'completion_list', 'name': '验收项目', 'icon': 'bi-check2-circle', 'url_name': 'eims_app:module_completion', 'url_pattern': '/module/completion/', 'sort_order': 1},
        ]
    },
]


def init_submodules():
    """初始化所有子模块数据"""
    
    print("="*80)
    print("子模块数据初始化")
    print("="*80)
    
    total_created = 0
    total_updated = 0
    total_skipped = 0
    
    for module_config in SUBMODULES_CONFIG:
        module_code = module_config['module_code']
        module_name = module_config['module_name']
        
        # 查找对应的一级模块
        try:
            parent_module = TenantModule.objects.get(code=module_code)
        except TenantModule.DoesNotExist:
            print(f"\n❌ 一级模块 '{module_name}' (code={module_code}) 不存在，跳过")
            continue
        
        print(f"\n📦 处理一级模块: {module_name} ({module_code})")
        print("-" * 80)
        
        for sub_config in module_config['submodules']:
            sub_code = sub_config['code']
            sub_name = sub_config['name']
            
            # 查找或创建子模块
            sub_module, created = SubModule.objects.get_or_create(
                parent_module=parent_module,
                code=sub_code,
                defaults={
                    'name': sub_name,
                    'icon': sub_config.get('icon', 'bi-circle'),
                    'url_name': sub_config.get('url_name', ''),
                    'url_pattern': sub_config.get('url_pattern', ''),
                    'sort_order': sub_config.get('sort_order', 0),
                    'is_active': True,
                }
            )
            
            if created:
                total_created += 1
                print(f"  ✓ 创建: {sub_name} ({sub_code})")
            else:
                # 更新现有子模块的信息
                updated = False
                if sub_module.name != sub_name:
                    sub_module.name = sub_name
                    updated = True
                if sub_module.icon != sub_config.get('icon', 'bi-circle'):
                    sub_module.icon = sub_config.get('icon', 'bi-circle')
                    updated = True
                if sub_module.url_name != sub_config.get('url_name', ''):
                    sub_module.url_name = sub_config.get('url_name', '')
                    updated = True
                if sub_module.url_pattern != sub_config.get('url_pattern', ''):
                    sub_module.url_pattern = sub_config.get('url_pattern', '')
                    updated = True
                
                if updated:
                    sub_module.save()
                    total_updated += 1
                    print(f"  ↻ 更新: {sub_name} ({sub_code})")
                else:
                    total_skipped += 1
                    print(f"  - 已存在: {sub_name} ({sub_code})")
    
    # 统计信息
    print("\n" + "="*80)
    print("初始化完成!")
    print("="*80)
    print(f"  ✓ 新建: {total_created} 个子模块")
    print(f"  ↻ 更新: {total_updated} 个子模块")
    print(f"  - 跳过: {total_skipped} 个子模块")
    print(f"  总计: {SubModule.objects.count()} 个子模块")
    print("="*80)
    
    # 显示所有子模块
    print("\n📋 当前所有子模块:")
    print("-" * 80)
    for sub in SubModule.objects.select_related('parent_module').order_by('parent_module__sort_order', 'sort_order'):
        status = "✓" if sub.is_active else "✗"
        print(f"  {status} {sub.parent_module.name:12} - {sub.name:15} ({sub.code})")


if __name__ == '__main__':
    try:
        init_submodules()
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
