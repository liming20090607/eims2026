# -*- coding: utf-8 -*-
"""Fix all cost consulting templates to use correct home URL"""
import os
import glob

base_path = r'e:\EIMS2026\eims_app\templates\cost_consulting'

# Find all HTML files
pattern = os.path.join(base_path, '**', '*.html')
templates = glob.glob(pattern, recursive=True)

print(f'Found {len(templates)} templates to check\n')

fixed_count = 0
for template_path in templates:
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace incorrect URL with correct one
    old_url = "{% url 'index' %}"
    new_url = "{% url 'eims_app:eims_index' %}"
    
    if old_url in content:
        content = content.replace(old_url, new_url)
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        rel_path = os.path.relpath(template_path, base_path)
        print(f'✓ Fixed: {rel_path}')
        fixed_count += 1
    else:
        rel_path = os.path.relpath(template_path, base_path)
        print(f'  OK: {rel_path}')

print(f'\n✅ Fixed {fixed_count} templates!')
