import pymysql
import platform

print(f"当前系统: {platform.system()}")
print(f"测试本地 MySQL 连接...")
print("="*50)

passwords_to_test = ['MysqlRoot2026!', 'EIMS2026_mysql', '', 'root', '123456', 'password', 'mysql']

for pwd in passwords_to_test:
    try:
        conn = pymysql.connect(host='127.0.0.1', user='root', password=pwd, charset='utf8mb4')
        cursor = conn.cursor()
        cursor.execute('SELECT VERSION()')
        version = cursor.fetchone()
        cursor.execute('SHOW DATABASES')
        dbs = [db[0] for db in cursor.fetchall()]
        print(f'\n✅ 密码: "{pwd}" - 成功!')
        print(f'   MySQL版本: {version[0]}')
        print(f'   数据库数量: {len(dbs)}')
        eims_dbs = [db for db in dbs if 'eims' in db.lower() or 'django' in db.lower()]
        if eims_dbs:
            print(f'   EIMS/Django相关数据库:')
            for db in eims_dbs:
                print(f'     - {db}')
        conn.close()
        print(f'\n请更新 settings.py 中的 PASSWORD 为: "{pwd}"')
        break
    except Exception as e:
        print(f'❌ 密码: "{pwd}" - 失败 ({str(e)[:50]})')
