import pymysql

print("🔄 正在恢复数据库...")

# 连接并重建数据库
conn = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='mysql2026!',
    charset='utf8mb4'
)
cursor = conn.cursor()
cursor.execute('DROP DATABASE IF EXISTS eims2026_dev')
cursor.execute('CREATE DATABASE eims2026_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
conn.close()
print("✅ 数据库已重建")

# 读取并执行 SQL
with open('eims_mysql_backup_utf8.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

conn = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='mysql2026!',
    database='eims2026_dev',
    charset='utf8mb4'
)
cursor = conn.cursor()

# 分割 SQL 语句并逐条执行
statements = sql_content.split(';')
executed = 0
skipped = 0
errors = 0

for stmt in statements:
    stmt = stmt.strip()
    if not stmt or stmt.startswith('--'):
        continue
    try:
        cursor.execute(stmt)
        executed += 1
    except Exception as e:
        if 'Duplicate' in str(e) or 'already exists' in str(e):
            skipped += 1
        else:
            errors += 1
            if errors <= 5:
                print(f"⚠️ Error: {str(e)[:100]}")

conn.commit()
conn.close()

print(f"\n📊 统计:")
print(f"   ✅ 成功执行: {executed}")
print(f"   ⏭️ 跳过: {skipped}")
print(f"   ❌ 错误: {errors}")

# 验证表数量
conn = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='mysql2026!',
    database='eims2026_dev',
    charset='utf8mb4'
)
cursor = conn.cursor()
cursor.execute('SHOW TABLES')
tables = cursor.fetchall()
print(f"\n📋 数据库中的表: {len(tables)}")

# 检查关键表
key_tables = ['eims_app_costprojectunified', 'eims_app_costprojectinfo', 'eims_app_department', 'eims_app_role', 'eims_app_tenant']
for t in key_tables:
    found = any(t in str(table[0]) for table in tables)
    print(f"   {'✅' if found else '❌'} {t}")

conn.close()
print("\n✅ 数据库恢复完成！")
