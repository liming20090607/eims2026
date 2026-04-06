#!/usr/bin/env python3
"""
清理并上传部门和角色数据到服务器
"""
import json
import os

print("=" * 60)
print("清理并上传部门和角色数据")
print("=" * 60)

# 1. 清理部门数据
print("\n1. 清理部门数据...")
dept_file = 'e:\\EIMS2026\\department_data.json'
with open(dept_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 找到第一个 [ 字符的位置
start_pos = content.find('[')
if start_pos != -1:
    clean_dept = content[start_pos:]
    # 验证 JSON
    dept_data = json.loads(clean_dept)
    print(f"   ✓ 读取到 {len(dept_data)} 条部门数据")
    
    # 保存清理后的数据
    with open('e:\\EIMS2026\\department_data_clean.json', 'w', encoding='utf-8') as f:
        f.write(clean_dept)
    print(f"   ✓ 已保存到 department_data_clean.json")
else:
    print("   ✗ 未找到有效数据")
    exit(1)

# 2. 清理角色数据
print("\n2. 清理角色数据...")
role_file = 'e:\\EIMS2026\\role_data.json'
with open(role_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 找到第一个 [ 字符的位置
start_pos = content.find('[')
if start_pos != -1:
    clean_role = content[start_pos:]
    # 验证 JSON
    role_data = json.loads(clean_role)
    print(f"   ✓ 读取到 {len(role_data)} 条角色数据")
    
    # 保存清理后的数据
    with open('e:\\EIMS2026\\role_data_clean.json', 'w', encoding='utf-8') as f:
        f.write(clean_role)
    print(f"   ✓ 已保存到 role_data_clean.json")
else:
    print("   ✗ 未找到有效数据")
    exit(1)

print("\n" + "=" * 60)
print("数据清理完成！")
print("=" * 60)
print("\n下一步：运行 upload-and-restore-dept-role.bat 上传到服务器")
