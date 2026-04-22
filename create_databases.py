"""
Create Multi-System Databases
Creates 4 independent databases for the multi-system architecture.
"""
import pymysql


def create_databases():
    """Create all required databases."""
    
    # MySQL connection parameters
    connection_params = {
        'host': 'localhost',
        'user': 'root',
        'password': 'root123',
        'charset': 'utf8mb4'
    }
    
    databases = [
        'eims_dingce',
        'eims_shengchang',
        'eims_jiachengda',
        'eims_root'
    ]
    
    print("="*80)
    print("创建多系统数据库...")
    print("="*80)
    
    try:
        # Connect to MySQL (without specifying database)
        connection = pymysql.connect(**connection_params)
        cursor = connection.cursor()
        
        print("\n✓ 成功连接到MySQL服务器")
        
        # Create each database
        for db_name in databases:
            try:
                sql = f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                cursor.execute(sql)
                print(f"✓ 数据库 '{db_name}' 创建成功")
            except Exception as e:
                print(f"✗ 数据库 '{db_name}' 创建失败: {e}")
        
        # Show all eims databases
        cursor.execute("SHOW DATABASES LIKE 'eims_%'")
        results = cursor.fetchall()
        
        print("\n" + "="*80)
        print("已创建的数据库:")
        print("="*80)
        for row in results:
            print(f"  - {row[0]}")
        
        cursor.close()
        connection.close()
        
        print("\n" + "="*80)
        print("✓ 所有数据库创建完成！")
        print("="*80)
        print("\n下一步:")
        print("1. 执行数据库迁移: python run_multi_system_migrations.py")
        print("2. 创建超级管理员: python manage.py createsuperuser --database=root_admin")
        print("3. 启动服务器: python manage.py runserver")
        print("="*80)
        
        return True
        
    except pymysql.err.OperationalError as e:
        print(f"\n✗ MySQL连接失败: {e}")
        print("\n请检查:")
        print("1. MySQL服务是否正在运行")
        print("2. 用户名和密码是否正确 (当前: root/root123)")
        print("3. MySQL是否允许本地连接")
        return False
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        return False


if __name__ == '__main__':
    import sys
    success = create_databases()
    sys.exit(0 if success else 1)
