"""
Multi-System Initialization Script
Customizes each company system with appropriate configurations.
"""
import os
import shutil

def customize_apps_py(app_dir, app_name, company_name):
    """Update apps.py for each company system."""
    apps_file = os.path.join(app_dir, 'apps.py')
    
    with open(apps_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace app name
    content = content.replace("name = 'eims_app'", f"name = '{app_name}'")
    
    # Add company identifier
    if 'TENANT_NAME' not in content:
        # Find the class definition and add TENANT_NAME after it
        lines = content.split('\n')
        new_lines = []
        for i, line in enumerate(lines):
            new_lines.append(line)
            if line.strip().startswith('class ') and 'AppConfig' in line:
                # Add TENANT_NAME after class declaration
                indent = len(line) - len(line.lstrip())
                new_lines.append(f"{' ' * (indent + 4)}TENANT_NAME = '{company_name}'")
        
        content = '\n'.join(new_lines)
    
    with open(apps_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Updated {apps_file}")


def customize_urls_py(app_dir, app_name):
    """Update urls.py namespace for each company system."""
    urls_file = os.path.join(app_dir, 'urls.py')
    
    with open(urls_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace app_name
    content = content.replace("app_name = 'eims_app'", f"app_name = '{app_name}'")
    
    with open(urls_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Updated {urls_file}")


def update_template_company_names(template_dir, old_name, new_name):
    """Replace company names in templates."""
    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Replace company names
                    if old_name in content:
                        content = content.replace(old_name, new_name)
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"  - Updated company name in {filepath}")
                except Exception as e:
                    print(f"  ! Error processing {filepath}: {e}")


def main():
    base_dir = r'E:\EIMS2026'
    
    companies = [
        {
            'dir': 'eims_dingce',
            'app_name': 'eims_dingce',
            'company_name': '广西鼎策工程顾问有限责任公司',
            'short_name': '鼎策'
        },
        {
            'dir': 'eims_shengchang',
            'app_name': 'eims_shengchang',
            'company_name': '广西晟昌工程科技有限责任公司',
            'short_name': '晟昌'
        },
        {
            'dir': 'eims_jiachengda',
            'app_name': 'eims_jiachengda',
            'company_name': '广西嘉诚达工程造价咨询有限公司',
            'short_name': '嘉诚达'
        }
    ]
    
    print("=" * 80)
    print("开始定制公司系统配置...")
    print("=" * 80)
    
    for company in companies:
        print(f"\n处理: {company['company_name']}")
        print("-" * 80)
        
        app_dir = os.path.join(base_dir, company['dir'])
        
        # 1. Update apps.py
        customize_apps_py(app_dir, company['app_name'], company['company_name'])
        
        # 2. Update urls.py
        customize_urls_py(app_dir, company['app_name'])
        
        # 3. Update template directory structure
        old_template_dir = os.path.join(app_dir, 'templates', 'eims_app')
        new_template_dir = os.path.join(app_dir, 'templates', company['app_name'])
        
        if os.path.exists(old_template_dir) and not os.path.exists(new_template_dir):
            shutil.move(old_template_dir, new_template_dir)
            print(f"✓ Renamed template directory: eims_app -> {company['app_name']}")
        
        # 4. Update company names in templates
        template_dir = os.path.join(app_dir, 'templates', company['app_name'])
        if os.path.exists(template_dir):
            print(f"  Updating company names in templates...")
            update_template_company_names(template_dir, '协同AI办公系统', f"{company['short_name']}办公系统")
    
    print("\n" + "=" * 80)
    print("✓ 所有公司系统配置完成！")
    print("=" * 80)


if __name__ == '__main__':
    main()
