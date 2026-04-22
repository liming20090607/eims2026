#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查备份归档的文件结构
"""
import tarfile
import os

backup_file = "backup/EIMS2026_backup_20260421_073419.tar.gz"

print("检查备份归档内容...")
print("归档文件: {}".format(backup_file))
print("文件大小: {:.2f} MB".format(os.path.getsize(backup_file) / 1024 / 1024))

try:
    with tarfile.open(backup_file, 'r:gz') as tar:
        # 获取所有文件名
        members = tar.getnames()
        
        print("\n总文件数: {}".format(len(members)))
        
        # 检查requirements.txt
        req_files = [m for m in members if 'requirements' in m.lower()]
        print("\nrequirements文件:")
        for f in req_files:
            print("  - {}".format(f))
        
        # 检查顶层目录结构
        print("\n顶层目录/文件:")
        top_level = set()
        for m in members:
            parts = m.split('/')
            if parts[0]:
                top_level.add(parts[0])
        
        for item in sorted(top_level):
            print("  - {}".format(item))
        
        # 检查是否有manage.py
        manage_files = [m for m in members if 'manage.py' in m]
        print("\nmanage.py位置:")
        for f in manage_files[:5]:
            print("  - {}".format(f))

except Exception as e:
    print("错误: {}".format(str(e)))
    import traceback
    traceback.print_exc()
