import pymysql
import sys

# MySQL配置
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'root123',
    'charset': 'utf8mb4'
}

DB_NAME = 'eims'

try:
    # 连接到MySQL（不指定数据库）
    conn = pymysql.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    
    # 检查数据库是否存在
    cursor.execute("SHOW DATABASES LIKE %s", (DB_NAME,))
    result = cursor.fetchone()
    
    if result:
        print(f"✓ 数据库 '{DB_NAME}' 已存在")
    else:
        # 创建数据库
        cursor.execute(f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✓ 数据库 '{DB_NAME}' 创建成功")
    
    cursor.close()
    conn.close()
    
    print("✓ MySQL连接测试成功")
    sys.exit(0)
    
except Exception as e:
    print(f"✗ 错误：{e}")
    sys.exit(1)
