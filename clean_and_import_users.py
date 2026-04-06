#!/usr/bin/env python
# 清理用户数据文件并导入
import os
import sys

# 确保可以导入Django设置
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

import django
django.setup()

# 文件路径
input_file = 'eims_app/fixtures/users_export_clean.json'
output_file = 'eims_app/fixtures/users_clean_fixed.json'

print("=" * 60)
print("清理用户数据文件...")
print("=" * 60)

# 读取并清理文件
with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# 找到JSON数组开始的行（以[开头）
json_start_line = 0
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith('['):
        json_start_line = i
        break

print(f"找到JSON开始位置：第 {json_start_line + 1} 行")
print(f"总行数：{len(lines)}")

# 提取JSON内容
json_lines = lines[json_start_line:]

# 写入清理后的文件
with open(output_file, 'w', encoding='utf-8') as f:
    f.writelines(json_lines)

print(f"已保存清理后的文件：{output_file}")

# 显示清理后文件的前3行
print("\n清理后的文件前3行：")
for i, line in enumerate(json_lines[:3], 1):
    print(f"  {i}: {line.rstrip()}")

# 统计用户数量
import json
try:
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    user_count = sum(1 for item in data if item.get('model') == 'auth.user')
    group_count = sum(1 for item in data if item.get('model') == 'auth.group')
    perm_count = sum(1 for item in data if item.get('model') == 'auth.permission')
    
    print(f"\n数据统计：")
    print(f"  用户数量：{user_count}")
    print(f"  用户组数量：{group_count}")
    print(f"  权限数量：{perm_count}")
    
except json.JSONDecodeError as e:
    print(f"\n警告：JSON解析问题 - {e}")
    print("将继续尝试导入...")

print("\n" + "=" * 60)
print("开始导入数据到本地数据库...")
print("=" * 60 + "\n")

# 使用Django的loaddata命令
from django.core.management import call_command

try:
    # 使用 --ignorenonexistent 跳过已存在的记录
    call_command('loaddata', output_file, ignorenonexistent=True)
    print("\n" + "=" * 60)
    print("✅ 数据导入成功！")
    print("=" * 60)
except Exception as e:
    error_msg = str(e)
    if 'UNIQUE constraint failed' in error_msg or 'unique' in error_msg.lower():
        print("\n" + "=" * 60)
        print("⚠️  部分用户已存在，尝试单独导入...")
        print("=" * 60 + "\n")
        
        # 手动逐个导入用户，跳过已存在的
        import json
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        from django.contrib.auth.models import User, Group, Permission
        from django.contrib.contenttypes.models import ContentType
        
        created_users = 0
        skipped_users = 0
        failed_users = 0
        
        for item in data:
            if item['model'] == 'auth.user':
                username = item['fields']['username']
                if User.objects.filter(username=username).exists():
                    skipped_users += 1
                    continue
                
                try:
                    User.objects.create(
                        id=item['pk'],
                        username=username,
                        password=item['fields']['password'],
                        first_name=item['fields'].get('first_name', ''),
                        last_name=item['fields'].get('last_name', ''),
                        email=item['fields'].get('email', ''),
                        is_staff=item['fields'].get('is_staff', False),
                        is_active=item['fields'].get('is_active', True),
                        is_superuser=item['fields'].get('is_superuser', False),
                        date_joined=item['fields'].get('date_joined', None),
                        last_login=item['fields'].get('last_login', None)
                    )
                    created_users += 1
                except Exception as user_error:
                    failed_users += 1
                    print(f"  创建用户 {username} 失败：{user_error}")
        
        print(f"\n用户导入结果：")
        print(f"  新增：{created_users} 个")
        print(f"  跳过：{skipped_users} 个（已存在）")
        print(f"  失败：{failed_users} 个")
        print("\n✅ 数据导入完成！")
    else:
        print(f"\n❌ 导入失败：{e}")
        sys.exit(1)

# 验证结果
print("\n" + "=" * 60)
print("验证导入结果...")
print("=" * 60 + "\n")

from django.contrib.auth.models import User
from eims_app.models import UserProfile

user_count = User.objects.count()
profile_count = UserProfile.objects.count()

print(f"用户账号总数：{user_count}")
print(f"用户资料总数：{profile_count}")

# 显示最新的5个用户
print("\n最新的5个用户：")
for user in User.objects.order_by('-id')[:5]:
    profile = getattr(user, 'userprofile', None)
    real_name = profile.real_name if profile else '-'
    print(f"  - {user.username} | 姓名：{real_name} | ID：{user.id}")

print("\n" + "=" * 60)
print("✅ 用户数据同步完成！")
print("=" * 60)
print("\n现在您可以访问：")
print("  用户管理页面：http://127.0.0.1:8000/user-management/")
print("  Django Admin：http://127.0.0.1:8000/admin/")
print("")
