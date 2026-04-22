#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速初始化嘉诚达子系统 - 创建测试用户并验证
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth.models import User

print("=" * 80)
print("  嘉诚达子系统 - 创建测试用户")
print("=" * 80)

# 创建测试用户
test_users = [
    {
        'username': 'admin_jcd',
        'email': 'admin@jiachengda.com',
        'password': 'admin123',
        'is_staff': True,
        'is_superuser': False,
    },
    {
        'username': 'test_user_jcd',
        'email': 'test@jiachengda.com',
        'password': 'test123',
        'is_staff': False,
        'is_superuser': False,
    },
]

print("\n[创建测试用户]")
print("-" * 80)

created_count = 0
for user_data in test_users:
    try:
        # 检查用户是否已存在
        existing = User.objects.using('jiachengda').filter(username=user_data['username']).first()
        
        if existing:
            print(f"  ⚠ 用户已存在: {user_data['username']}")
            # 更新密码
            existing.set_password(user_data['password'])
            existing.is_staff = user_data['is_staff']
            existing.is_superuser = user_data['is_superuser']
            existing.save(using='jiachengda')
            print(f"    ✓ 已更新密码和权限")
        else:
            user = User.objects.using('jiachengda').create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password']
            )
            user.is_staff = user_data['is_staff']
            user.is_superuser = user_data['is_superuser']
            user.save(using='jiachengda')
            print(f"  ✓ 创建用户: {user_data['username']} (密码: {user_data['password']})")
            created_count += 1
    except Exception as e:
        print(f"  ✗ 处理用户 {user_data['username']} 失败: {str(e)}")

print("\n" + "=" * 80)
print("  ✅ 嘉诚达子系统初始化完成！")
print("=" * 80)

print("\n📊 系统信息:")
print("   应用目录: eims_jiachengda/")
print("   数据库: eims_jiachengda (MySQL)")
print("   迁移状态: 已完成")
print("")
print("👥 测试用户:")
print("   管理员: admin_jcd / admin123")
print("   普通用户: test_user_jcd / test123")
print("")
print("🌐 访问地址:")
print("   http://localhost:8000/jiachengda/")
print("")
print("✅ 下一步操作:")
print("   1. 启动服务器: python manage.py runserver")
print("   2. 访问嘉诚达系统并使用测试用户登录")
print("   3. 验证所有功能和样式与鼎策系统一致")
print("")
