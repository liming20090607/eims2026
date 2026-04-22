#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建嘉诚达数据库并初始化测试数据
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

import pymysql
from django.contrib.auth.models import User
from django.core.management import call_command

print("=" * 80)
print("  创建嘉诚达数据库和测试数据")
print("=" * 80)

# ==================== 步骤1: 创建数据库 ====================
print("\n[步骤 1] 创建嘉诚达数据库")
print("-" * 80)

try:
    # 连接到MySQL服务器
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='root123',
        port=3306,
        charset='utf8mb4'
    )
    
    cursor = connection.cursor()
    
    # 检查数据库是否存在
    cursor.execute("SHOW DATABASES LIKE 'eims_jiachengda';")
    result = cursor.fetchone()
    
    if result:
        print("  ⚠ 数据库 eims_jiachengda 已存在")
        response = input("  是否删除并重新创建？(yes/no): ")
        if response.lower() == 'yes':
            cursor.execute("DROP DATABASE eims_jiachengda;")
            print("  ✓ 已删除现有数据库")
            # 重新创建数据库
            cursor.execute("""
                CREATE DATABASE eims_jiachengda 
                DEFAULT CHARACTER SET utf8mb4 
                DEFAULT COLLATE utf8mb4_unicode_ci;
            """)
            print("  ✓ 数据库 eims_jiachengda 重新创建成功")
        else:
            print("  跳过数据库创建")
    else:
        # 创建新数据库
        cursor.execute("""
            CREATE DATABASE eims_jiachengda 
            DEFAULT CHARACTER SET utf8mb4 
            DEFAULT COLLATE utf8mb4_unicode_ci;
        """)
        print("  ✓ 数据库 eims_jiachengda 创建成功")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"  ✗ 数据库创建失败: {str(e)}")
    sys.exit(1)

# ==================== 步骤2: 执行数据库迁移 ====================
print("\n[步骤 2] 执行嘉诚达数据库迁移")
print("-" * 80)

try:
    call_command('migrate', '--database=jiachengda', verbosity=1)
    print("  ✓ 数据库迁移完成")
except Exception as e:
    print(f"  ✗ 迁移失败: {str(e)}")
    sys.exit(1)

# ==================== 步骤3: 创建测试用户 ====================
print("\n[步骤 3] 创建测试用户")
print("-" * 80)

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

created_count = 0
for user_data in test_users:
    try:
        if not User.objects.using('jiachengda').filter(username=user_data['username']).exists():
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
        else:
            print(f"  ⚠ 用户已存在: {user_data['username']}")
    except Exception as e:
        print(f"  ✗ 创建用户 {user_data['username']} 失败: {str(e)}")

if created_count == 0:
    print("  ⚠ 没有创建新用户，所有用户已存在")

# ==================== 步骤4: 从鼎策复制基础数据（可选）====================
print("\n[步骤 4] 从鼎策复制基础配置数据")
print("-" * 80)
print("  提示: 此步骤将复制部门、角色等基础配置（不包括业务数据）")
print("  如需完整复制所有数据，请手动执行:")
print("    python manage.py dumpdata --database=dingce > temp_data.json")
print("    python manage.py loaddata --database=jiachengda temp_data.json")
print("")

response = input("  是否复制基础配置数据？(yes/no): ")
if response.lower() == 'yes':
    try:
        # 导出鼎策的基础数据（排除业务数据）
        print("  正在导出鼎策基础数据...")
        call_command(
            'dumpdata',
            '--database=dingce',
            '--indent=2',
            '--natural-foreign',
            '--natural-primary',
            '-e', 'contenttypes',
            '-e', 'auth.Permission',
            '-e', 'sessions.session',
            '-e', 'eims_app.projectdetail',  # 排除项目数据
            '-e', 'eims_app.contract',  # 排除合同数据
            '-e', 'eims_app.personnel',  # 排除人员数据
            '--output=temp_dingce_config.json'
        )
        print("  ✓ 基础数据导出成功")
        
        # 导入到嘉诚达
        print("  正在导入到嘉诚达...")
        call_command(
            'loaddata',
            '--database=jiachengda',
            'temp_dingce_config.json'
        )
        print("  ✓ 基础数据导入成功")
        
        # 清理临时文件
        import os
        if os.path.exists('temp_dingce_config.json'):
            os.remove('temp_dingce_config.json')
            print("  ✓ 已清理临时文件")
            
    except Exception as e:
        print(f"  ⚠ 数据复制失败: {str(e)}")
        print("  这不影响系统使用，可以稍后手动添加数据")
else:
    print("  跳过数据复制")

# ==================== 总结 ====================
print("\n" + "=" * 80)
print("  嘉诚达子系统初始化完成！")
print("=" * 80)
print("\n📊 数据库信息:")
print("   数据库名: eims_jiachengda")
print("   字符集: utf8mb4")
print("")
print("👥 测试用户:")
print("   管理员: admin_jcd / admin123")
print("   普通用户: test_user_jcd / test123")
print("")
print("🌐 访问地址:")
print("   http://localhost:8000/jiachengda/")
print("")
print("✅ 下一步:")
print("   1. 启动服务器: python manage.py runserver")
print("   2. 访问嘉诚达系统并使用测试用户登录")
print("   3. 根据需要添加更多测试数据")
print("")
