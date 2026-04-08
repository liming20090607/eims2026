import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import ProjectDetail
from django.db.models import Q

print('=' * 80)
print('测试项目模糊搜索功能')
print('=' * 80)

# 测试搜索关键词
test_keywords = ['桂林', '2019', '国投', '咨询']

for keyword in test_keywords:
    print(f'\n搜索关键词: "{keyword}"')
    print('-' * 60)
    
    # 测试完整的搜索逻辑
    results = ProjectDetail.objects.filter(
        Q(project_code__icontains=keyword) |
        Q(project_name__icontains=keyword) |
        Q(project_address__icontains=keyword) |
        Q(contract_party_a__icontains=keyword) |
        Q(contract_party_b__icontains=keyword)
    )
    
    print(f'找到 {results.count()} 个项目:')
    for proj in results[:5]:  # 只显示前5个
        # 检查是哪个字段匹配的
        match_fields = []
        if keyword.lower() in (proj.project_code or '').lower():
            match_fields.append('项目编号')
        if keyword in (proj.project_name or ''):
            match_fields.append('项目名称')
        if keyword in (proj.project_address or ''):
            match_fields.append('项目地址')
        if keyword in (proj.contract_party_a or ''):
            match_fields.append('合同甲方')
        if keyword in (proj.contract_party_b or ''):
            match_fields.append('合同乙方')
        
        print(f'  ✓ {proj.project_code} - {proj.project_name[:30]}...')
        print(f'    匹配字段: {", ".join(match_fields)}')
    
    if results.count() > 5:
        print(f'  ... 还有 {results.count() - 5} 个项目')

print('\n' + '=' * 80)
print('搜索功能验证完成！')
print('=' * 80)
