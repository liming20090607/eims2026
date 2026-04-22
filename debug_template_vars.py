"""诊断为什么模板中的tenants_all为空"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.template import Template, Context
from django.contrib.auth import get_user_model
from eims_app.models import UserProfile, Tenant

User = get_user_model()

print("=" * 70)
print("诊断模板中tenants_all变量问题")
print("=" * 70)

# 1. 检查settings.py中的context_processors配置
print("\n1. 检查settings.py中的context_processors配置:")
with open('settings.py', 'r', encoding='utf-8') as f:
    content = f.read()
    if 'eims_app.context_processors.sidebar_context' in content:
        print("   ✅ context_processors.sidebar_context 已正确配置")
    else:
        print("   ❌ context_processors.sidebar_context 未找到")
        
    if 'eims_app.context_processors.global_settings' in content:
        print("   ⚠️  global_settings 也存在（可能导致覆盖问题）")

# 2. 检查context_processors.py中是否有多个函数
print("\n2. 检查context_processors.py中的函数:")
with open('eims_app/context_processors.py', 'r', encoding='utf-8') as f:
    content = f.read()
    import re
    functions = re.findall(r'^def (\w+)\(', content, re.MULTILINE)
    print(f"   找到的函数: {functions}")
    
    if 'global_settings' in functions and 'sidebar_context' in functions:
        print("   ⚠️  检测到两个函数，global_settings可能覆盖sidebar_context")

# 3. 模拟模板渲染
print("\n3. 模拟模板渲染测试:")
root_user = User.objects.get(username='root')

# 创建模拟request
class MockRequest:
    def __init__(self, user):
        self.user = user
        self.session = {'tenant_id': 2}
        from eims_app.models import Tenant
        self.tenant = Tenant.objects.get(id=2)

mock_request = MockRequest(root_user)

# 测试sidebar_context
from eims_app.context_processors import sidebar_context
result = sidebar_context(mock_request)
print(f"   sidebar_context返回的tenants_all数量: {len(result.get('tenants_all', []))}")
print(f"   sidebar_context返回的所有键: {list(result.keys())}")

# 测试global_settings
from eims_app.context_processors import global_settings
result2 = global_settings(mock_request)
print(f"   global_settings返回的键: {list(result2.keys())}")

# 检查是否有重复键
overlap = set(result.keys()) & set(result2.keys())
if overlap:
    print(f"   ⚠️  两个函数有重复的键: {overlap}")

# 4. 实际测试模板渲染
print("\n4. 测试实际模板变量注入:")
try:
    template_str = """
{% for tenant in tenants_all %}
  {{ tenant.name }}
{% empty %}
  无租户
{% endfor %}
    """
    template = Template(template_str)
    context_data = {}
    context_data.update(global_settings(mock_request))
    context_data.update(sidebar_context(mock_request))
    context = Context(context_data)
    rendered = template.render(context)
    print(f"   渲染结果: {rendered.strip()}")
    print(f"   使用的tenants_all数量: {len(context_data.get('tenants_all', []))}")
except Exception as e:
    print(f"   ❌ 模板渲染失败: {e}")

print("\n" + "=" * 70)
print("诊断完成")
print("=" * 70)
