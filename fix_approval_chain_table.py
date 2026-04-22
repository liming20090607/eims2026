#!/usr/bin/env python
"""修复审批链表结构 - 简单直接的方式"""
import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

import pymysql

def fix_database(db_name):
    """修复单个数据库"""
    print(f"\n{'='*60}")
    print(f"修复数据库: {db_name}")
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
            print(f"  ✗ 表不存在，跳过")
            conn.close()
            return
        
        # 获取当前列
        cursor.execute("DESCRIBE eims_app_approvalchain")
        columns = {row[0]: row[1] for row in cursor.fetchall()}
        
        print(f"  当前列: {list(columns.keys())}")
        
        # 删除旧的外键约束（如果存在）
        cursor.execute("SHOW CREATE TABLE eims_app_approvalchain")
        create_sql = cursor.fetchone()[1]
        
        constraints_to_drop = []
        if 'fk_level1_role' in create_sql:
            constraints_to_drop.append("fk_level1_role")
        if 'fk_level2_role' in create_sql:
            constraints_to_drop.append("fk_level2_role")
        if 'fk_level3_role' in create_sql:
            constraints_to_drop.append("fk_level3_role")
        
        for constraint in constraints_to_drop:
            try:
                cursor.execute(f"ALTER TABLE eims_app_approvalchain DROP FOREIGN KEY {constraint}")
                print(f"  ✓ 删除外键约束: {constraint}")
            except Exception as e:
                print(f"  - 外键约束 {constraint} 不存在或已删除")
        
        # 检查并添加缺失的部门列
        if 'level_1_department_id' not in columns:
            cursor.execute("ALTER TABLE eims_app_approvalchain ADD COLUMN level_1_department_id BIGINT NULL")
            cursor.execute("ALTER TABLE eims_app_approvalchain ADD CONSTRAINT fk_level1_dept FOREIGN KEY (level_1_department_id) REFERENCES eims_app_department(id)")
            print(f"  ✓ 添加 level_1_department_id 列及外键")
        
        if 'level_2_department_id' not in columns:
            cursor.execute("ALTER TABLE eims_app_approvalchain ADD COLUMN level_2_department_id BIGINT NULL")
            cursor.execute("ALTER TABLE eims_app_approvalchain ADD CONSTRAINT fk_level2_dept FOREIGN KEY (level_2_department_id) REFERENCES eims_app_department(id)")
            print(f"  ✓ 添加 level_2_department_id 列及外键")
        
        if 'level_3_department_id' not in columns:
            cursor.execute("ALTER TABLE eims_app_approvalchain ADD COLUMN level_3_department_id BIGINT NULL")
            cursor.execute("ALTER TABLE eims_app_approvalchain ADD CONSTRAINT fk_level3_dept FOREIGN KEY (level_3_department_id) REFERENCES eims_app_department(id)")
            print(f"  ✓ 添加 level_3_department_id 列及外键")
        
        # 处理角色列
        # 如果有 level_1_role_old (varchar)，删除它
        if 'level_1_role_old' in columns:
            cursor.execute("ALTER TABLE eims_app_approvalchain DROP COLUMN level_1_role_old")
            print(f"  ✓ 删除 level_1_role_old 列")
        
        if 'level_2_role_old' in columns:
            cursor.execute("ALTER TABLE eims_app_approvalchain DROP COLUMN level_2_role_old")
            print(f"  ✓ 删除 level_2_role_old 列")
        
        if 'level_3_role_old' in columns:
            cursor.execute("ALTER TABLE eims_app_approvalchain DROP COLUMN level_3_role_old")
            print(f"  ✓ 删除 level_3_role_old 列")
        
        # 如果角色列是 varchar，删除并重新添加为 INT
        role_cols = ['level_1_role', 'level_2_role', 'level_3_role']
        for col in role_cols:
            if col in columns and columns[col].startswith('varchar'):
                cursor.execute(f"ALTER TABLE eims_app_approvalchain DROP COLUMN {col}")
                print(f"  ✓ 删除旧的 {col} (varchar)")
        
        # 添加新的 INT 角色列
        if 'level_1_role' not in columns or columns.get('level_1_role', '').startswith('varchar'):
            cursor.execute("ALTER TABLE eims_app_approvalchain ADD COLUMN level_1_role INT NULL")
            print(f"  ✓ 添加 level_1_role (INT)")
        
        if 'level_2_role' not in columns or columns.get('level_2_role', '').startswith('varchar'):
            cursor.execute("ALTER TABLE eims_app_approvalchain ADD COLUMN level_2_role INT NULL")
            print(f"  ✓ 添加 level_2_role (INT)")
        
        if 'level_3_role' not in columns or columns.get('level_3_role', '').startswith('varchar'):
            cursor.execute("ALTER TABLE eims_app_approvalchain ADD COLUMN level_3_role INT NULL")
            print(f"  ✓ 添加 level_3_role (INT)")
        
        # 添加外键约束
        try:
            cursor.execute("ALTER TABLE eims_app_approvalchain ADD CONSTRAINT fk_level1_role FOREIGN KEY (level_1_role) REFERENCES eims_app_departmentrole(id)")
            print(f"  ✓ 添加 fk_level1_role 外键")
        except Exception as e:
            print(f"  - fk_level1_role 外键已存在: {str(e)[:50]}")
        
        try:
            cursor.execute("ALTER TABLE eims_app_approvalchain ADD CONSTRAINT fk_level2_role FOREIGN KEY (level_2_role) REFERENCES eims_app_departmentrole(id)")
            print(f"  ✓ 添加 fk_level2_role 外键")
        except Exception as e:
            print(f"  - fk_level2_role 外键已存在: {str(e)[:50]}")
        
        try:
            cursor.execute("ALTER TABLE eims_app_approvalchain ADD CONSTRAINT fk_level3_role FOREIGN KEY (level_3_role) REFERENCES eims_app_departmentrole(id)")
            print(f"  ✓ 添加 fk_level3_role 外键")
        except Exception as e:
            print(f"  - fk_level3_role 外键已存在: {str(e)[:50]}")
        
        conn.commit()
        
        # 验证最终结构
        cursor.execute("DESCRIBE eims_app_approvalchain")
        final_columns = {row[0]: row[1] for row in cursor.fetchall()}
        
        print(f"\n  最终表结构:")
        for col in ['level_1_department_id', 'level_1_role', 'level_2_department_id', 'level_2_role', 'level_3_department_id', 'level_3_role']:
            if col in final_columns:
                print(f"    ✓ {col}: {final_columns[col]}")
            else:
                print(f"    ✗ {col}: 缺失")
        
        conn.close()
        print(f"\n  ✓ 数据库 {db_name} 修复完成")
        
    except Exception as e:
        print(f"\n  ✗ 数据库 {db_name} 修复失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    databases = ['eims_dingce', 'eims_shengchang', 'eims_jiachengda', 'eims_root']
    
    print("审批链表结构修复脚本")
    print("修复角色字段为 INT 类型并添加外键约束")
    print()
    
    for db in databases:
        fix_database(db)
    
    print("\n" + "="*60)
    print("所有数据库修复完成！")
    print("="*60)
