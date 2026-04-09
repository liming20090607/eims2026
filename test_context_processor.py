import os
import sys
import django

sys.path.insert(0, '/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_local_mysql')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from eims_app.context_processors import sidebar_context

User = get_user_model()

print("=== 测试 sidebar_context 实际执行 ===\n")

# 创建模拟请求
factory = RequestFactory()
admin = User.objects.filter(is_superuser=True).first()

if admin:
    # 创建带认证用户的请求
    request = factory.get('/')
    request.user = admin
    request.session = {'sidebar_collapsed': False}
    
    print(f"测试用户: {admin.username} (is_superuser={admin.is_superuser})")
    print(f"用户认证状态: {request.user.is_authenticated}")
    
    # 执行 context processor
    try:
        context = sidebar_context(request)
        print(f"\nContext 返回结果:")
        print(f"  sidebar_collapsed: {context.get('sidebar_collapsed')}")
        print(f"  pending_count: {context.get('pending_count')}")
        
        tenants_all = context.get('tenants_all', [])
        print(f"  tenants_all 类型: {type(tenants_all)}")
        print(f"  tenants_all 数量: {tenants_all.count() if hasattr(tenants_all, 'count') else len(tenants_all)}")
        
        if hasattr(tenants_all, 'all'):
            for t in tenants_all.all():
                print(f"    - {t.name} (ID={t.id})")
        else:
            for t in tenants_all:
                print(f"    - {t.name} (ID={t.id})")
                
    except Exception as e:
        print(f"\n✗ 执行 context processor 时出错:")
        import traceback
        traceback.print_exc()
else:
    print("✗ 未找到超级管理员用户")

print("\n✅ 测试完成！")
