"""手动添加 CompanyExecutiveRole 相关字段到 ApprovalChain 表"""
import os
import django
import pymysql

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.conf import settings

def add_executive_fields():
    """添加 executive 外键字段"""
    
    # 获取 root_admin 数据库配置
    db_config = settings.DATABASES['root_admin']
    
    # 连接数据库
    connection = pymysql.connect(
        host=db_config['HOST'],
        user=db_config['USER'],
        password=db_config['PASSWORD'],
        database=db_config['NAME'],
        charset='utf8mb4'
    )
    
    try:
        with connection.cursor() as cursor:
            print("=" * 80)
            print("开始添加 CompanyExecutiveRole 相关字段...")
            print("=" * 80)
            
            # 1. 检查并添加 level_1_executive_id
            cursor.execute("SHOW COLUMNS FROM eims_app_approvalchain LIKE 'level_1_executive_id'")
            if not cursor.fetchone():
                print("添加 level_1_executive_id 字段...")
                cursor.execute("""
                    ALTER TABLE eims_app_approvalchain 
                    ADD COLUMN level_1_executive_id INT NULL,
                    ADD CONSTRAINT fk_level1_executive 
                    FOREIGN KEY (level_1_executive_id) REFERENCES eims_app_companyexecutiverole(id)
                """)
                print("✓ level_1_executive_id 添加成功")
            else:
                print("⊙ level_1_executive_id 已存在")
            
            # 2. 检查并添加 level_2_executive_id
            cursor.execute("SHOW COLUMNS FROM eims_app_approvalchain LIKE 'level_2_executive_id'")
            if not cursor.fetchone():
                print("添加 level_2_executive_id 字段...")
                cursor.execute("""
                    ALTER TABLE eims_app_approvalchain 
                    ADD COLUMN level_2_executive_id INT NULL,
                    ADD CONSTRAINT fk_level2_executive 
                    FOREIGN KEY (level_2_executive_id) REFERENCES eims_app_companyexecutiverole(id)
                """)
                print("✓ level_2_executive_id 添加成功")
            else:
                print("⊙ level_2_executive_id 已存在")
            
            # 3. 检查并添加 level_3_executive_id
            cursor.execute("SHOW COLUMNS FROM eims_app_approvalchain LIKE 'level_3_executive_id'")
            if not cursor.fetchone():
                print("添加 level_3_executive_id 字段...")
                cursor.execute("""
                    ALTER TABLE eims_app_approvalchain 
                    ADD COLUMN level_3_executive_id INT NULL,
                    ADD CONSTRAINT fk_level3_executive 
                    FOREIGN KEY (level_3_executive_id) REFERENCES eims_app_companyexecutiverole(id)
                """)
                print("✓ level_3_executive_id 添加成功")
            else:
                print("⊙ level_3_executive_id 已存在")
            
            connection.commit()
            
            print("=" * 80)
            print("所有字段添加完成！")
            print("=" * 80)
            
            # 验证表结构
            cursor.execute("DESCRIBE eims_app_approvalchain")
            columns = cursor.fetchall()
            print("\n当前 ApprovalChain 表结构:")
            print("-" * 80)
            for col in columns:
                if 'executive' in col[0] or 'approver_type' in col[0]:
                    print(f"  {col[0]:<30} {col[1]:<20}")
            
    except Exception as e:
        print(f"错误: {e}")
        connection.rollback()
        raise
    finally:
        connection.close()

if __name__ == '__main__':
    add_executive_fields()
