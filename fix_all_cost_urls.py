# -*- coding: utf-8 -*-
"""Fix all URL references in cost consulting templates to include eims_app: namespace"""
import os
import re
import glob

base_path = r'e:\EIMS2026\eims_app\templates\cost_consulting'

# Find all HTML files recursively
pattern = os.path.join(base_path, '**', '*.html')
templates = glob.glob(pattern, recursive=True)

print(f"Found {len(templates)} template files to check...\n")

fixed_count = 0
total_replacements = 0

for template_path in templates:
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern 1: {% url 'cost_xxx' %} -> {% url 'eims_app:cost_xxx' %}
    # This matches any URL tag with cost_ prefix that doesn't already have eims_app:
    pattern1 = r"{%\s*url\s+'((?!eims_app:)cost_[^']+)'(?:\s+[^%]*)?%}"
    
    def add_namespace(match):
        full_match = match.group(0)
        url_name = match.group(1)
        # Replace the URL name with namespaced version
        return full_match.replace(f"'{url_name}'", f"'eims_app:{url_name}'")
    
    content = re.sub(pattern1, add_namespace, content)
    
    # Count replacements
    if content != original_content:
        rel_path = os.path.relpath(template_path, base_path)
        # Count how many replacements were made
        replacements = len(re.findall(r"eims_app:cost_", content)) - len(re.findall(r"eims_app:cost_", original_content))
        print(f"✓ Fixed {rel_path} ({replacements} URLs)")
        fixed_count += 1
        total_replacements += replacements
        
        # Write back
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)

print(f"\n{'='*60}")
print(f"✅ Summary:")
print(f"   Templates modified: {fixed_count}")
print(f"   Total URL fixes: {total_replacements}")
print(f"{'='*60}")
