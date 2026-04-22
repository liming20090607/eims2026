"""
Fix app_label in all models for company apps
Adds explicit app_label to Meta class in all model files
"""
import os
import re


def add_app_label_to_model(filepath, app_name):
    """Add app_label to Meta class in a model file."""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if app_label already exists
    if 'app_label' in content:
        return False
    
    # Find all class definitions that inherit from models.Model or BaseModel
    pattern = r'(class \w+\((?:models\.Model|BaseModel)\):.*?)(class Meta:)'
    
    def add_app_label(match):
        class_def = match.group(1)
        meta_keyword = match.group(2)
        
        # Extract indentation from class definition
        lines = class_def.split('\n')
        indent = '        '  # Default 8 spaces for Meta class
        
        # Add app_label after class Meta:
        replacement = f"{class_def}{meta_keyword}\n{indent}app_label = '{app_name}'"
        return replacement
    
    # Replace all occurrences
    new_content = re.sub(pattern, add_app_label, content, flags=re.DOTALL)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False


def process_app_models(app_dir, app_name):
    """Process all model files in an app."""
    models_dir = os.path.join(app_dir, 'models')
    
    if not os.path.exists(models_dir):
        print(f"⚠ Models directory not found: {models_dir}")
        return
    
    fixed_count = 0
    
    for filename in os.listdir(models_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            filepath = os.path.join(models_dir, filename)
            
            if add_app_label_to_model(filepath, app_name):
                print(f"✓ Fixed {filename}")
                fixed_count += 1
    
    return fixed_count


def main():
    base_dir = r'E:\EIMS2026'
    
    apps = [
        ('eims_dingce', '鼎策公司'),
        ('eims_shengchang', '晟昌公司'),
        ('eims_jiachengda', '嘉诚达公司'),
        ('eims_root_admin', 'Root后台'),
    ]
    
    print("="*80)
    print("修复模型 app_label...")
    print("="*80)
    
    total_fixed = 0
    
    for app_dir, description in apps:
        print(f"\n处理: {description} ({app_dir})")
        app_path = os.path.join(base_dir, app_dir)
        
        fixed = process_app_models(app_path, app_dir)
        if fixed:
            total_fixed += fixed
            print(f"  → 修复了 {fixed} 个模型文件")
    
    print("\n" + "="*80)
    print(f"✓ 完成！共修复 {total_fixed} 个模型文件")
    print("="*80)


if __name__ == '__main__':
    main()
