import pymysql

databases = {
    'root': 'eims_root',
    'dingce': 'eims_dingce',
    'shengchang': 'eims_shengchang',
    'jiachengda': 'eims_jiachengda',
}

print('='*70)
print('检查 Personnel 表结构')
print('='*70)

for alias, name in databases.items():
    print(f'\n{alias} ({name}):')
    try:
        conn = pymysql.connect(host='localhost', user='root', password='root123', database=name)
        cursor = conn.cursor()
        
        # 检查 Personnel 表结构
        cursor.execute("DESCRIBE eims_app_personnel")
        columns = cursor.fetchall()
        
        print(f'  Personnel 表字段:')
        for col in columns:
            print(f'    - {col[0]} ({col[1]})')
        
        # 检查是否有重复字段
        field_names = [col[0] for col in columns]
        is_deleted_count = field_names.count('is_deleted')
        create_time_count = field_names.count('create_time')
        update_time_count = field_names.count('update_time')
        
        if is_deleted_count > 1:
            print(f'  ❌ 发现 {is_deleted_count} 个 is_deleted 字段！')
        if create_time_count > 1:
            print(f'  ❌ 发现 {create_time_count} 个 create_time 字段！')
        if update_time_count > 1:
            print(f'  ❌ 发现 {update_time_count} 个 update_time 字段！')
        
        conn.close()
    except Exception as e:
        print(f'  错误: {e}')

print('\n' + '='*70)
