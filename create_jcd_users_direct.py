#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接在嘉诚达数据库中创建测试用户
"""

import pymysql
from django.contrib.auth.hashers import make_password

print("=" * 80)
print("  在嘉诚达数据库中直接创建测试用户")
print("=" * 80)

try:
    # 连接到嘉诚达数据库
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='root123',
        database='eims_jiachengda',
        port=3306,
        charset='utf8mb4'
    )
    
    cursor = connection.cursor()
    
    # 检查auth_user表是否存在
    cursor.execute("SHOW TABLES LIKE 'auth_user';")
    if not cursor.fetchone():
        print("\n✗ auth_user 表不存在！")
        print("  请先执行: python manage.py migrate auth --database=jiachengda")
        cursor.close()
        connection.close()
        exit(1)
    
    print("\n✓ auth_user 表存在")
    
    # 创建测试用户
    test_users = [
        {
            'username': 'admin_jcd',
            'email': 'admin@jiachengda.com',
            'password': 'admin123',
            'is_staff': 1,
            'is_superuser': 0,
        },
        {
            'username': 'test_user_jcd',
            'email': 'test@jiachengda.com',
            'password': 'test123',
            'is_staff': 0,
            'is_superuser': 0,
        },
    ]
    
    print("\n[创建/更新测试用户]")
    print("-" * 80)
    
    for user_data in test_users:
        # 检查用户是否已存在
        cursor.execute("SELECT id FROM auth_user WHERE username = %s", (user_data['username'],))
        existing = cursor.fetchone()
        
        if existing:
            # 更新现有用户
            hashed_password = make_password(user_data['password'])
            cursor.execute("""
                UPDATE auth_user 
                SET password = %s, email = %s, is_staff = %s, is_superuser = %s
                WHERE username = %s
            """, (hashed_password, user_data['email'], user_data['is_staff'], 
                  user_data['is_superuser'], user_data['username']))
            print(f"  ✓ 更新用户: {user_data['username']}")
        else:
            # 创建新用户
            from datetime import datetime
            hashed_password = make_password(user_data['password'])
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute("""
                INSERT INTO auth_user 
                (password, last_login, is_superuser, username, first_name, last_name, 
                 email, is_staff, is_active, date_joined)
                VALUES (%s, NULL, %s, %s, '', '', %s, %s, 1, %s)
            """, (hashed_password, user_data['is_superuser'], user_data['username'],
                  user_data['email'], user_data['is_staff'], now))
            print(f"  ✓ 创建用户: {user_data['username']} (密码: {user_data['password']})")
    
    connection.commit()
    cursor.close()
    connection.close()
    
    print("\n" + "=" * 80)
    print("  ✅ 测试用户创建完成！")
    print("=" * 80)
    print("\n👥 测试用户:")
    print("   管理员: admin_jcd / admin123")
    print("   普通用户: test_user_jcd / test123")
    print("\n🌐 访问地址:")
    print("   http://localhost:8000/jiachengda/")
    print("")
    
except Exception as e:
    print(f"\n✗ 操作失败: {str(e)}")
    import traceback
    traceback.print_exc()
