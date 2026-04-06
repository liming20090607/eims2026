#!/usr/bin/env python3
"""
恢复用户组和权限数据
在服务器上运行此脚本
"""
import sys
import os

# 设置 Django 环境
sys.path.append('/var/www/eims')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

import django
django.setup()

from django.contrib.auth.models import User, Group, Permission
import json

print("=" * 60)
print("Restore User Groups and Permissions")
print("=" * 60)

# 步骤 1: 读取备份文件
print("\n[Step 1] Reading backup file...")
backup_file = '/root/backup_before_phase4.json'

if not os.path.exists(backup_file):
    print(f"ERROR: Backup file not found: {backup_file}")
    print("Please upload it first:")
    print("scp E:\\EIMS2026\\backup_before_phase4.json root@39.106.41.239:/root/")
    sys.exit(1)

try:
    with open(backup_file, 'rb') as f:
        raw_content = f.read()
    
    # 检测并移除 BOM
    if raw_content.startswith(b'\xef\xbb\xbf'):
        print('  Detected UTF-8 BOM, removing...')
        raw_content = raw_content[3:]
    elif raw_content.startswith(b'\xff\xfe'):
        print('  Detected UTF-16 LE BOM, converting...')
        raw_content = raw_content.decode('utf-16-le').encode('utf-8')
    elif raw_content.startswith(b'\xfe\xff'):
        print('  Detected UTF-16 BE BOM, converting...')
        raw_content = raw_content.decode('utf-16-be').encode('utf-8')
    
    # 解码为字符串
    content = raw_content.decode('utf-8')
    
    # 清理第一行 Python path（如果存在）
    first_line_end = content.find('\n')
    if first_line_end != -1 and 'Python path' in content[:first_line_end]:
        print('  Removing Python path line...')
        content = content[first_line_end + 1:]
    
    # 找到 JSON 数组开始位置
    start = content.find('[')
    if start == -1:
        raise ValueError("Cannot find JSON array start '['")
    
    data = json.loads(content[start:])
    print(f'✓ Successfully read backup file')
except Exception as e:
    print(f'✗ Error reading file: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 提取 Group 和 User 数据
groups_data = [obj for obj in data if obj['model'] == 'auth.group']
users_data = [obj for obj in data if obj['model'] == 'auth.user']

print(f"✓ Found {len(groups_data)} groups")
print(f"✓ Found {len(users_data)} users")

# 步骤 2: 清除现有用户组
print("\n[Step 2] Clearing existing groups...")
Group.objects.all().delete()
print("✓ Cleared all existing groups")

# 步骤 3: 恢复用户组
print("\n[Step 3] Restoring groups...")
for group_obj in groups_data:
    try:
        pk = group_obj['pk']
        fields = group_obj['fields']
        perm_ids = fields.get('permissions', [])
        
        group, created = Group.objects.update_or_create(
            id=pk,
            defaults={'name': fields['name']}
        )
        
        if perm_ids:
            permissions = Permission.objects.filter(id__in=perm_ids)
            group.permissions.set(permissions)
        
        status = 'Created' if created else 'Updated'
        print(f"✓ [{status}] Group: {group.name} (ID={group.id}), Permissions: {group.permissions.count()}")
        
    except Exception as e:
        print(f"✗ Error (Group ID={group_obj.get('pk', '?')}): {e}")

# 步骤 4: 恢复用户的组成员关系
print("\n[Step 4] Restoring user-group relationships...")
success_count = 0
error_count = 0

for user_obj in users_data:
    try:
        pk = user_obj['pk']
        fields = user_obj['fields']
        
        # 跳过超级管理员（admin）的组关系
        if pk == 1:
            continue
        
        # 尝试获取用户
        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            print(f"⚠ Skip: User ID={pk} ({fields.get('username', 'unknown')}) does not exist")
            continue
        
        # 获取组 ID 列表
        group_ids = fields.get('groups', [])
        
        if group_ids:
            # 设置用户的组
            groups = Group.objects.filter(id__in=group_ids)
            user.groups.set(groups)
            success_count += 1
            print(f"✓ User {user.username}: assigned to {len(group_ids)} groups")
        else:
            success_count += 1
            
    except Exception as e:
        error_count += 1
        print(f"✗ Error (User ID={user_obj.get('pk', '?')}): {e}")

print(f"\nCompleted! Success: {success_count}, Errors: {error_count}")

# 步骤 5: 验证结果
print("\n[Step 5] Verification...")
all_groups = Group.objects.all().order_by('id')
print(f"Total groups in database: {len(all_groups)}")
for group in all_groups:
    print(f"  - ID={group.id}, Name={group.name}, Members={group.user_set.count()}, Permissions={group.permissions.count()}")

users_with_groups = User.objects.filter(groups__isnull=False).distinct()
print(f"\nUsers with group assignments: {users_with_groups.count()}")

print("\n" + "=" * 60)
print("Restoration completed successfully!")
print("=" * 60)
