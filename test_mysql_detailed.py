import pymysql

print("测试本地 MySQL 连接...")
print("="*50)

pwd = 'MysqlRoot2026!'
try:
    print(f"尝试密码: {pwd}")
    conn = pymysql.connect(
        host='127.0.0.1', 
        port=3306,
        user='root', 
        password=pwd, 
        charset='utf8mb4',
        connect_timeout=5
    )
    cursor = conn.cursor()
    cursor.execute('SELECT VERSION()')
    version = cursor.fetchone()
    print(f"✅ 连接成功!")
    print(f"MySQL版本: {version[0]}")
    cursor.execute('SHOW DATABASES')
    dbs = [db[0] for db in cursor.fetchall()]
    print(f"数据库列表: {dbs}")
    conn.close()
except Exception as e:
    print(f"❌ 连接失败: {e}")

# 测试另一个密码
pwd2 = 'EIMS2026_mysql'
print(f"\n尝试密码: {pwd2}")
try:
    conn = pymysql.connect(
        host='127.0.0.1', 
        port=3306,
        user='root', 
        password=pwd2, 
        charset='utf8mb4',
        connect_timeout=5
    )
    print(f"✅ 连接成功!")
    conn.close()
except Exception as e:
    print(f"❌ 连接失败: {e}")
