"""
Add explicit label to all company AppConfigs
"""
import os
import re


def add_label_to_appconfig(app_dir):
    """Add explicit label attribute to AppConfig."""
    apps_file = os.path.join(app_dir, 'apps.py')
    
    with open(apps_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if label already exists
    if 'label =' in content:
        print(f"⊘ {app_dir} already has label")
        return
    
    # Add label after name = line
    app_name = os.path.basename(app_dir)
    content = re.sub(
        r"(name = '[^']+')",
        f"\\1\n    label = '{app_name}'  # Explicit unique label",
        content
    )
    
    with open(apps_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Added label to {app_dir}")


def main():
    base_dir = r'E:\EIMS2026'
    
    apps = ['eims_shengchang', 'eims_jiachengda', 'eims_root_admin']
    
    print("Adding explicit labels to AppConfig...")
    for app in apps:
        add_label_to_appconfig(os.path.join(base_dir, app))
    
    print("\n✓ Done!")


if __name__ == '__main__':
    main()
