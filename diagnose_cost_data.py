#!/usr/bin/env python
"""
诊断脚本 - 检查造价咨询数据状态

用于诊断：
1. 新增记录是否在统一表中
2. 编辑记录是否正确更新
3. 租户字段是否正确设置
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import CostProjectUnified, CostProjectInfo
from django.db import models


def check_unified_table():
    """检查统一表数据"""
    print("="*70)
    print("统一表 (CostProjectUnified) 数据检查")
    print("="*70)
    
    count = CostProjectUnified.objects.count()
    print(f"\n总记录数: {count}")
    
    if count == 0:
        print("\n[WARN] 统一表中没有数据！")
        return
    
    # 按租户分组
    tenant_dist = CostProjectUnified.objects.values('tenant').annotate(
        count=models.Count('id')
    )
    print(f"\n租户分布:")
    for item in tenant_dist:
        tenant_id = item['tenant']
        cnt = item['count']
        if tenant_id is None:
            print(f"  tenant=NULL: {cnt}条")
        else:
            print(f"  tenant={tenant_id}: {cnt}条")
    
    # 显示最近的5条记录
    print(f"\n最近5条记录:")
    recent = CostProjectUnified.objects.order_by('-created_at')[:5]
    for obj in recent:
        print(f"  ID={obj.id}, 编号={obj.project_code}, 名称={obj.project_name[:20]}, tenant={obj.tenant_id}")


def check_old_table():
    """检查旧表数据"""
    print("\n" + "="*70)
    print("旧表 (CostProjectInfo) 数据检查")
    print("="*70)
    
    count = CostProjectInfo.objects.count()
    print(f"\n总记录数: {count}")
    
    if count > 0:
        print(f"\n[WARN] 旧表中仍有 {count} 条记录")
        print("这些记录可能没有被迁移到统一表")
        
        # 显示最近的5条
        print(f"\n最近5条记录:")
        recent = CostProjectInfo.objects.order_by('-created_at')[:5]
        for obj in recent:
            print(f"  ID={obj.id}, 编号={obj.project_code}, 名称={obj.project_name[:20]}")


def compare_tables():
    """对比两个表的数据"""
    print("\n" + "="*70)
    print("两表数据对比")
    print("="*70)
    
    unified_codes = set(CostProjectUnified.objects.values_list('project_code', flat=True))
    old_codes = set(CostProjectInfo.objects.values_list('project_code', flat=True))
    
    print(f"\n统一表项目编号数: {len(unified_codes)}")
    print(f"旧表项目编号数: {len(old_codes)}")
    
    # 只在旧表中的
    only_in_old = old_codes - unified_codes
    if only_in_old:
        print(f"\n[WARN] 以下项目编号只在旧表中（未迁移）:")
        for code in list(only_in_old)[:10]:
            print(f"  - {code}")
        if len(only_in_old) > 10:
            print(f"  ... 还有 {len(only_in_old) - 10} 个")
    
    # 只在统一表中的
    only_in_unified = unified_codes - old_codes
    if only_in_unified:
        print(f"\n[INFO] 以下项目编号只在统一表中（新增）:")
        for code in list(only_in_unified)[:10]:
            print(f"  - {code}")
        if len(only_in_unified) > 10:
            print(f"  ... 还有 {len(only_in_unified) - 10} 个")
    
    # 两表都有的
    in_both = unified_codes & old_codes
    print(f"\n两表都有的项目编号数: {len(in_both)}")


def test_add_record():
    """测试新增记录功能"""
    print("\n" + "="*70)
    print("测试新增记录")
    print("="*70)
    
    print("\n请在浏览器中执行以下操作：")
    print("1. 访问项目信息列表页")
    print("2. 点击'新增'按钮")
    print("3. 填写表单并提交")
    print("4. 观察是否提示成功")
    print("5. 返回列表查看是否有新记录")
    
    print("\n然后重新运行此脚本检查数据")


def test_edit_record():
    """测试编辑记录功能"""
    print("\n" + "="*70)
    print("测试编辑记录")
    print("="*70)
    
    # 找一个可编辑的记录
    obj = CostProjectUnified.objects.first()
    if obj:
        print(f"\n请编辑以下记录：")
        print(f"  ID: {obj.id}")
        print(f"  编号: {obj.project_code}")
        print(f"  名称: {obj.project_name}")
        print(f"\n操作步骤：")
        print("1. 在列表中点击该记录的'编辑'")
        print("2. 修改项目名称（例如添加'测试'后缀）")
        print("3. 保存")
        print("4. 观察是否提示成功")
        print("5. 返回列表查看修改是否生效")
    else:
        print("\n[WARN] 统一表中没有记录，无法测试编辑功能")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("  造价咨询数据状态诊断")
    print("="*70)
    
    check_unified_table()
    check_old_table()
    compare_tables()
    test_add_record()
    test_edit_record()
    
    print("\n" + "="*70)
    print("诊断完成")
    print("="*70)
    print("\n如果发现问题，请检查：")
    print("1. 视图代码是否正确保存到统一表")
    print("2. tenant字段是否正确设置")
    print("3. 浏览器是否有缓存")
    print("\n")
