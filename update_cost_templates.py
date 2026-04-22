"""
Script to update cost consulting sub-module templates to match project_ledger layout
"""
import os
import shutil

# Define template configurations
templates_config = {
    'task_implementation': {
        'title': '造价咨询 - 任务实施',
        'icon': 'bi-calendar-check',
        'name': '任务实施',
        'url_prefix': 'cost_task_implementation',
        'min_width': '2400px',
        'columns': 23,
    },
    'review_result': {
        'title': '造价咨询 - 审核成果',
        'icon': 'bi-file-earmark-check',
        'name': '审核成果',
        'url_prefix': 'cost_review_result',
        'min_width': '2000px',
        'columns': 18,
    },
    'payment_status': {
        'title': '造价咨询 - 收费情况',
        'icon': 'bi-cash-stack',
        'name': '收费情况',
        'url_prefix': 'cost_payment_status',
        'min_width': '1800px',
        'columns': 16,
    },
    'project_archive': {
        'title': '造价咨询 - 项目存档',
        'icon': 'bi-archive',
        'name': '项目存档',
        'url_prefix': 'cost_project_archive',
        'min_width': '2000px',
        'columns': 17,
    },
    'remuneration_distribution': {
        'title': '造价咨询 - 酬劳分配',
        'icon': 'bi-wallet2',
        'name': '酬劳分配',
        'url_prefix': 'cost_remuneration_distribution',
        'min_width': '1800px',
        'columns': 14,
    }
}

base_template_path = r'e:\EIMS2026\eims_app\templates\cost_consulting\task_plan\list.html'
target_dir = r'e:\EIMS2026\eims_app\templates\cost_consulting'

print("Starting template updates...")
print("=" * 80)

for module_name, config in templates_config.items():
    source_file = base_template_path
    target_file = os.path.join(target_dir, module_name, 'list.html')
    
    print(f"\nProcessing: {config['name']} ({module_name})")
    print(f"  Source: {source_file}")
    print(f"  Target: {target_file}")
    
    # Read the base template
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace title and breadcrumb
    content = content.replace('{% block title %}造价咨询 - 任务计划{% endblock %}', 
                             '{% block title %}' + config['title'] + '{% endblock %}')
    
    content = content.replace('<li class="breadcrumb-item active">任务计划</li>',
                             '<li class="breadcrumb-item active">' + config["name"] + '</li>')
    
    # Replace icon
    content = content.replace('<i class="bi bi-calendar-check me-2"></i>任务计划</h2>',
                             f'<i class="bi {config["icon"]} me-2"></i>{config["name"]}</h2>')
    
    # Replace URL prefixes
    old_prefix = 'cost_task_plan'
    new_prefix = config['url_prefix']
    content = content.replace(old_prefix, new_prefix)
    
    # Update table min-width
    content = content.replace('min-width: 2200px;', f"min-width: {config['min_width']};")
    
    # Write to target file
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✓ Updated successfully")

print("\n" + "=" * 80)
print("All templates updated successfully!")
print("\nNote: You may need to manually adjust:")
print("  1. Table headers (thead) to match each module's specific columns")
print("  2. Table body (tbody) data fields for each module")
print("  3. Detail panel fields to show relevant information")
print("  4. JavaScript data attributes for detail panel")
