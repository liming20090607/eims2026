"""重命名 ApprovalChain 表的 role 字段，添加 _id 后缀"""
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


def rename_role_columns(db_name):
    """重命名单个数据库中的 role 字段"""
    print(f"\n{'='*60}")
    print(f"重命名数据库: {db_name}")
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
        
        # 需要重命名的列（从 level_X_role 到 level_X_role_id）
        renames = [
            ('level_1_role', 'level_1_role_id'),
            ('level_2_role', 'level_2_role_id'),
            ('level_3_role', 'level_3_role_id'),
        ]
        
        # 执行重命名
        for old_name, new_name in renames:
            if old_name in column_dict and new_name not in column_dict:
                col_type = column_dict[old_name]
                print(f"\n  重命名: {old_name} -> {new_name}")
                
                # 使用 CHANGE COLUMN 重命名
                sql = f"ALTER TABLE eims_app_approvalchain CHANGE COLUMN {old_name} {new_name} {col_type}"
                try:
                    cursor.execute(sql)
                    connection.commit()
                    print(f"    ✓ 已重命名 {old_name} 为 {new_name}")
                except Exception as e:
                    print(f"    ✗ 重命名失败: {e}")
            elif new_name in column_dict:
                print(f"\n  ✓ {new_name} 已存在")
            else:
                print(f"\n  ⚠ {old_name} 不存在")
        
        # 再次获取表结构确认
        cursor.execute("DESCRIBE eims_app_approvalchain")
        columns = cursor.fetchall()
        print(f"\n  修复后的列:")
        for col in columns:
            print(f"    - {col[0]}: {col[1]}")
        
        cursor.close()
        connection.close()
        print(f"\n  ✓ 数据库 {db_name} 重命名完成")
        
    except Exception as e:
        print(f"  ✗ 连接数据库 {db_name} 失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    print("ApprovalChain 数据库字段重命名工具")
    print("将 level_X_role 重命名为 level_X_role_id")
    
    # 需要处理的数据库列表
    databases = ['dingce', 'shengchang', 'jiachengda', 'root_admin']
    
    for db_name in databases:
        rename_role_columns(db_name)
    
    print(f"\n{'='*60}")
    print("所有数据库重命名完成！")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
