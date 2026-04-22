"""
检查 Django 模板渲染问题
验证 show_detail 变量是否正确传递
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, r'e:\EIMS2026')
django.setup()

from django.template import Template, Context
from eims_app.models import CostReviewResult, Tenant
from django.contrib.auth import get_user_model

User = get_user_model()

def check_template_issue():
    print("=" * 80)
    print("检查审核成果列表页面的模板渲染")
    print("=" * 80)
    
    # 读取模板文件
    template_path = r'e:\EIMS2026\eims_app\templates\cost_consulting\review_result\list.html'
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找 show_detail 的使用
    print("\n1. 检查 show_detail 变量使用:")
    if '{{ show_detail|default:"false"|yesno:"true,false" }}' in content:
        print("   ✅ 已修复：使用了 default 过滤器")
    elif '{{ show_detail|yesno:"true,false" }}' in content:
        print("   ❌ 未修复：缺少 default 过滤器")
    else:
        print("   ⚠️  未找到 show_detail 变量")
    
    # 检查 handleSort 函数定义
    print("\n2. 检查 handleSort 函数:")
    if 'function handleSort(field, event)' in content:
        print("   ✅ handleSort 函数已定义")
    else:
        print("   ❌ handleSort 函数未找到")
    
    # 检查表头 onclick 属性
    print("\n3. 检查表头 onclick 属性:")
    import re
    onclick_pattern = r'onclick="handleSort\([^)]+\)"'
    onclicks = re.findall(onclick_pattern, content)
    print(f"   找到 {len(onclicks)} 个 onclick 属性")
    
    # 检查是否有错误的格式
    wrong_pattern = r'onclick="handleSort\(\'[^\']+\'\)"'
    wrong_onclicks = re.findall(wrong_pattern, content)
    if wrong_onclicks:
        print(f"   ❌ 找到 {len(wrong_onclicks)} 个缺少 event 参数的 onclick")
    else:
        print("   ✅ 所有 onclick 都包含 event 参数")
    
    print("\n4. 检查其他可能的语法错误:")
    # 查找可能的模板语法问题
    problem_patterns = [
        (r'\{\{[^}]+\}\}\s*[;<>\+\-\*\/\(\)\{\}]', 'Django变量后直接跟特殊字符'),
        (r'var\s+\w+\s*=\s*\{\{[^}]+\}\}\s*;', '模板变量赋值缺少引号'),
    ]
    
    for pattern, desc in problem_patterns:
        matches = re.findall(pattern, content)
        if matches:
            print(f"   ⚠️  发现潜在问题：{desc} ({len(matches)}处)")
    
    print("\n" + "=" * 80)
    print("建议操作:")
    print("1. 重启 Django 服务器（必须！）")
    print("2. 清除浏览器缓存（Ctrl + Shift + R）")
    print("3. 检查控制台是否还有错误")
    print("=" * 80)

if __name__ == "__main__":
    check_template_issue()
