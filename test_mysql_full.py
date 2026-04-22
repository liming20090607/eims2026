import pymysql

print("="*60)
print("全面检查本地 MySQL 配置")
print("="*60)

test_passwords = ['', 'root', '123456', 'password', 'MysqlRoot2026!', 'EIMS2026_mysql', 'mysql', 'admin', 'Admin@123', 'test']

for host in ['localhost', '127.0.0.1']:
    print(f"\n尝试连接 {host}:")
    for pwd in test_passwords:
        try:
            conn = pymysql.connect(host=host, port=3306, user='root', password=pwd, charset='utf8mb4', connect_timeout=3)
            cursor = conn.cursor()
            cursor.execute('SELECT VERSION()')
            version = cursor.fetchone()
            cursor.execute('SHOW DATABASES')
            dbs = [db[0] for db in cursor.fetchall()]
            print(f"  ✅ 密码 '{pwd}' - 成功!")
            print(f"     MySQL {version[0]}, 数据库: {dbs}")
            conn.close()
            print("\n✅ 找到正确密码，程序退出")
            exit(0)
        except Exception as e:
            error_msg = str(e)
            if '1045' in error_msg:
                pass
            else:
                print(f"  ❌ 密码 '{pwd}' - {error_msg[:80]}")

print("\n❌ 所有密码都失败了")
print("\n建议：使用 mysqladmin 重置 root 密码")
print("命令: mysqladmin -u root password '123456'")
