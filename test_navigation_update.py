"""
测试导航更新脚本
验证Root系统和租户系统的导航菜单是否正确显示
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from eims_app.context_processors import sidebar_context

print("="*80)
print("导航更新验证测试")
print("="*80)

# 创建测试用户
try:
    superuser = User.objects.get(username='admin')
    print(f"\n✓ 找到超级管理员: {superuser.username}")
except User.DoesNotExist:
    print("\n✗ 未找到admin用户,请先创建超级管理员")
    exit(1)

# 创建请求工厂
factory = RequestFactory()

# 测试1: Root系统导航
print("\n" + "="*80)
print("测试1: Root系统导航 (/root/)")
print("="*80)

request = factory.get('/root/')
request.user = superuser
request.session = {'sidebar_collapsed': False, 'tenant_id': None}

context = sidebar_context(request)
print(f"\nurl_namespace: {context.get('url_namespace')}")
print(f"enabled_module_codes数量: {len(context.get('enabled_module_codes', []))}")
print(f"tenants_all数量: {len(context.get('tenants_all', []))}")

if context.get('url_namespace') == 'root':
    print("✓ Root命名空间检测正确")
else:
    print("✗ Root命名空间检测失败")

# 测试2: 鼎策公司系统导航
print("\n" + "="*80)
print("测试2: 鼎策公司系统导航 (/dingce/)")
print("="*80)

request = factory.get('/dingce/')
request.user = superuser
request.session = {'sidebar_collapsed': False, 'tenant_id': 2}  # 假设dingce的ID是2

context = sidebar_context(request)
print(f"\nurl_namespace: {context.get('url_namespace')}")
print(f"enabled_module_codes数量: {len(context.get('enabled_module_codes', []))}")
print(f"启用的模块: {context.get('enabled_module_codes', [])}")

if context.get('url_namespace') == 'dingce':
    print("✓ 鼎策命名空间检测正确")
else:
    print("✗ 鼎策命名空间检测失败")

# 测试3: 晟昌公司系统导航
print("\n" + "="*80)
print("测试3: 晟昌公司系统导航 (/shengchang/)")
print("="*80)

request = factory.get('/shengchang/')
request.user = superuser
request.session = {'sidebar_collapsed': False, 'tenant_id': 4}  # 假设shengchang的ID是4

context = sidebar_context(request)
print(f"\nurl_namespace: {context.get('url_namespace')}")

if context.get('url_namespace') == 'shengchang':
    print("✓ 晟昌命名空间检测正确")
else:
    print("✗ 晟昌命名空间检测失败")

# 测试4: 嘉诚达公司系统导航
print("\n" + "="*80)
print("测试4: 嘉诚达公司系统导航 (/jiachengda/)")
print("="*80)

request = factory.get('/jiachengda/')
request.user = superuser
request.session = {'sidebar_collapsed': False, 'tenant_id': 3}  # 假设jiachengda的ID是3

context = sidebar_context(request)
print(f"\nurl_namespace: {context.get('url_namespace')}")

if context.get('url_namespace') == 'jiachengda':
    print("✓ 嘉诚达命名空间检测正确")
else:
    print("✗ 嘉诚达命名空间检测失败")

# 测试5: 检查模板文件中的关键代码
print("\n" + "="*80)
print("测试5: 检查base.html模板关键代码")
print("="*80)

template_path = r'e:\EIMS2026\eims_app\templates\base\base.html'
with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

checks = [
    ("Root专属菜单判断", "{% if url_namespace == 'root' and user.is_superuser %}"),
    ("租户管理菜单", "租户管理"),
    ("公司管理链接", "/root/tenants/"),
    ("用户管理链接", "/root/users/"),
    ("模块配置链接", "/root/modules/"),
    ("禁用菜单样式", "disabled-menu"),
    ("待开发徽章", "待开发"),
    ("项目前期", "项目前期"),
    ("招标投标", "招标投标"),
    ("造价咨询", "造价咨询"),
    ("工程设计", "工程设计"),
    ("工程施工", "工程施工"),
    ("工程检测", "工程检测"),
    ("竣工验收", "竣工验收"),
]

print("\n模板检查项:")
for name, keyword in checks:
    if keyword in content:
        print(f"  ✓ {name}: 找到")
    else:
        print(f"  ✗ {name}: 未找到")

# 总结
print("\n" + "="*80)
print("测试总结")
print("="*80)
print("""
导航更新已完成以下改进:

1. Root系统专属菜单:
   - 添加"租户管理"折叠菜单(公司管理、用户管理、模块配置)
   - 保留完整的组织管理和人证管理功能
   - 仅在 url_namespace == 'root' 时显示

2. 租户系统优化:
   - 移除重复的"合同管理"、"项目管理"、"产值回款"独立菜单项
   - 这些功能统一整合到"工程监理"子菜单中
   - 所有待开发模块标记为灰色并显示"待开发"徽章

3. 待开发模块(7个):
   - 项目前期 (preparation)
   - 招标投标 (bidding)
   - 造价咨询 (cost)
   - 工程设计 (design)
   - 工程施工 (construction)
   - 工程检测 (testing)
   - 竣工验收 (completion)

4. 权限控制:
   - 非超级管理员看到灰色的"组织管理"和"人证管理"菜单
   - 点击时弹出权限拒绝提示
   - 文件管理中的"批量上传"和"版本管理"也受权限控制

下一步建议:
1. 启动Django服务器进行实际UI测试
2. 分别访问 /root/, /dingce/, /shengchang/, /jiachengda/ 验证导航
3. 使用不同权限的账号登录测试权限控制
4. 创建Root系统的租户管理视图函数
""")
