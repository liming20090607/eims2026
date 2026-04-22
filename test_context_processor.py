"""
测试 context_processors 是否正确返回租户列表
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model
from eims_app.models import Tenant, UserProfile, UserTenantRelation
from eims_app.context_processors import sidebar_context
from unittest.mock import Mock

User = get_user_model()

print("=" * 80)
print("测试 context_processors.sidebar_context")
print("=" * 80)

# 测试几个不同类型的用户
test_users = [
    ('root', '超级管理员，有多公司关联'),
    ('admin', '超级管理员，单公司关联'),
    ('秦方玉', '普通用户，单公司关联'),
    ('黎绍昆', '超级管理员，多公司关联'),
]

for username, description in test_users:
    try:
        user = User.objects.get(username=username)
        
        # 创建模拟 request 对象
        mock_request = Mock()
        mock_request.user = user
        mock_request.session = {'tenant_id': 2}  # 模拟已选择租户
        
        # 调用 context_processors
        context = sidebar_context(mock_request)
        
        print(f"\n用户: {username}")
        print(f"说明: {description}")
        print(f"  - 是超级管理员: {user.is_superuser}")
        print(f"  - tenants_all 数量: {len(context['tenants_all'])}")
        print(f"  - 可切换的公司:")
        for tenant in context['tenants_all']:
            current_marker = " (当前)" if tenant.id == 2 else ""
            print(f"    • {tenant.name}{current_marker}")
        print(f"  - 启用模块数: {len(context['enabled_module_codes'])}")
        
    except User.DoesNotExist:
        print(f"\n✗ 用户 '{username}' 不存在")
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
