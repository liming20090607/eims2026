"""
批量重新编号人员脚本
根据公司前缀规则为所有现有人员重新编号
"""
import os
import sys
import django

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models.model_personnel import Personnel
from eims_app.models.model_tenant import Tenant

# 公司前缀映射
COMPANY_PREFIX_MAP = {
    'dingce': 'DCRY-',
    'shengchang': 'SCRY-',
    'jiachengda': 'JCDRY-',
}

def get_prefix_for_tenant(tenant):
    """根据租户获取人员编号前缀"""
    if not tenant:
        return 'RY-'
    
    company_code = tenant.code
    company_name = tenant.name
    
    # 优先使用公司代码匹配
    if company_code in COMPANY_PREFIX_MAP:
        return COMPANY_PREFIX_MAP[company_code]
    
    # 其次使用公司名称关键词匹配
    if '鼎策' in company_name:
        return 'DCRY-'
    elif '晟昌' in company_name:
        return 'SCRY-'
    elif '嘉诚达' in company_name:
        return 'JCDRY-'
    
    # 默认前缀
    return 'RY-'

def renumber_personnel():
    """重新编号所有人员"""
    print("=" * 80)
    print("人员编号批量更新工具")
    print("=" * 80)
    
    # 获取所有租户
    tenants = Tenant.objects.all()
    print(f"\n找到 {tenants.count()} 个公司/租户\n")
    
    total_updated = 0
    
    for tenant in tenants:
        prefix = get_prefix_for_tenant(tenant)
        print(f"处理公司: {tenant.name} (代码: {tenant.code})")
        print(f"  使用前缀: {prefix}")
        
        # 获取该公司的所有人员，按ID排序以保持相对稳定
        personnel_list = Personnel.objects.filter(
            tenant=tenant,
            is_deleted=False
        ).order_by('id')
        
        count = personnel_list.count()
        print(f"  找到 {count} 名人员")
        
        if count == 0:
            print(f"  跳过（无人员）\n")
            continue
        
        # 批量更新人员编号
        updated_count = 0
        for index, personnel in enumerate(personnel_list, start=1):
            old_code = personnel.personnel_code
            new_code = f"{prefix}{index:03d}"  # 格式：前缀 + 3位数字
            
            # 只更新确实需要改变的编号
            if old_code != new_code:
                personnel.personnel_code = new_code
                personnel.save(update_fields=['personnel_code'])
                updated_count += 1
                
                # 显示前5个和最后5个的变更详情
                if index <= 5 or index > count - 5:
                    print(f"    [{index}/{count}] {personnel.name}: {old_code} → {new_code}")
                elif index == 6 and count > 10:
                    print(f"    ... ({count - 10} 条记录省略) ...")
        
        print(f"  ✅ 已更新 {updated_count}/{count} 名人员的编号\n")
        total_updated += updated_count
    
    print("=" * 80)
    print(f"批量更新完成！共更新 {total_updated} 名人员的编号")
    print("=" * 80)
    
    # 显示统计信息
    print("\n各公司人员统计：")
    print("-" * 80)
    for tenant in tenants:
        prefix = get_prefix_for_tenant(tenant)
        count = Personnel.objects.filter(tenant=tenant, is_deleted=False).count()
        print(f"  {tenant.name:20s} | 前缀: {prefix:8s} | 人员数: {count}")
    print("-" * 80)

if __name__ == '__main__':
    try:
        # 确认操作
        print("\n⚠️  警告：此操作将修改所有现有人员的编号！")
        print("建议先备份数据库后再执行。\n")
        
        confirm = input("是否继续？(yes/no): ")
        if confirm.lower() != 'yes':
            print("操作已取消")
            sys.exit(0)
        
        renumber_personnel()
        
    except KeyboardInterrupt:
        print("\n\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
