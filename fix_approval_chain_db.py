"""检查和修复 ApprovalChain 表的数据库结构"""
import os
import sys

# 确保项目路径正确
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 配置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

import django
django.setup()

from django.conf import settings
import pymysql


def check_and_fix_table(db_name):
    """检查并修复单个数据库中的 ApprovalChain 表"""
    print(f"\n{'='*60}")
    print(f"检查数据库: {db_name}")
    print(f"{'='*60}")
    
    # 获取数据库配置
    db_config = settings.DATABASES.get(db_name, {})
    if not db_config:
        print(f"   数据库 {db_name} 未配置，跳过")
        return
    
    try:
        # 连接数据库
        connection = pymysql.connect(
            host=db_config.get('HOST', '127.0.0.1'),
            port=int(db_config.get('PORT', 3306)),
            user=db_config.get('USER', 'root'),
            password=db_config.get('PASSWORD', ''),
            database=db_config.get('NAME', ''),
            charset='utf8mb4'
        )
        cursor = connection.cursor()
        
        # 获取表结构
        cursor.execute("DESCRIBE eims_app_approvalchain")
        columns = cursor.fetchall()
        column_dict = {col[0]: col[1] for col in columns}
        
        print(f"\n  当前列:")
        for col in columns:
            print(f"    - {col[0]}: {col[1]}")
        
        # 检查需要的列
        required_columns = {
            'level_1_department_id': 'bigint',
            'level_1_role_id': 'int',
            'level_2_department_id': 'bigint',
            'level_2_role_id': 'int',
            'level_3_department_id': 'bigint',
            'level_3_role_id': 'int',
        }
        
        # 检查并添加缺失的列
        for col_name, col_type in required_columns.items():
            if col_name not in column_dict:
                print(f"\n  ⚠ 缺少列: {col_name}")
                # 根据列名判断是部门还是角色
                if 'department' in col_name:
                    ref_table = 'eims_app_department'
                else:
                    ref_table = 'eims_app_departmentrole'
                
                # 添加列和外键
                sql = f"ALTER TABLE eims_app_approvalchain ADD COLUMN {col_name} INT NULL, ADD CONSTRAINT fk_{col_name} FOREIGN KEY ({col_name}) REFERENCES {ref_table}(id)"
                try:
                    cursor.execute(sql)
                    connection.commit()
                    print(f"    ✓ 已添加列 {col_name} 及外键")
                except Exception as e:
                    print(f"    ✗ 添加列失败: {e}")
            else:
                print(f"\n  ✓ 列 {col_name} 已存在: {column_dict[col_name]}")
        
        cursor.close()
        connection.close()
        print(f"\n  ✓ 数据库 {db_name} 检查完成")
        
    except Exception as e:
        print(f"  ✗ 连接数据库 {db_name} 失败: {e}")


def main():
    """主函数"""
    print("ApprovalChain 数据库表结构检查和修复工具")
    
    # 需要检查的数据库列表
    databases = ['dingce', 'shengchang', 'jiachengda', 'root_admin']
    
    for db_name in databases:
        check_and_fix_table(db_name)
    
    print(f"\n{'='*60}")
    print("所有数据库检查完成！")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
