"""
验证项目编号前缀功能
"""
import os
import sys
import django

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Tenant, CostProjectUnified

print("=" * 60)
print("验证租户项目编号前缀配置")
print("=" * 60)

# 检查租户前缀
tenants_data = [
    ('dingce', 'DC'),
    ('shengchang', 'SC'),
    ('jiachengda', 'JCD'),
]

for code, expected_prefix in tenants_data:
    try:
        tenant = Tenant.objects.using('root_admin').get(code=code)
        actual_prefix = tenant.project_code_prefix
        status = "✅" if actual_prefix == expected_prefix else "❌"
        print(f"{status} {tenant.name}: {actual_prefix} (期望: {expected_prefix})")
    except Tenant.DoesNotExist:
        print(f"⚠️  {code} 不存在")

print("\n" + "=" * 60)
print("各租户现有项目数量")
print("=" * 60)

for code, prefix in tenants_data:
    try:
        tenant = Tenant.objects.using('root_admin').get(code=code)
        count = CostProjectUnified.objects.using(code).filter(tenant=tenant).count()
        print(f"{tenant.name}: {count} 个项目")
        
        # 显示最近5个项目编号
        projects = CostProjectUnified.objects.using(code).filter(tenant=tenant).order_by('-id')[:5]
        if projects:
            print(f"  最近项目: {[p.project_code for p in projects]}")
    except Exception as e:
        print(f"⚠️  {code}: {str(e)}")

print("\n✅ 验证完成！")
print("\n现在可以在浏览器中测试:")
print("1. 登录到任一租户系统")
print("2. 进入造价咨询 > 项目信息总表")
print("3. 点击'新增'按钮")
print("4. 查看项目编号字段是否自动填充了对应前缀的编号")
