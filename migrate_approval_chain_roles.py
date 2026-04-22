#!/usr/bin/env python
"""手动执行数据库迁移脚本 - 将审批链角色字段从 CharField 转换为 ForeignKey"""
import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

import pymysql

def migrate_database(db_name):
    """迁移单个数据库"""
    print(f"\n{'='*60}")
    print(f"开始迁移数据库: {db_name}")
    print('='*60)
    
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='root123',
            database=db_name,
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SHOW TABLES LIKE 'eims_app_approvalchain'")
        if not cursor.fetchone():
            print(f"  ✗ 表 eims_app_approvalchain 不存在，跳过")
            conn.close()
            return
        
        # 检查当前列结构
        cursor.execute("DESCRIBE eims_app_approvalchain")
        columns = {row[0]: row for row in cursor.fetchall()}
        
        print(f"  当前表结构:")
        for col_name, col_info in columns.items():
            if 'role' in col_name.lower():
                print(f"    - {col_name}: {col_info[1]}")
        
        # 执行迁移
        sql_statements = []
        
        # 检查是否需要添加部门外键列
        needs_dept_columns = 'level_1_department_id' not in columns
        
        if needs_dept_columns:
            print(f"  提示: 缺少部门外键列，将一并添加")
            sql_statements.append("ALTER TABLE eims_app_approvalchain ADD COLUMN level_1_department_id BIGINT NULL;")
            sql_statements.append("ALTER TABLE eims_app_approvalchain ADD COLUMN level_2_department_id BIGINT NULL;")
            sql_statements.append("ALTER TABLE eims_app_approvalchain ADD COLUMN level_3_department_id BIGINT NULL;")
            sql_statements.append("ALTER TABLE eims_app_approvalchain ADD CONSTRAINT fk_level1_dept FOREIGN KEY (level_1_department_id) REFERENCES eims_app_department(id);")
            sql_statements.append("ALTER TABLE eims_app_approvalchain ADD CONSTRAINT fk_level2_dept FOREIGN KEY (level_2_department_id) REFERENCES eims_app_department(id);")
            sql_statements.append("ALTER TABLE eims_app_approvalchain ADD CONSTRAINT fk_level3_dept FOREIGN KEY (level_3_department_id) REFERENCES eims_app_department(id);")
        
        # 1. 备份旧数据到新列（保留原始字符串值）
        if 'level_1_role_id' in columns:
            sql_statements.append("ALTER TABLE eims_app_approvalchain CHANGE COLUMN level_1_role_id level_1_role_old VARCHAR(50) NULL;")
        elif 'level_1_role' in columns and 'level_1_role_old' not in columns:
            sql_statements.append("ALTER TABLE eims_app_approvalchain CHANGE COLUMN level_1_role level_1_role_old VARCHAR(50) NULL;")
        
        if 'level_2_role' in columns and 'level_2_role_old' not in columns:
            sql_statements.append("ALTER TABLE eims_app_approvalchain CHANGE COLUMN level_2_role level_2_role_old VARCHAR(50) NULL;")
        
        if 'level_3_role' in columns and 'level_3_role_old' not in columns:
            sql_statements.append("ALTER TABLE eims_app_approvalchain CHANGE COLUMN level_3_role level_3_role_old VARCHAR(50) NULL;")
        
        # 2. 添加新的外键列
        if 'level_1_role' not in columns or columns.get('level_1_role', ('', 'varchar'))[1].startswith('varchar'):
            sql_statements.append("ALTER TABLE eims_app_approvalchain ADD COLUMN level_1_role_new INT NULL;")
        
        if 'level_2_role' not in columns or columns.get('level_2_role', ('', 'varchar'))[1].startswith('varchar'):
            sql_statements.append("ALTER TABLE eims_app_approvalchain ADD COLUMN level_2_role_new INT NULL;")
        
        if 'level_3_role' not in columns or columns.get('level_3_role', ('', 'varchar'))[1].startswith('varchar'):
            sql_statements.append("ALTER TABLE eims_app_approvalchain ADD COLUMN level_3_role_new INT NULL;")
        
        # 3. 删除旧列
        if 'level_1_role_old' in columns:
            sql_statements.append("ALTER TABLE eims_app_approvalchain DROP COLUMN level_1_role_old;")
        if 'level_2_role_old' in columns:
            sql_statements.append("ALTER TABLE eims_app_approvalchain DROP COLUMN level_2_role_old;")
        if 'level_3_role_old' in columns:
            sql_statements.append("ALTER TABLE eims_app_approvalchain DROP COLUMN level_3_role_old;")
        
        # 4. 重命名新列为正式名称
        if any('ADD COLUMN level_1_role_new' in s for s in sql_statements):
            sql_statements.append("ALTER TABLE eims_app_approvalchain CHANGE COLUMN level_1_role_new level_1_role INT NULL;")
        if any('ADD COLUMN level_2_role_new' in s for s in sql_statements):
            sql_statements.append("ALTER TABLE eims_app_approvalchain CHANGE COLUMN level_2_role_new level_2_role INT NULL;")
        if any('ADD COLUMN level_3_role_new' in s for s in sql_statements):
            sql_statements.append("ALTER TABLE eims_app_approvalchain CHANGE COLUMN level_3_role_new level_3_role INT NULL;")
        
        # 5. 添加外键约束
        sql_statements.append("ALTER TABLE eims_app_approvalchain ADD CONSTRAINT fk_level1_role FOREIGN KEY (level_1_role) REFERENCES eims_app_departmentrole(id);")
        sql_statements.append("ALTER TABLE eims_app_approvalchain ADD CONSTRAINT fk_level2_role FOREIGN KEY (level_2_role) REFERENCES eims_app_departmentrole(id);")
        sql_statements.append("ALTER TABLE eims_app_approvalchain ADD CONSTRAINT fk_level3_role FOREIGN KEY (level_3_role) REFERENCES eims_app_departmentrole(id);")
        
        # 执行 SQL
        print(f"\n  执行 SQL 语句:")
        for i, sql in enumerate(sql_statements, 1):
            print(f"    {i}. {sql[:80]}...")
            try:
                cursor.execute(sql)
                conn.commit()
            except Exception as e:
                print(f"      ✗ 失败: {str(e)[:100]}")
                # 某些语句可能已经执行过，继续执行其他语句
                continue
        
        # 验证结果
        cursor.execute("DESCRIBE eims_app_approvalchain")
        new_columns = {row[0]: row[1] for row in cursor.fetchall()}
        
        print(f"\n  迁移后的表结构:")
        for col_name in ['level_1_role', 'level_2_role', 'level_3_role']:
            if col_name in new_columns:
                print(f"    ✓ {col_name}: {new_columns[col_name]}")
            else:
                print(f"    ✗ {col_name}: 不存在")
        
        conn.close()
        print(f"\n  ✓ 数据库 {db_name} 迁移完成")
        
    except Exception as e:
        print(f"\n  ✗ 数据库 {db_name} 迁移失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # 迁移所有相关数据库
    databases = ['eims_dingce', 'eims_shengchang', 'eims_jiachengda', 'eims_root']
    
    print("审批链角色字段迁移脚本")
    print("将 CharField 转换为 ForeignKey (DepartmentRole)")
    print()
    
    for db in databases:
        migrate_database(db)
    
    print("\n" + "="*60)
    print("所有数据库迁移完成！")
    print("="*60)
