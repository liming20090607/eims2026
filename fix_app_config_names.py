"""
Fix AppConfig class names for all company apps
"""
import os


def fix_apps_py(app_dir, app_name, chinese_name):
    """Fix the AppConfig in a company app."""
    apps_file = os.path.join(app_dir, 'apps.py')
    
    if not os.path.exists(apps_file):
        print(f"⚠ {apps_file} not found")
        return
    
    # Generate proper class name from app_name
    # eims_dingce -> EimsDingceConfig
    parts = app_name.split('_')
    class_name = ''.join(part.capitalize() for part in parts) + 'Config'
    
    with open(apps_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace class name
    import re
    content = re.sub(r'class \w+\(AppConfig\):', f'class {class_name}(AppConfig):', content)
    
    # Update verbose_name
    content = re.sub(r"verbose_name = '[^']*'", f"verbose_name = '{chinese_name}'", content)
    
    # Simplify ready() method
    content = re.sub(
        r'def ready\(self\):.*?(?=\n\S|\Z)',
        'def ready(self):\n        pass\n',
        content,
        flags=re.DOTALL
    )
    
    with open(apps_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Fixed {app_dir}/apps.py - Class: {class_name}")


def main():
    base_dir = r'E:\EIMS2026'
    
    apps = [
        ('eims_shengchang', '晟昌公司系统'),
        ('eims_jiachengda', '嘉诚达公司系统'),
        ('eims_root_admin', '超级管理员后台'),
    ]
    
    print("="*80)
    print("修复 AppConfig 类名...")
    print("="*80)
    
    for app_dir, chinese_name in apps:
        app_path = os.path.join(base_dir, app_dir)
        fix_apps_py(app_path, app_dir, chinese_name)
    
    print("\n✓ 完成！")


if __name__ == '__main__':
    main()
