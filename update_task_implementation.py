# -*- coding: utf-8 -*-
"""批量更新造价咨询子模块模板的表格内容"""

# 任务实施
task_implementation_content = """                <thead>
                    <tr>
                        <th width="40"><input type="checkbox" id="selectAll"></th>
                        <th width="120">项目编号</th>
                        <th width="200">项目名称</th>
                        <th width="100">项目类型</th>
                        <th width="100">编制人</th>
                        <th width="120">编制金额(万)</th>
                        <th width="100">一审计划工期(天)</th>
                        <th width="120">一审计划完成</th>
                        <th width="120">一审实际完成</th>
                        <th width="100">一审实际工期(天)</th>
                        <th width="150">一审进度结果</th>
                        <th width="100">二审计划工期(天)</th>
                        <th width="120">二审计划完成</th>
                        <th width="120">二审实际完成</th>
                        <th width="100">二审实际工期(天)</th>
                        <th width="150">二审进度结果</th>
                        <th width="100">三审计划工期(天)</th>
                        <th width="120">三审计划完成</th>
                        <th width="120">三审实际完成</th>
                        <th width="100">三审实际工期(天)</th>
                        <th width="150">三审进度结果</th>
                        <th width="150">操作</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in page_obj %}
                    <tr>
                        <td><input type="checkbox" class="item-checkbox" value="{{ item.pk }}"></td>
                        <td>{{ item.project_code }}</td>
                        <td>{{ item.project_name }}</td>
                        <td>{{ item.get_project_type_display }}</td>
                        <td>{{ item.compiler|default:"-" }}</td>
                        <td>{{ item.compilation_amount|floatformat:2 }}</td>
                        <td>{{ item.first_review_planned_duration|default:"0" }}</td>
                        <td>{{ item.first_review_planned_completion|date:"Y-m-d"|default:"-" }}</td>
                        <td>{{ item.first_review_actual_completion|date:"Y-m-d"|default:"-" }}</td>
                        <td>{{ item.first_review_actual_duration|default:"0" }}</td>
                        <td>{{ item.first_review_progress_result|default:"-" }}</td>
                        <td>{{ item.second_review_planned_duration|default:"0" }}</td>
                        <td>{{ item.second_review_planned_completion|date:"Y-m-d"|default:"-" }}</td>
                        <td>{{ item.second_review_actual_completion|date:"Y-m-d"|default:"-" }}</td>
                        <td>{{ item.second_review_actual_duration|default:"0" }}</td>
                        <td>{{ item.second_review_progress_result|default:"-" }}</td>
                        <td>{{ item.third_review_planned_duration|default:"0" }}</td>
                        <td>{{ item.third_review_planned_completion|date:"Y-m-d"|default:"-" }}</td>
                        <td>{{ item.third_review_actual_completion|date:"Y-m-d"|default:"-" }}</td>
                        <td>{{ item.third_review_actual_duration|default:"0" }}</td>
                        <td>{{ item.third_review_progress_result|default:"-" }}</td>
                        <td>
                            <a href="{% url 'eims_app:cost_task_implementation_detail' item.pk %}" class="btn btn-info btn-sm me-1">
                                <i class="bi bi-eye"></i>
                            </a>
                            <a href="{% url 'eims_app:cost_task_implementation_edit' item.pk %}" class="btn btn-warning btn-sm me-1">
                                <i class="bi bi-pencil"></i>
                            </a>
                            <button class="btn btn-danger btn-sm" onclick="deleteItem({{ item.pk }})">
                                <i class="bi bi-trash"></i>
                            </button>
                        </td>
                    </tr>
                    {% empty %}
                    <tr>
                        <td colspan="23" class="text-center py-4">暂无数据</td>
                    </tr>
                    {% endfor %}
                </tbody>"""

print("任务实施模板内容已准备")
print("请手动替换 task_implementation/list.html 中的表格部分")
