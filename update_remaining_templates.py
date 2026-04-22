"""
批量更新造价咨询子模块模板的表头、表格内容和详情面板
"""
import re

# 定义每个模块的字段配置
modules_config = {
    'review_result': {
        'name': '审核成果',
        'url_prefix': 'cost_review_result',
        'icon': 'bi-file-earmark-check',
        'min_width': '2000px',
        'colspan': 18,
        'headers': '''                                <th class="text-center" width="50">
                                    <input type="checkbox" id="selectAll" class="form-check-input">
                                </th>
                                <th class="text-center">序号</th>
                                <th class="sortable" data-field="project_code" onclick="handleSort('project_code')">项目编号<span class="sort-icon"></span></th>
                                <th class="sortable" data-field="project_name" onclick="handleSort('project_name')">项目名称<span class="sort-icon"></span></th>
                                <th class="sortable" data-field="project_type" onclick="handleSort('project_type')">项目类型<span class="sort-icon"></span></th>
                                <th class="sortable text-end" data-field="first_submission" onclick="handleSort('first_submission')">一审送审(万)<span class="sort-icon"></span></th>
                                <th class="sortable" data-field="first_result" onclick="handleSort('first_result')">一审结果<span class="sort-icon"></span></th>
                                <th class="sortable text-end" data-field="first_reduction" onclick="handleSort('first_reduction')">一审审减(万)<span class="sort-icon"></span></th>
                                <th class="sortable text-end" data-field="first_reduction_rate" onclick="handleSort('first_reduction_rate')">一审减率(%)<span class="sort-icon"></span></th>
                                <th class="sortable text-end" data-field="second_submission" onclick="handleSort('second_submission')">二审送审(万)<span class="sort-icon"></span></th>
                                <th class="sortable" data-field="second_result" onclick="handleSort('second_result')">二审结果<span class="sort-icon"></span></th>
                                <th class="sortable text-end" data-field="second_reduction" onclick="handleSort('second_reduction')">二审审减(万)<span class="sort-icon"></span></th>
                                <th class="sortable text-end" data-field="second_reduction_rate" onclick="handleSort('second_reduction_rate')">二审减率(%)<span class="sort-icon"></span></th>
                                <th class="sortable text-end" data-field="third_submission" onclick="handleSort('third_submission')">三审送审(万)<span class="sort-icon"></span></th>
                                <th class="sortable" data-field="third_result" onclick="handleSort('third_result')">三审结果<span class="sort-icon"></span></th>
                                <th class="sortable text-end" data-field="third_reduction" onclick="handleSort('third_reduction')">三审审减(万)<span class="sort-icon"></span></th>
                                <th class="sortable text-end" data-field="third_reduction_rate" onclick="handleSort('third_reduction_rate')">三审减率(%)<span class="sort-icon"></span></th>
                                <th class="sortable text-end" data-field="final_approved_amount" onclick="handleSort('final_approved_amount')">最终审定(万)<span class="sort-icon"></span></th>
                                <th class="text-center sticky-col">操作</th>''',
        'data_attrs': '''                                data-project-code="{{ item.project_code|default:'' }}"
                                data-project-name="{{ item.project_name|default:'' }}"
                                data-project-type="{{ item.get_project_type_display|default:'' }}"
                                data-first-submission="{{ item.first_submission|default:0 }}"
                                data-first-result="{{ item.first_result|default:'' }}"
                                data-first-reduction="{{ item.first_reduction|default:0 }}"
                                data-first-reduction-rate="{{ item.first_reduction_rate|default:0 }}"
                                data-second-submission="{{ item.second_submission|default:0 }}"
                                data-second-result="{{ item.second_result|default:'' }}"
                                data-second-reduction="{{ item.second_reduction|default:0 }}"
                                data-second-reduction-rate="{{ item.second_reduction_rate|default:0 }}"
                                data-third-submission="{{ item.third_submission|default:0 }}"
                                data-third-result="{{ item.third_result|default:'' }}"
                                data-third-reduction="{{ item.third_reduction|default:0 }}"
                                data-third-reduction-rate="{{ item.third_reduction_rate|default:0 }}"
                                data-final-approved-amount="{{ item.final_approved_amount|default:0 }}"''',
        'table_cells': '''                                <td class="text-center">{{ forloop.counter|add:page_obj.start_index|add:-1 }}</td>
                                <td><code>{{ item.project_code|default:"-" }}</code></td>
                                <td>{{ item.project_name|default:"-" }}</td>
                                <td>{{ item.get_project_type_display|default:"-" }}</td>
                                <td class="text-end">{{ item.first_submission|floatformat:2 }}</td>
                                <td>{{ item.first_result|default:"-" }}</td>
                                <td class="text-end">{{ item.first_reduction|floatformat:2 }}</td>
                                <td class="text-end">{{ item.first_reduction_rate|floatformat:2 }}</td>
                                <td class="text-end">{{ item.second_submission|floatformat:2 }}</td>
                                <td>{{ item.second_result|default:"-" }}</td>
                                <td class="text-end">{{ item.second_reduction|floatformat:2 }}</td>
                                <td class="text-end">{{ item.second_reduction_rate|floatformat:2 }}</td>
                                <td class="text-end">{{ item.third_submission|floatformat:2 }}</td>
                                <td>{{ item.third_result|default:"-" }}</td>
                                <td class="text-end">{{ item.third_reduction|floatformat:2 }}</td>
                                <td class="text-end">{{ item.third_reduction_rate|floatformat:2 }}</td>
                                <td class="text-end">{{ item.final_approved_amount|floatformat:2 }}</td>''',
        'detail_fields': '''                    <!-- 基本信息 -->
                    <div class="detail-item">
                        <span class="detail-label">项目编号</span>
                        <span class="detail-value" id="detail-project-code"><code>-</code></span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">项目名称</span>
                        <span class="detail-value" id="detail-project-name"><strong>-</strong></span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">项目类型</span>
                        <span class="detail-value" id="detail-project-type">-</span>
                    </div>
                    
                    <!-- 一审信息 -->
                    <div class="detail-item">
                        <span class="detail-label">一审送审(万)</span>
                        <span class="detail-value" id="detail-first-submission">-</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">一审结果</span>
                        <span class="detail-value" id="detail-first-result">-</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">一审审减(万)</span>
                        <span class="detail-value" id="detail-first-reduction">-</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">一审减率(%)</span>
                        <span class="detail-value" id="detail-first-reduction-rate">-</span>
                    </div>
                    
                    <!-- 二审信息 -->
                    <div class="detail-item">
                        <span class="detail-label">二审送审(万)</span>
                        <span class="detail-value" id="detail-second-submission">-</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">二审结果</span>
                        <span class="detail-value" id="detail-second-result">-</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">二审审减(万)</span>
                        <span class="detail-value" id="detail-second-reduction">-</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">二审减率(%)</span>
                        <span class="detail-value" id="detail-second-reduction-rate">-</span>
                    </div>
                    
                    <!-- 三审信息 -->
                    <div class="detail-item">
                        <span class="detail-label">三审送审(万)</span>
                        <span class="detail-value" id="detail-third-submission">-</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">三审结果</span>
                        <span class="detail-value" id="detail-third-result">-</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">三审审减(万)</span>
                        <span class="detail-value" id="detail-third-reduction">-</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">三审减率(%)</span>
                        <span class="detail-value" id="detail-third-reduction-rate">-</span>
                    </div>
                    
                    <!-- 最终审定 -->
                    <div class="detail-item">
                        <span class="detail-label">最终审定(万)</span>
                        <span class="detail-value text-success" id="detail-final-approved-amount"><strong>-</strong></span>
                    </div>''',
        'js_field_map': '''        'detail-project-code': data.project_code || '-',
        'detail-project-name': data.project_name || '-',
        'detail-project-type': data.project_type || '-',
        'detail-first-submission': data.first_submission ? '¥' + parseFloat(data.first_submission).toFixed(2) : '-',
        'detail-first-result': data.first_result || '-',
        'detail-first-reduction': data.first_reduction ? '¥' + parseFloat(data.first_reduction).toFixed(2) : '-',
        'detail-first-reduction-rate': data.first_reduction_rate ? parseFloat(data.first_reduction_rate).toFixed(2) + '%' : '-',
        'detail-second-submission': data.second_submission ? '¥' + parseFloat(data.second_submission).toFixed(2) : '-',
        'detail-second-result': data.second_result || '-',
        'detail-second-reduction': data.second_reduction ? '¥' + parseFloat(data.second_reduction).toFixed(2) : '-',
        'detail-second-reduction-rate': data.second_reduction_rate ? parseFloat(data.second_reduction_rate).toFixed(2) + '%' : '-',
        'detail-third-submission': data.third_submission ? '¥' + parseFloat(data.third_submission).toFixed(2) : '-',
        'detail-third-result': data.third_result || '-',
        'detail-third-reduction': data.third_reduction ? '¥' + parseFloat(data.third_reduction).toFixed(2) : '-',
        'detail-third-reduction-rate': data.third_reduction_rate ? parseFloat(data.third_reduction_rate).toFixed(2) + '%' : '-',
        'detail-final-approved-amount': data.final_approved_amount ? '¥' + parseFloat(data.final_approved_amount).toFixed(2) : '-' '''
    },
    
    'payment_status': {
        'name': '收费情况',
        'url_prefix': 'cost_payment_status',
        'icon': 'bi-cash-stack',
        'min_width': '1800px',
        'colspan': 16,
        'headers': '''                                <th class="text-center" width="50">
                                    <input type="checkbox" id="selectAll" class="form-check-input">
                                </th>
                                <th class="text-center">序号</th>
                                <th class="sortable" data-field="project_code" onclick="handleSort('project_code')">项目编号<span class="sort-icon"></span></th>
                                <th class="sortable" data-field="project_name" onclick="handleSort('project_name')">项目名称<span class="sort-icon"></span></th>
                                <th class="sortable" data-field="project_type" onclick="handleSort('project_type')">项目类型<span class="sort-icon"></span></th>
                                <th class="sortable text-end" data-field="invoice_amount" onclick="handleSort('invoice_amount')">开票金额(万)<span class="sort-icon"></span></th>
                                <th class="sortable" data-field="is_invoiced" onclick="handleSort('is_invoiced')">是否开票<span class="sort-icon"></span></th>
                                <th class="sortable text-end" data-field="owner_payable" onclick="handleSort('owner_payable')">业主方应付(万)<span class="sort-icon"></span></th>
                                <th class="sortable text-end" data-field="owner_paid" onclick="handleSort('owner_paid')">业主方已付(万)<span class="sort-icon"></span></th>
                                <th class="sortable text-end" data-field="owner_pending" onclick="handleSort('owner_pending')">业主方待付(万)<span class="sort-icon"></span></th>
                                <th class="sortable text-end" data-field="contractor_payable" onclick="handleSort('contractor_payable')">施工方应付(万)<span class="sort-icon"></span></th>
                                <th class="sortable text-end" data-field="contractor_paid" onclick="handleSort('contractor_paid')">施工方已付(万)<span class="sort-icon"></span></th>
                                <th class="sortable text-end" data-field="contractor_pending" onclick="handleSort('contractor_pending')">施工方待付(万)<span class="sort-icon"></span></th>
                                <th class="sortable" data-field="is_settled" onclick="handleSort('is_settled')">是否结清<span class="sort-icon"></span></th>
                                <th class="text-center sticky-col">操作</th>''',
        'data_attrs': '''                                data-project-code="{{ item.project_code|default:'' }}"
                                data-project-name="{{ item.project_name|default:'' }}"
                                data-project-type="{{ item.get_project_type_display|default:'' }}"
                                data-invoice-amount="{{ item.invoice_amount|default:0 }}"
                                data-is-invoiced="{{ item.get_is_invoiced_display|default:'' }}"
                                data-owner-payable="{{ item.owner_payable|default:0 }}"
                                data-owner-paid="{{ item.owner_paid|default:0 }}"
                                data-owner-pending="{{ item.owner_pending|default:0 }}"
                                data-contractor-payable="{{ item.contractor_payable|default:0 }}"
                                data-contractor-paid="{{ item.contractor_paid|default:0 }}"
                                data-contractor-pending="{{ item.contractor_pending|default:0 }}"
                                data-is-settled="{{ item.get_is_settled_display|default:'' }}"''',
        'table_cells': '''                                <td class="text-center">{{ forloop.counter|add:page_obj.start_index|add:-1 }}</td>
                                <td><code>{{ item.project_code|default:"-" }}</code></td>
                                <td>{{ item.project_name|default:"-" }}</td>
                                <td>{{ item.get_project_type_display|default:"-" }}</td>
                                <td class="text-end">{{ item.invoice_amount|floatformat:2 }}</td>
                                <td>{{ item.get_is_invoiced_display|default:"-" }}</td>
                                <td class="text-end">{{ item.owner_payable|floatformat:2 }}</td>
                                <td class="text-end">{{ item.owner_paid|floatformat:2 }}</td>
                                <td class="text-end">{{ item.owner_pending|floatformat:2 }}</td>
                                <td class="text-end">{{ item.contractor_payable|floatformat:2 }}</td>
                                <td class="text-end">{{ item.contractor_paid|floatformat:2 }}</td>
                                <td class="text-end">{{ item.contractor_pending|floatformat:2 }}</td>
                                <td>{{ item.get_is_settled_display|default:"-" }}</td>''',
        'detail_fields': '''                    <!-- 基本信息 -->
                    <div class="detail-item">
                        <span class="detail-label">项目编号</span>
                        <span class="detail-value" id="detail-project-code"><code>-</code></span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">项目名称</span>
                        <span class="detail-value" id="detail-project-name"><strong>-</strong></span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">项目类型</span>
                        <span class="detail-value" id="detail-project-type">-</span>
                    </div>
                    
                    <!-- 开票信息 -->
                    <div class="detail-item">
                        <span class="detail-label">开票金额(万)</span>
                        <span class="detail-value" id="detail-invoice-amount">-</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">是否开票</span>
                        <span class="detail-value" id="detail-is-invoiced">-</span>
                    </div>
                    
                    <!-- 业主方付款 -->
                    <div class="detail-item">
                        <span class="detail-label">业主方应付(万)</span>
                        <span class="detail-value" id="detail-owner-payable">-</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">业主方已付(万)</span>
                        <span class="detail-value" id="detail-owner-paid">-</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">业主方待付(万)</span>
                        <span class="detail-value text-warning" id="detail-owner-pending">-</span>
                    </div>
                    
                    <!-- 施工方付款 -->
                    <div class="detail-item">
                        <span class="detail-label">施工方应付(万)</span>
                        <span class="detail-value" id="detail-contractor-payable">-</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">施工方已付(万)</span>
                        <span class="detail-value" id="detail-contractor-paid">-</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">施工方待付(万)</span>
                        <span class="detail-value text-warning" id="detail-contractor-pending">-</span>
                    </div>
                    
                    <!-- 结算状态 -->
                    <div class="detail-item">
                        <span class="detail-label">是否结清</span>
                        <span class="detail-value" id="detail-is-settled">-</span>
                    </div>''',
        'js_field_map': '''        'detail-project-code': data.project_code || '-',
        'detail-project-name': data.project_name || '-',
        'detail-project-type': data.project_type || '-',
        'detail-invoice-amount': data.invoice_amount ? '¥' + parseFloat(data.invoice_amount).toFixed(2) : '-',
        'detail-is-invoiced': data.is_invoiced || '-',
        'detail-owner-payable': data.owner_payable ? '¥' + parseFloat(data.owner_payable).toFixed(2) : '-',
        'detail-owner-paid': data.owner_paid ? '¥' + parseFloat(data.owner_paid).toFixed(2) : '-',
        'detail-owner-pending': data.owner_pending ? '¥' + parseFloat(data.owner_pending).toFixed(2) : '-',
        'detail-contractor-payable': data.contractor_payable ? '¥' + parseFloat(data.contractor_payable).toFixed(2) : '-',
        'detail-contractor-paid': data.contractor_paid ? '¥' + parseFloat(data.contractor_paid).toFixed(2) : '-',
        'detail-contractor-pending': data.contractor_pending ? '¥' + parseFloat(data.contractor_pending).toFixed(2) : '-',
        'detail-is-settled': data.is_settled || '-' '''
    }
}

print("配置已准备就绪")
print(f"共 {len(modules_config)} 个模块需要更新")
for key in modules_config.keys():
    print(f"  - {key}")
