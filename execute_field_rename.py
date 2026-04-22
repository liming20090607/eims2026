"""
为所有数据库执行字段重命名：employee_code → personnel_code
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection, connections

def rename_field_in_db(db_alias):
    """在指定数据库中重命名字段"""
    print(f"\n📊 处理数据库: {db_alias}")
    
    try:
        with connections[db_alias].cursor() as cursor:
            table_name = 'eims_app_employee'
            
            # 检查字段是否存在
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = %s 
                AND COLUMN_NAME = 'employee_code'
            """, [table_name])
            
            has_employee_code = cursor.fetchone()[0] > 0
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = %s 
                AND COLUMN_NAME = 'personnel_code'
            """, [table_name])
            
            has_personnel_code = cursor.fetchone()[0] > 0
            
            if has_employee_code and not has_personnel_code:
                # 重命名字段
                print(f"  ✅ 重命名 employee_code → personnel_code")
                cursor.execute(f"""
                    ALTER TABLE {table_name}
                    CHANGE COLUMN employee_code personnel_code VARCHAR(50) NOT NULL
                """)
                
                # 重命名唯一索引
                old_index_name = f"{table_name}_employee_code_3f147628_uniq"
                new_index_name = f"{table_name}_personnel_code_3f147628_uniq"
                
                try:
                    cursor.execute(f"DROP INDEX {old_index_name} ON {table_name}")
                    print(f"  ✅ 删除旧索引: {old_index_name}")
                except Exception as e:
                    print(f"  ⚠️  删除索引失败（可能已删除）: {e}")
                
                try:
                    cursor.execute(f"ALTER TABLE {table_name} ADD UNIQUE INDEX {new_index_name} (personnel_code)")
                    print(f"  ✅ 添加新索引: {new_index_name}")
                except Exception as e:
                    print(f"  ⚠️  添加索引失败（可能已存在）: {e}")
                
            elif has_personnel_code:
                print(f"  ⏭️  personnel_code 字段已存在，跳过")
            else:
                print(f"  ⚠️  employee_code 字段不存在，跳过")
                
    except Exception as e:
        print(f"  ❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    print("=" * 80)
    print("在所有数据库中重命名字段：employee_code → personnel_code")
    print("=" * 80)
    
    databases = ['default', 'dingce', 'shengchang', 'jiachengda']
    
    for db_alias in databases:
        rename_field_in_db(db_alias)
    
    print("\n" + "=" * 80)
    print("✅ 完成！")
    print("=" * 80)
    print("\n下一步：")
    print("1. 执行 Django 迁移：python manage.py migrate eims_app")
    print("2. 验证数据完整性")

if __name__ == '__main__':
    main()
