"""
更新租户项目编号前缀配置
"""
import os
import sys
import django

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Tenant
from django.db import connections

def add_column_if_not_exists():
    """如果列不存在则添加"""
    # 使用 root_admin 数据库连接（实际数据库名为 eims_root）
    with connections['root_admin'].cursor() as cursor:
        # 检查列是否存在
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'eims_root' 
            AND TABLE_NAME = 'eims_app_tenant' 
            AND COLUMN_NAME = 'project_code_prefix'
        """)
        exists = cursor.fetchone()[0]
        
        if not exists:
            print("添加 project_code_prefix 列到 eims_root.eims_app_tenant 表...")
            cursor.execute("""
                ALTER TABLE eims_root.eims_app_tenant 
                ADD COLUMN project_code_prefix VARCHAR(10) DEFAULT '' 
                COMMENT '项目编号前缀'
            """)
            print("✅ 列添加成功！")
        else:
            print("✅ 列已存在！")

def update_tenant_prefixes():
    """更新租户的项目编号前缀"""
    print("=" * 60)
    print("更新租户项目编号前缀")
    print("=" * 60)
    
    updates = [
        ('dingce', 'DC'),           # 广西鼎策工程顾问有限责任公司
        ('shengchang', 'SC'),       # 广西晟昌工程科技有限责任公司
        ('jiachengda', 'JCD'),      # 广西嘉诚达工程造价咨询有限公司
    ]
    
    for code, prefix in updates:
        try:
            tenant = Tenant.objects.using('root_admin').get(code=code)
            tenant.project_code_prefix = prefix
            tenant.save(using='root_admin')
            print(f"✅ {tenant.name}: {prefix}")
        except Tenant.DoesNotExist:
            print(f"⚠️  {code} 不存在")
    
    print("\n✅ 全部完成！")

if __name__ == '__main__':
    add_column_if_not_exists()
    update_tenant_prefixes()
