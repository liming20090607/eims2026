"""
URL配置验证脚本 - 防止命名空间错误
"""
import os
import django
from django.urls import reverse, NoReverseMatch

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EIMS.settings')
django.setup()

def validate_namespace():
    """验证命名空间是否正确注册"""
    print("=" * 50)
    print("URL命名空间验证工具")
    print("=" * 50)
    
    # 测试关键URL
    test_urls = [
        ('projects:eims_index', '首页'),
        ('projects:contract_list', '合同列表'),
        ('projects:project_list', '项目列表'),
    ]
    
    success = True
    for url_name, description in test_urls:
        try:
            url = reverse(url_name)
            print(f"✅ [{url_name}] {description} - 解析成功: {url}")
        except NoReverseMatch as e:
            print(f"❌ [{url_name}] {description} - 解析失败: {str(e)}")
            success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 所有命名空间验证通过！系统可以正常运行。")
    else:
        print("🚨 发现命名空间问题！请检查根URL配置。")
    
    return success

if __name__ == "__main__":
    validate_namespace()