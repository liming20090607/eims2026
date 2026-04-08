#!/usr/bin/env python
"""导出数据脚本"""
import os
import sys
import django
import json

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

# 修复 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    django.setup()
except Exception as e:
    print(f"Django 设置错误: {e}")
    sys.exit(1)

from django.core.management import call_command

print("=" * 50)
print("开始导出数据...")
print("=" * 50)

try:
    # 导出数据到 JSON 文件
    output_file = os.path.join(project_root, 'local_data.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        call_command(
            'dumpdata',
            '--natural-foreign',
            '--natural-primary',
            '--indent=2',
            stdout=f
        )
    
    # 检查文件大小
    file_size = os.path.getsize(output_file)
    file_size_mb = file_size / (1024 * 1024)
    
    print("=" * 50)
    print(f"✓ 导出成功！")
    print(f"  文件: {output_file}")
    print(f"  大小: {file_size_mb:.2f} MB")
    print("=" * 50)
    
except Exception as e:
    print("=" * 50)
    print(f"✗ 导出失败: {e}")
    print("=" * 50)
    import traceback
    traceback.print_exc()
    sys.exit(1)
