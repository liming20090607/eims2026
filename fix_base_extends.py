# -*- coding: utf-8 -*-
"""Fix base.html extends in all cost consulting templates"""
import os
import glob

base_path = r'e:\EIMS2026\eims_app\templates\cost_consulting'

# Find all HTML files
pattern = os.path.join(base_path, '**', '*.html')
templates = glob.glob(pattern, recursive=True)

print(f'Found {len(templates)} templates to update\n')

for template_path in templates:
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace extends base.html with base/base.html
    old1 = "extends 'base.html'"
    new1 = "extends 'base/base.html'"
    
    if old1 in content:
        content = content.replace(old1, new1)
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'✓ Updated: {os.path.relpath(template_path, base_path)}')
    else:
        print(f'  Skipped: {os.path.relpath(template_path, base_path)}')

print('\n✅ All templates updated!')
