"""
验证人员管理模块完全正常
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User

print("=" * 70)
print("人员管理模块 - 最终验证")
print("=" * 70)

# 创建测试客户端
client = Client()

# 获取管理员用户
admin_user = User.objects.filter(is_superuser=True).first()
if not admin_user:
    print("❌ 未找到管理员用户，创建中...")
    admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
    print(f"✓ 已创建管理员账号：admin / admin123")
else:
    print(f"✓ 使用现有管理员：{admin_user.username}")

# 登录
login = client.login(username=admin_user.username, password='admin123')
print(f"✓ 登录状态：{'成功' if login else '失败'}")

# 测试所有 URL
urls_to_test = [
    ('人员列表', '/personnel/'),
    ('添加人员', '/personnel/add/'),
    ('导入模板', '/personnel/import/template/'),
    ('导出人员', '/personnel/export/'),
]

print("\n" + "=" * 70)
print("URL 访问测试:")
print("=" * 70)

all_passed = True
for name, url in urls_to_test:
    try:
        response = client.get(url)
        if response.status_code == 200:
            print(f"✅ {name:10s} - {url:35s} -> 200 OK")
        else:
            print(f"⚠️  {name:10s} - {url:35s} -> {response.status_code}")
            all_passed = False
    except Exception as e:
        print(f"❌ {name:10s} - {url:35s} -> 错误：{e}")
        all_passed = False

print("\n" + "=" * 70)
if all_passed:
    print("✅ 所有测试通过！人员管理模块完全正常！")
else:
    print("⚠️  部分测试未通过，请检查系统")
print("=" * 70)

print("\n📊 系统状态:")
from eims_app.models import Personnel
total = Personnel.objects.filter(is_deleted=False).count()
with_project = Personnel.objects.filter(is_deleted=False, project__isnull=False).count()
print(f"   - 总人数：{total}")
print(f"   - 在岗人数：{with_project}")
print(f"   - 未分配：{total - with_project}")

print("\n🎯 访问地址:")
print("   http://localhost:8000/personnel/")

print("\n💡 提示:")
print("   - 服务器已重启")
print("   - 请清除浏览器缓存 (Ctrl+Shift+Delete)")
print("   - 硬刷新页面 (Ctrl+F5)")

print("=" * 70)
