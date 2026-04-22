#!/usr/bin/env python
"""
修复人员数据库分配问题
将人员记录移动到正确的数据库中
"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from eims_app.models import Personnel, Tenant
from django.db import transaction

print("=" * 70)
print("修复人员数据库分配问题")
print("=" * 70)

# 获取租户信息
tenants = Tenant.objects.using('root_admin').all()
tenant_map = {t.id: t.code for t in tenants}
print(f"\n租户映射: {tenant_map}")

# 正确的数据库分配:
# tenant_id=2 (dingce) -> dingce 数据库
# tenant_id=3 (shengchang) -> shengchang 数据库
# tenant_id=4 (jiachengda) -> jiachengda 数据库

# 步骤1: 从 default 数据库读取所有人员
print("\n--- 步骤1: 分析 default 数据库中的人员 ---")
default_personnel = Personnel.objects.using('default').filter(is_deleted=False)
print(f"default 数据库总人数: {default_personnel.count()}")

# 按 tenant_id 分组
tenant_groups = {}
for p in default_personnel:
    tid = p.tenant_id
    if tid not in tenant_groups:
        tenant_groups[tid] = []
    tenant_groups[tid].append(p)

for tid, ppl in tenant_groups.items():
    tenant_code = tenant_map.get(tid, 'unknown')
    print(f"  tenant_id={tid} ({tenant_code}): {len(ppl)} 人")
    for p in ppl[:3]:
        print(f"    - {p.personnel_code}: {p.name}")

# 步骤2: 迁移人员到正确的数据库
print("\n--- 步骤2: 迁移人员 ---")

target_db_map = {
    2: 'dingce',       # 鼎策
    3: 'shengchang',   # 晟昌
    4: 'jiachengda',   # 嘉诚达
}

for tid, target_db in target_db_map.items():
    if tid not in tenant_groups:
        print(f"  tenant_id={tid}: 无数据需要迁移")
        continue
    
    personnel_to_move = tenant_groups[tid]
    print(f"\n  迁移 tenant_id={tid} 的 {len(personnel_to_move)} 人到 {target_db} 数据库:")
    
    for p in personnel_to_move:
        try:
            # 获取人员的完整数据
            p_data = {
                'tenant_id': p.tenant_id,
                'personnel_code': p.personnel_code,
                'employee': p.employee,
                'department': p.department,
                'position': p.position,
                'gender': p.gender,
                'phone': p.phone,
                'project': p.project,
                'project_code': p.project_code,
                'project2': p.project2,
                'project_code2': p.project_code2,
                'project3': p.project3,
                'project_code3': p.project_code3,
                'project4': p.project4,
                'project_code4': p.project_code4,
                'project5': p.project5,
                'project_code5': p.project_code5,
                'is_deleted': p.is_deleted,
            }
            
            # 检查目标数据库是否已存在该人员
            existing = Personnel.objects.using(target_db).filter(
                personnel_code=p.personnel_code
            ).first()
            
            if existing:
                # 更新现有记录
                for field, value in p_data.items():
                    setattr(existing, field, value)
                existing.save(using=target_db)
                print(f"    更新: {p.personnel_code} - {p.name}")
            else:
                # 创建新记录
                new_p = Personnel(**p_data)
                new_p.save(using=target_db)
                print(f"    创建: {p.personnel_code} - {p.name}")
        
        except Exception as e:
            print(f"    错误: {p.personnel_code} - {e}")
    
    # 从 default 数据库删除已迁移的记录
    codes_to_delete = [p.personnel_code for p in personnel_to_move]
    Personnel.objects.using('default').filter(
        personnel_code__in=codes_to_delete
    ).delete()
    print(f"    已从 default 数据库删除 {len(codes_to_delete)} 条记录")

print("\n--- 步骤3: 验证迁移结果 ---")
for db_name in ['default', 'dingce', 'shengchang', 'jiachengda']:
    count = Personnel.objects.using(db_name).filter(is_deleted=False).count()
    print(f"  {db_name}: {count} 人")

print("\n完成!")
