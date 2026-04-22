"""
Fix Admin Registration Conflicts
Removes duplicate admin registrations from company apps to avoid AlreadyRegistered errors.
Only eims_root_admin should have full admin access.
Company apps will use simplified admin or no admin at all.
"""
import os


def fix_admin_py(app_dir, app_name):
    """Modify admin.py to prevent duplicate registrations."""
    admin_file = os.path.join(app_dir, 'admin.py')
    
    if not os.path.exists(admin_file):
        print(f"⚠ {admin_file} does not exist")
        return
    
    with open(admin_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # For company apps (not root admin), comment out all @admin.register decorators
    if app_name != 'eims_root_admin':
        # Replace all @admin.register lines with commented versions
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            if line.strip().startswith('@admin.register('):
                # Comment out the decorator
                new_lines.append(f'# {line}  # Disabled in company app - managed by root admin')
            else:
                new_lines.append(line)
        
        content = '\n'.join(new_lines)
        
        # Add a note at the top
        header = f"""# NOTE: Admin registrations disabled for {app_name}
# This is a company-specific instance.
# All admin management is handled by eims_root_admin.
# Uncomment these registrations only if you need local admin for this company.

"""
        content = header + content
    
    with open(admin_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Fixed {admin_file}")


def main():
    base_dir = r'E:\EIMS2026'
    
    apps = [
        ('eims_dingce', '鼎策公司'),
        ('eims_shengchang', '晟昌公司'),
        ('eims_jiachengda', '嘉诚达公司'),
        ('eims_root_admin', 'Root后台（保持不变）'),
    ]
    
    print("="*80)
    print("修复 Admin 注册冲突...")
    print("="*80)
    
    for app_dir, description in apps:
        print(f"\n处理: {description} ({app_dir})")
        app_path = os.path.join(base_dir, app_dir)
        fix_admin_py(app_path, app_dir)
    
    print("\n" + "="*80)
    print("✓ Admin 注册冲突已修复！")
    print("="*80)
    print("\n说明:")
    print("- 三个公司应用的 admin 注册已被注释掉")
    print("- Root 后台管理应用保持完整 admin 功能")
    print("- 如需在公司应用中启用本地 admin，可手动取消注释")
    print("="*80)


if __name__ == '__main__':
    main()
