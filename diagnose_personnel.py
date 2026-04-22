import pymysql
import sys
sys.path.insert(0, 'E:\\EIMS2026')

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

# Apply Python 3.14 compatibility patch
try:
    from django.utils import _os
    _os._safe_join = _os.safe_join
except Exception:
    pass

import django
django.setup()

from django.conf import settings

print('='*70)
print('检查 Personnel 表的实际结构')
print('='*70)

for db_alias in ['root_admin', 'dingce', 'shengchang', 'jiachengda']:
    db_config = settings.DATABASES.get(db_alias)
    if not db_config:
        continue
    
    print(f'\n{db_alias} ({db_config["NAME"]}):')
    try:
        conn = pymysql.connect(
            host=db_config.get('HOST', 'localhost'),
            user=db_config.get('USER', 'root'),
            password=db_config.get('PASSWORD', ''),
            database=db_config.get('NAME')
        )
        cursor = conn.cursor()
        
        # 检查 Personnel 表字段
        cursor.execute("DESCRIBE eims_app_personnel")
        columns = cursor.fetchall()
        
        print(f'  Personnel 表字段 ({len(columns)} 个):')
        has_is_deleted = False
        has_create_time = False
        has_update_time = False
        
        for col in columns:
            print(f'    - {col[0]} ({col[1]})')
            if col[0] == 'is_deleted':
                has_is_deleted = True
            elif col[0] == 'create_time':
                has_create_time = True
            elif col[0] == 'update_time':
                has_update_time = True
        
        print(f'\n  检查 BaseModel 继承字段:')
        print(f'    is_deleted: {"✓ 存在" if has_is_deleted else "✗ 不存在"}')
        print(f'    create_time: {"✓ 存在" if has_create_time else "✗ 不存在"}')
        print(f'    update_time: {"✓ 存在" if has_update_time else "✗ 不存在"}')
        
        # 测试直接查询
        cursor.execute("SELECT COUNT(*) FROM eims_app_personnel WHERE is_deleted = 0")
        count = cursor.fetchone()[0]
        print(f'  Personnel 记录数 (is_deleted=0): {count}')
        
        conn.close()
    except Exception as e:
        print(f'  错误: {e}')

print('\n' + '='*70)
print('检查 Django Personnel 模型的字段')
print('='*70)

from eims_app.models.model_personnel import Personnel
from eims_app.models.model_project_detail import ProjectDetail

personnel_fields = [f.name for f in Personnel._meta.get_fields()]
project_fields = [f.name for f in ProjectDetail._meta.get_fields()]

print(f'\nPersonnel 模型字段 ({len(personnel_fields)} 个):')
print(', '.join(personnel_fields))

print(f'\nProjectDetail 模型字段 ({len(project_fields)} 个):')
print(', '.join(project_fields))

print(f'\nPersonnel 有 is_deleted: {"is_deleted" in personnel_fields}')
print(f'ProjectDetail 有 is_deleted: {"is_deleted" in project_fields}')

# 测试 Personnel 查询
print('\n' + '='*70)
print('测试 Personnel 查询')
print('='*70)

try:
    # 不使用 using() 测试默认路由
    count = Personnel.objects.filter(is_deleted=False).count()
    print(f'Personnel.objects.filter(is_deleted=False).count() = {count}')
except Exception as e:
    print(f'默认路由查询失败: {e}')

try:
    # 使用 dingce 数据库
    count = Personnel.objects.using('dingce').filter(is_deleted=False).count()
    print(f'Personnel.objects.using("dingce").filter(is_deleted=False).count() = {count}')
except Exception as e:
    print(f'dingce 数据库查询失败: {e}')

print('\n' + '='*70)
