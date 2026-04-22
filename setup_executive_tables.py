"""
在所有公司数据库中创建 CompanyExecutiveRole 表
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

import pymysql
from django.conf import settings

def create_table_in_database(db_config, db_name):
    """在指定数据库中创建 CompanyExecutiveRole 表"""
    
    print(f"\n{'='*80}")
    print(f"处理数据库: {db_name}")
    print(f"{'='*80}")
    
    try:
        connection = pymysql.connect(
            host=db_config['HOST'],
            user=db_config['USER'],
            password=db_config['PASSWORD'],
            database=db_name,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 检查表是否已存在
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = %s 
                AND table_name = 'eims_app_companyexecutiverole'
            """, (db_name,))
            
            table_exists = cursor.fetchone()[0] > 0
            
            if table_exists:
                print(f"✓ 表 eims_app_companyexecutiverole 已存在")
                
                # 检查是否有 tenant_id 字段
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.columns 
                    WHERE table_schema = %s 
                    AND table_name = 'eims_app_companyexecutiverole'
                    AND column_name = 'tenant_id'
                """, (db_name,))
                
                has_tenant_field = cursor.fetchone()[0] > 0
                
                if not has_tenant_field:
                    print("  添加 tenant_id 字段...")
                    cursor.execute("""
                        ALTER TABLE eims_app_companyexecutiverole 
                        ADD COLUMN tenant_id INT NULL AFTER update_time,
                        ADD INDEX idx_tenant (tenant_id)
                    """)
                    print("  ✓ tenant_id 字段添加成功")
                else:
                    print("  ✓ tenant_id 字段已存在")
            else:
                print("创建表 eims_app_companyexecutiverole...")
                cursor.execute("""
                    CREATE TABLE eims_app_companyexecutiverole (
                        id BIGINT AUTO_INCREMENT PRIMARY KEY,
                        is_deleted TINYINT(1) NOT NULL DEFAULT 0,
                        create_time DATETIME(6) NOT NULL,
                        update_time DATETIME(6) NOT NULL,
                        tenant_id INT NULL,
                        executive_type VARCHAR(30) NOT NULL,
                        role_name VARCHAR(50) NOT NULL,
                        is_primary TINYINT(1) NOT NULL DEFAULT 1,
                        description LONGTEXT,
                        approval_authority LONGTEXT,
                        `order` INT NOT NULL DEFAULT 0,
                        user_id INT NOT NULL,
                        UNIQUE KEY unique_user_executive (user_id, executive_type),
                        INDEX idx_tenant (tenant_id),
                        INDEX idx_executive_type (executive_type),
                        INDEX idx_is_primary (is_primary),
                        INDEX idx_create_time (create_time)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                print("✓ 表创建成功")
            
            connection.commit()
            print(f"✓ {db_name} 数据库处理完成")
            
    except Exception as e:
        print(f"✗ {db_name} 数据库处理失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'connection' in locals():
            connection.close()

def main():
    """主函数：在所有公司数据库中创建表"""
    
    print("=" * 80)
    print("在所有公司数据库中创建 CompanyExecutiveRole 表")
    print("=" * 80)
    
    # 需要处理的公司数据库
    company_databases = ['eims_dingce', 'eims_shengchang', 'eims_jiachengda']
    
    # 获取数据库配置（使用 root_admin 的配置，因为所有数据库在同一服务器）
    db_config = settings.DATABASES['root_admin']
    
    success_count = 0
    fail_count = 0
    
    for db_name in company_databases:
        try:
            create_table_in_database(db_config, db_name)
            success_count += 1
        except Exception as e:
            print(f"✗ {db_name} 处理失败: {e}")
            fail_count += 1
    
    print("\n" + "=" * 80)
    print("处理完成！")
    print(f"  成功: {success_count} 个数据库")
    print(f"  失败: {fail_count} 个数据库")
    print("=" * 80)
    
    if fail_count == 0:
        print("\n✅ 所有数据库表创建成功！")
        print("\n现在可以：")
        print("1. 访问各公司的 Admin 后台配置高管角色")
        print("   - 鼎策: http://127.0.0.1:8000/dingce/admin/")
        print("   - 晟昌: http://127.0.0.1:8000/shengchang/admin/")
        print("   - 嘉诚达: http://127.0.0.1:8000/jiachengda/admin/")
        print("\n2. 在对应公司的 Admin 中找到 '公司高管角色配置' 进行设置")

if __name__ == '__main__':
    main()
