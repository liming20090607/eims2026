import pymysql

print("测试新密码: mysql2026!")
try:
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='mysql2026!',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    cursor.execute('SELECT VERSION()')
    version = cursor.fetchone()
    cursor.execute('SHOW DATABASES')
    dbs = [db[0] for db in cursor.fetchall()]
    print(f"✅ 连接成功!")
    print(f"MySQL {version[0]}")
    print(f"数据库: {dbs}")
    
    # 创建开发数据库
    cursor.execute('CREATE DATABASE IF NOT EXISTS eims2026_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
    print(f"✅ 已创建/确认数据库: eims2026_dev")
    
    conn.close()
except Exception as e:
    print(f"❌ 连接失败: {e}")
