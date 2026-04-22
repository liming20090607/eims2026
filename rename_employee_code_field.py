"""
自定义迁移：重命名 employee_code 为 personnel_code
保留现有数据
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection

def rename_field_in_database():
    """直接在数据库中重命名字段"""
    databases = ['default', 'dingce', 'shengchang', 'jiachengda']
    
    print("=" * 80)
    print("开始重命名字段：employee_code → personnel_code")
    print("=" * 80)
    
    for db_name in databases:
        try:
            print(f"\n📊 处理数据库: {db_name}")
            
            with connection.cursor() as cursor:
                # 使用 eims_app_employee 表（Employee 模型对应的表名）
                table_name = 'eims_app_employee'
                
                # 检查字段是否存在
                cursor.execute(f"""
                    SELECT COUNT(*) 
                    FROM information_schema.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = '{table_name}' 
                    AND COLUMN_NAME = 'employee_code'
                """)
                
                has_employee_code = cursor.fetchone()[0] > 0
                has_personnel_code = cursor.execute(f"""
                    SELECT COUNT(*) 
                    FROM information_schema.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = '{table_name}' 
                    AND COLUMN_NAME = 'personnel_code'
                """)
                
                if has_employee_code and not has_personnel_code:
                    # 重命名字段
                    print(f"  ✅ 重命名 employee_code → personnel_code")
                    cursor.execute(f"""
                        ALTER TABLE {table_name}
                        CHANGE COLUMN employee_code personnel_code VARCHAR(50) NOT NULL
                    """)
                    
                    # 重命名唯一索引
                    cursor.execute(f"""
                        ALTER TABLE {table_name}
                        DROP INDEX {table_name}_employee_code_3f147628_uniq
                    """)
                    cursor.execute(f"""
                        ALTER TABLE {table_name}
                        ADD UNIQUE INDEX {table_name}_personnel_code_3f147628_uniq (personnel_code)
                    """)
                    
                elif has_personnel_code:
                    print(f"  ⏭️  personnel_code 字段已存在，跳过")
                else:
                    print(f"  ⚠️  employee_code 字段不存在，跳过")
                    
        except Exception as e:
            print(f"  ❌ 错误: {str(e)}")
    
    print("\n" + "=" * 80)
    print("✅ 完成！")
    print("=" * 80)

if __name__ == '__main__':
    rename_field_in_database()
