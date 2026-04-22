"""
数据库启动前验证脚本
确保系统使用MySQL，防止误用SQLite
"""
import os
import sys
import pymysql

def validate_mysql_connection():
    """验证MySQL连接是否正常"""
    print("=" * 60)
    print("🔍 数据库配置验证")
    print("=" * 60)
    
    # 1. 检查settings.py中的数据库配置
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
    
    import django
    django.setup()
    
    from django.conf import settings
    
    # 2. 验证所有数据库配置都使用MySQL
    databases = settings.DATABASES
    print("\n📊 检测到的数据库配置:")
    
    sqlite_found = False
    mysql_count = 0
    
    for db_name, db_config in databases.items():
        engine = db_config.get('ENGINE', '')
        if 'sqlite' in engine.lower():
            print(f"   ❌ {db_name}: 使用了SQLite (ENGINE={engine})")
            sqlite_found = True
        elif 'mysql' in engine.lower():
            mysql_count += 1
            print(f"   ✅ {db_name}: 使用MySQL ({db_config.get('HOST')}:{db_config.get('PORT')}/{db_config.get('NAME')})")
        else:
            print(f"   ⚠️  {db_name}: 未知数据库引擎 (ENGINE={engine})")
    
    # 3. 检查是否存在db.sqlite3文件
    sqlite_file = os.path.join(settings.BASE_DIR, 'db.sqlite3')
    if os.path.exists(sqlite_file):
        print(f"\n⚠️  发现SQLite文件: {sqlite_file}")
        print("   建议删除以避免误用: python manage.py delete_sqlite_file")
    else:
        print(f"\n✅ 未发现SQLite文件")
    
    # 4. 测试MySQL连接
    print("\n🔌 测试MySQL连接:")
    try:
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='root123',
            charset='utf8mb4'
        )
        cursor = connection.cursor()
        cursor.execute('SELECT VERSION()')
        version = cursor.fetchone()
        print(f"   ✅ MySQL连接成功 (版本: {version[0]})")
        
        # 检查项目数据库是否存在
        cursor.execute('SHOW DATABASES')
        databases_list = [db[0] for db in cursor.fetchall()]
        
        required_dbs = ['eims_dingce', 'eims_shengchang', 'eims_jiachengda', 'eims_root']
        print(f"\n📁 检查项目数据库:")
        for db in required_dbs:
            if db in databases_list:
                print(f"   ✅ {db}: 已存在")
            else:
                print(f"   ❌ {db}: 不存在（需要创建）")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"   ❌ MySQL连接失败: {str(e)}")
        print("\n💡 解决方案:")
        print("   1. 确保MySQL服务已启动")
        print("   2. 检查用户名和密码是否正确")
        print("   3. 运行: python manage.py check_mysql")
        return False
    
    # 5. 总结
    print("\n" + "=" * 60)
    if sqlite_found:
        print("❌ 验证失败: 发现SQLite配置，请修正后重新启动")
        return False
    elif mysql_count == 0:
        print("❌ 验证失败: 未找到MySQL配置")
        return False
    else:
        print(f"✅ 验证通过: 所有{mysql_count}个数据库均使用MySQL")
        print("=" * 60)
        return True

if __name__ == '__main__':
    success = validate_mysql_connection()
    sys.exit(0 if success else 1)
