# -*- coding: utf-8 -*-
"""Update remuneration distribution templates"""
import os

base_path = r'e:\EIMS2026\eims_app\templates\cost_consulting\remuneration_distribution'

# Update list.html
list_path = os.path.join(base_path, 'list.html')
with open(list_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace title and module name
content = content.replace('项目信息', '酬劳分配')
content = content.replace('project_info', 'remuneration_distribution')
content = content.replace('CostProjectInfo', 'CostRemunerationDistribution')
content = content.replace('cost_project_info_list', 'cost_remuneration_distribution_list')
content = content.replace('cost_project_info_add', 'cost_remuneration_distribution_add')
content = content.replace('cost_project_info_detail', 'cost_remuneration_distribution_detail')
content = content.replace('cost_project_info_edit', 'cost_remuneration_distribution_edit')
content = content.replace('cost_project_info_delete', 'cost_remuneration_distribution_delete')
content = content.replace('cost_project_info_batch_delete', 'cost_remuneration_distribution_batch_delete')
content = content.replace('cost_project_info_export', 'cost_remuneration_distribution_export')

# Update table headers
old_headers = """                    <th scope="col">项目编号</th>
                    <th scope="col">项目名称</th>
                    <th scope="col">项目类型</th>
                    <th scope="col">编制类别</th>
                    <th scope="col">审核类别</th>
                    <th scope="col">项目状态</th>
                    <th scope="col">建设单位</th>
                    <th scope="col">送审时间</th>
                    <th scope="col">编制金额(万元)</th>
                    <th scope="col">送审金额(万元)</th>
                    <th scope="col">审定金额(万元)</th>
                    <th scope="col">费用总额(万元)</th>
                    <th scope="col">操作</th>"""

new_headers = """                    <th scope="col">项目编号</th>
                    <th scope="col">项目名称</th>
                    <th scope="col">计算类型</th>
                    <th scope="col">计算基准</th>
                    <th scope="col">工程总造价(万元)</th>
                    <th scope="col">审减金额(万元)</th>
                    <th scope="col">酬劳总额(万元)</th>
                    <th scope="col">计算式</th>
                    <th scope="col">分配状态</th>
                    <th scope="col">操作</th>"""

content = content.replace(old_headers, new_headers)

# Update table body rows
old_rows = """                        <td>{{ obj.project_code }}</td>
                        <td>{{ obj.project_name }}</td>
                        <td>{{ obj.get_project_type_display }}</td>
                        <td>{{ obj.get_compilation_category_display }}</td>
                        <td>{{ obj.get_review_category_display }}</td>
                        <td><span class="badge bg-{% if obj.project_status == 'completed' %}success{% elif obj.project_status == 'in_progress' %}primary{% elif obj.project_status == 'suspended' %}warning{% else %}secondary{% endif %}">{{ obj.get_project_status_display }}</span></td>
                        <td>{{ obj.client_unit|default:"-" }}</td>
                        <td>{{ obj.submission_time|date:"Y-m-d"|default:"-" }}</td>
                        <td>{{ obj.compilation_amount }}</td>
                        <td>{{ obj.submission_amount }}</td>
                        <td>{{ obj.approved_amount }}</td>
                        <td>{{ obj.total_fee }}</td>"""

new_rows = """                        <td>{{ obj.project_code }}</td>
                        <td>{{ obj.project_name }}</td>
                        <td>{{ obj.get_calculation_type_display }}</td>
                        <td>{{ obj.get_calculation_base_display }}</td>
                        <td>{{ obj.total_cost }}</td>
                        <td>{{ obj.reduced_amount }}</td>
                        <td>{{ obj.total_remuneration }}</td>
                        <td>{{ obj.calculation_formula|truncatechars:30|default:"-" }}</td>
                        <td><span class="badge bg-{% if obj.distribution_status == 'confirmed' %}success{% elif obj.distribution_status == 'distributed' %}primary{% else %}warning{% endif %}">{{ obj.get_distribution_status_display }}</span></td>"""

content = content.replace(old_rows, new_rows)

# Update filter options
old_filters = """                <!-- 项目状态筛选 -->
                <div class="col-md-2">
                    <select class="form-select form-select-sm" name="project_status" onchange="this.form.submit()">
                        <option value="">全部状态</option>
                        {% for value, label in PROJECT_STATUS_CHOICES %}
                        <option value="{{ value }}" {% if project_status == value %}selected{% endif %}>{{ label }}</option>
                        {% endfor %}
                    </select>
                </div>
                <!-- 项目类型筛选 -->
                <div class="col-md-2">
                    <select class="form-select form-select-sm" name="project_type" onchange="this.form.submit()">
                        <option value="">全部类型</option>
                        {% for value, label in PROJECT_TYPE_CHOICES %}
                        <option value="{{ value }}" {% if project_type == value %}selected{% endif %}>{{ label }}</option>
                        {% endfor %}
                    </select>
                </div>"""

new_filters = """                <!-- 计算类型筛选 -->
                <div class="col-md-2">
                    <select class="form-select form-select-sm" name="calculation_type" onchange="this.form.submit()">
                        <option value="">全部类型</option>
                        {% for value, label in CALC_TYPE_CHOICES %}
                        <option value="{{ value }}" {% if calculation_type == value %}selected{% endif %}>{{ label }}</option>
                        {% endfor %}
                    </select>
                </div>
                <!-- 分配状态筛选 -->
                <div class="col-md-2">
                    <select class="form-select form-select-sm" name="distribution_status" onchange="this.form.submit()">
                        <option value="">全部状态</option>
                        {% for value, label in DISTRIBUTION_STATUS_CHOICES %}
                        <option value="{{ value }}" {% if distribution_status == value %}selected{% endif %}>{{ label }}</option>
                        {% endfor %}
                    </select>
                </div>"""

content = content.replace(old_filters, new_filters)

with open(list_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ Updated list.html')

# Update form.html
form_path = os.path.join(base_path, 'form.html')
with open(form_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('项目信息', '酬劳分配')
content = content.replace('cost_project_info_list', 'cost_remuneration_distribution_list')

with open(form_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ Updated form.html')

# Update detail.html
detail_path = os.path.join(base_path, 'detail.html')
with open(detail_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('项目信息', '酬劳分配')
content = content.replace('cost_project_info_list', 'cost_remuneration_distribution_list')
content = content.replace('cost_project_info_edit', 'cost_remuneration_distribution_edit')
content = content.replace('cost_project_info_delete', 'cost_remuneration_distribution_delete')

# Update detail fields
old_fields = """            <tr>
                <td class="detail-label">项目编号：</td>
                <td class="detail-value">{{ object.project_code }}</td>
                <td class="detail-label">项目名称：</td>
                <td class="detail-value">{{ object.project_name }}</td>
            </tr>
            <tr>
                <td class="detail-label">项目类型：</td>
                <td class="detail-value">{{ object.get_project_type_display }}</td>
                <td class="detail-label">编制类别：</td>
                <td class="detail-value">{{ object.get_compilation_category_display }}</td>
            </tr>
            <tr>
                <td class="detail-label">审核类别：</td>
                <td class="detail-value">{{ object.get_review_category_display }}</td>
                <td class="detail-label">项目状态：</td>
                <td class="detail-value"><span class="badge bg-{% if object.project_status == 'completed' %}success{% elif object.project_status == 'in_progress' %}primary{% elif object.project_status == 'suspended' %}warning{% else %}secondary{% endif %}">{{ object.get_project_status_display }}</span></td>
            </tr>
            <tr>
                <td class="detail-label">建设单位：</td>
                <td class="detail-value" colspan="3">{{ object.client_unit|default:"-" }}</td>
            </tr>
            <tr>
                <td class="detail-label">委托单位：</td>
                <td class="detail-value" colspan="3">{{ object.entrusting_unit|default:"-" }}</td>
            </tr>
            <tr>
                <td class="detail-label">联系人：</td>
                <td class="detail-value">{{ object.contact_person|default:"-" }}</td>
                <td class="detail-label">联系电话：</td>
                <td class="detail-value">{{ object.contact_phone|default:"-" }}</td>
            </tr>
            <tr>
                <td class="detail-label">送审时间：</td>
                <td class="detail-value">{{ object.submission_time|date:"Y-m-d"|default:"-" }}</td>
                <td class="detail-label">开始时间：</td>
                <td class="detail-value">{{ object.start_time|date:"Y-m-d"|default:"-" }}</td>
            </tr>
            <tr>
                <td class="detail-label">计划工期(天)：</td>
                <td class="detail-value">{{ object.planned_duration }}</td>
                <td class="detail-label">计划完成时间：</td>
                <td class="detail-value">{{ object.planned_completion_time|date:"Y-m-d"|default:"-" }}</td>
            </tr>
            <tr>
                <td class="detail-label">编制金额(万元)：</td>
                <td class="detail-value">{{ object.compilation_amount }}</td>
                <td class="detail-label">送审金额(万元)：</td>
                <td class="detail-value">{{ object.submission_amount }}</td>
            </tr>
            <tr>
                <td class="detail-label">审定金额(万元)：</td>
                <td class="detail-value">{{ object.approved_amount }}</td>
                <td class="detail-label">审减金额(万元)：</td>
                <td class="detail-value">{{ object.reduced_amount }}</td>
            </tr>
            <tr>
                <td class="detail-label">报告时间：</td>
                <td class="detail-value">{{ object.report_time|date:"Y-m-d"|default:"-" }}</td>
                <td class="detail-label">结果确认：</td>
                <td class="detail-value">{{ object.get_result_confirm_display }}</td>
            </tr>
            <tr>
                <td class="detail-label">费用总额(万元)：</td>
                <td class="detail-value">{{ object.total_fee }}</td>
                <td class="detail-label">已收费用(万元)：</td>
                <td class="detail-value">{{ object.received_fee }}</td>
            </tr>
            <tr>
                <td class="detail-label">待收费用(万元)：</td>
                <td class="detail-value">{{ object.pending_fee }}</td>
                <td class="detail-label">费用结清：</td>
                <td class="detail-value">{{ object.get_fee_settlement_display }}</td>
            </tr>"""

new_fields = """            <tr>
                <td class="detail-label">项目编号：</td>
                <td class="detail-value">{{ object.project_code }}</td>
                <td class="detail-label">项目名称：</td>
                <td class="detail-value">{{ object.project_name }}</td>
            </tr>
            <tr>
                <td class="detail-label">计算类型：</td>
                <td class="detail-value">{{ object.get_calculation_type_display }}</td>
                <td class="detail-label">计算基准：</td>
                <td class="detail-value">{{ object.get_calculation_base_display }}</td>
            </tr>
            <tr>
                <td class="detail-label">工程总造价(万元)：</td>
                <td class="detail-value">{{ object.total_cost }}</td>
                <td class="detail-label">审减金额(万元)：</td>
                <td class="detail-value">{{ object.reduced_amount }}</td>
            </tr>
            <tr>
                <td class="detail-label">酬劳总额(万元)：</td>
                <td class="detail-value">{{ object.total_remuneration }}</td>
                <td class="detail-label">分配状态：</td>
                <td class="detail-value"><span class="badge bg-{% if object.distribution_status == 'confirmed' %}success{% elif object.distribution_status == 'distributed' %}primary{% else %}warning{% endif %}">{{ object.get_distribution_status_display }}</span></td>
            </tr>
            <tr>
                <td class="detail-label">计算式：</td>
                <td class="detail-value" colspan="3">{{ object.calculation_formula|default:"-" }}</td>
            </tr>"""

content = content.replace(old_fields, new_fields)

with open(detail_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ Updated detail.html')
print('\n✅ All remuneration distribution templates updated!')
