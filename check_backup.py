#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查备份文件中的数据量
"""
import json

backup_file = 'backup_local_20260406_172503.json'

print("=" * 80)
print(f"检查备份文件: {backup_file}")
print("=" * 80)

try:
    with open(backup_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"\n总记录数: {len(data)}")
    
    # 按模型统计
    models = {}
    for item in data:
        model = item.get("model", "unknown")
        models[model] = models.get(model, 0) + 1
    
    print("\n各模型记录数（按数量排序）:")
    print("-" * 80)
    for model, count in sorted(models.items(), key=lambda x: x[1], reverse=True):
        print(f"  {model:60s} : {count:5d} 条")
    
    # 特别关注合同、项目、人员
    print("\n" + "=" * 80)
    print("重点关注的模型:")
    print("=" * 80)
    key_models = [
        'eims_app.contract',
        'eims_app.projectdetail', 
        'eims_app.personnel',
        'eims_app.employee',
        'auth.user',
        'eims_app.userprofile'
    ]
    
    for model in key_models:
        count = models.get(model, 0)
        print(f"  {model:40s} : {count:5d} 条")
        
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
