{% extends 'base/base.html' %}{% load static %}{% block title %}合同管理{% endblock %}{% block extra_css %}
<style>
/* === 三段式固定布局核心样式 === */
.contract-top-bar {
    position: sticky;
    top: 0;
    background: white;
    z-index: 1020;
    padding: 12px 0;
    border-bottom: 1px solid #e9ecef;
    margin-bottom: 0;
}
/* === 关键修复：独立的固定表头容器 === */
.contract-header-container {
    position: sticky;
    top: 0;
    background: white;
    z-index: 1015;
    border-bottom: 1px solid #dee2e6;
    margin-top: 8px;
    overflow-x: hidden;
}
.contract-header-container table {
    margin-bottom: 0 !important;
    border-collapse: collapse;
    table-layout: fixed !important;
    width: 1200px !important; /* 恢复原始宽度 */
    transform: translateX(-0.5px); /* 微调对齐 */
}
.contract-content-container {
    max-height: calc(100vh - 280px);
    overflow-y: auto;
    margin-top: 0;
}
.contract-content-container table {
    margin-top: 0;
    table-layout: fixed !important;
    width: 1200px !important; /* 恢复原始宽度 */
    transform: translateX(-0.5px); /* 微调对齐 */
}
/* 表头样式（精确控制） */
.contract-header-container table th {
    text-align: center !important;
    vertical-align: middle !important;
    padding: 12px 8px !important;
    font-weight: 600 !important;
    background-color: #f8f9fa !important;
    border: 1px solid #dee2e6 !important;
    position: relative !important;
    box-sizing: border-box !important;
}
/* 内容行样式 */
.contract-content-container table td {
    text-align: center !important;
    vertical-align: middle !important;
    padding: 10px 8px !important;
    box-sizing: border-box !important;
}
/* 强制表格列宽同步 */
.contract-header-container table,
.contract-content-container table {
    min-width: 1200px !important;
    table-layout: fixed !important;
    border-collapse: separate !important;
    border-spacing: 0 !important;
}

/* === 关键修复：统一列宽定义（使用固定像素） === */
/* 第1列：复选框 */
.contract-header-container table th:nth-child(1),
.contract-content-container table td:nth-child(1) { width: 50px !important; }

/* 第2列：序号 */
.contract-header-container table th:nth-child(2),
.contract-content-container table td:nth-child(2) { width: 60px !important; }

/* 第3列：合同类型 */
.contract-header-container table th:nth-child(3),
.contract-content-container table td:nth-child(3) { width: 100px !important; }

/* 第4列：项目编号 */
.contract-header-container table th:nth-child(4),
.contract-content-container table td:nth-child(4) { width: 120px !important; }

/* 第5列：合同编号 */
.contract-header-container table th:nth-child(5),
.contract-content-container table td:nth-child(5) { width: 120px !important; }

/* 第6列：项目名称 */
.contract-header-container table th:nth-child(6),
.contract-content-container table td:nth-child(6) { width: 180px !important; }

/* 第7列：合同状态 */
.contract-header-container table th:nth-child(7),
.contract-content-container table td:nth-child(7) { width: 90px !important; }

/* 第8列：合同甲方 */
.contract-header-container table th:nth-child(8),
.contract-content-container table td:nth-child(8) { width: 150px !important; }

/* 第9列：合同乙方 */
.contract-header-container table th:nth-child(9),
.contract-content-container table td:nth-child(9) { width: 150px !important; }

/* 第10列：合同总价 */
.contract-header-container table th:nth-child(10),
.contract-content-container table td:nth-child(10) { width: 100px !important; }

/* 第11列：项目投资 */
.contract-header-container table th:nth-child(11),
.contract-content-container table td:nth-child(11) { width: 100px !important; }

/* 第12列：签订日期 */
.contract-header-container table th:nth-child(12),
.contract-content-container table td:nth-child(12) { width: 100px !important; }

/* 第13列：项目地址 */
.contract-header-container table th:nth-child(13),
.contract-content-container table td:nth-child(13) { width: 180px !important; }

/* 第14列：备注 */
.contract-header-container table th:nth-child(14),
.contract-content-container table td:nth-child(14) { width: 100px !important; }

/* 第15列：操作 */
.contract-header-container table th:nth-child(15),
.contract-content-container table td:nth-child(15) { width: 180px !important; } /* 扩宽操作列 */

/* 滚动区域样式 */
.contract-content-container > div {
    overflow-x: auto;
}

/* 列宽拖拽样式 */
.dragging-indicator {
    position: fixed;
    top: 0;
    height: 100vh;
    width: 2px;
    background: #0d6efd;
    z-index: 9999;
    display: none;
    pointer-events: none;
}
.resizable-grip {
    position: absolute;
    top: 0;
    right: -3px;
    bottom: 0;
    width: 6px;
    cursor: col-resize;
    z-index: 10;
    background: transparent;
}
.resizable-grip:hover {
    background: rgba(13, 110, 253, 0.3);
}

/* === 内容对齐样式 === */
/* 左对齐：项目名称、备注 */
.contract-content-container table td:nth-child(6), /* 项目名称 */
.contract-content-container table td:nth-child(14) { /* 备注 */
    text-align: left !important;
    padding-left: 12px !important;
}

/* 右对齐：金额列 */
.contract-content-container table td:nth-child(10), /* 合同总价 */
.contract-content-container table td:nth-child(11) { /* 项目投资 */
    text-align: right !important;
    padding-right: 12px !important;
}

/* 操作列样式：按钮并排 */
.contract-content-container table td:nth-child(15) {
    text-align: left !important;
    padding-left: 10px !important;
}
.contract-content-container table td:nth-child(15) .btn {
    margin-right: 2px !important;
    margin-left: 0 !important;
    padding: 4px 8px !important;
    font-size: 0.8rem !important;
}

/* === 按钮布局优化 === */
.button-group {
    display: flex;
    gap: 10px;
    align-items: center;
}
.new-contract-btn {
    margin-left: auto; /* 推到右侧 */
}
.import-btn {
    margin-left: 0;
}
</style>
{% endblock %}{% block content %}
<div class="contract-top-bar">
<div class="d-flex justify-content-between align-items-center mb-3">
    <h4>合同列表</h4>
    <div class="button-group">
        <button type="button" class="btn btn-success import-btn" onclick="document.getElementById('import-file').click()">
            导入Excel
        </button>
        <a href="{% url 'contract_add' %}" class="btn btn-primary new-contract-btn">新建合同</a>
    </div>
</div>

<form method="get" class="row mb-3 g-2">
    <div class="col-md-3">
        <input type="text" name="keyword" value="{{ keyword }}" 
               class="form-control" placeholder="项目名称/合同甲方/合同乙方/项目地址/备注">
    </div>
    <div class="col-md-2">
        <select name="status" class="form-select">
            <option value="">全部状态</option>
            {% for value, label in status_choices %}
            <option value="{{ value }}" {% if selected_status == value %}selected{% endif %}>
                {{ label }}
            </option>
            {% endfor %}
        </select>
    </div>
    <div class="col-md-2">
        <select name="contract_type" class="form-select">
            <option value="">全部类型</option>
            {% for value, label in type_choices %}
            <option value="{{ value }}" {% if selected_type == value %}selected{% endif %}>
                {{ label }}
            </option>
            {% endfor %}
        </select>
    </div>
    <div class="col-md-3">
        <button type="submit" class="btn btn-primary">筛选</button>
        <a href="{% url 'contract_list' %}" class="btn btn-secondary">重置</a>
    </div>
</form>
</div>

<form id="batch-form" method="post" action="{% url 'contract_batch_delete' %}">
    {% csrf_token %}
    
    <!-- === 关键：分离表头容器（固定宽度+微调） === -->
    <div class="contract-header-container">
        <table class="table table-bordered" style="width: 1200px; transform: translateX(-0.5px);">
            <thead class="table-light">
                <tr>
                    <th><input type="checkbox" id="select-all" style="margin: 0 auto; display: block;"></th>
                    <th>序号</th>
                    <th>合同类型</th>
                    <th>项目编号</th>
                    <th>合同编号</th>
                    <th>项目名称</th>
                    <th>合同状态</th>
                    <th>合同甲方</th>
                    <th>合同乙方</th>
                    <th>合同总价(万)</th>
                    <th>项目投资(万)</th>
                    <th>签订日期</th>
                    <th>项目地址</th>
                    <th>备注</th>
                    <th>操作</th>
                </tr>
            </thead>
        </table>
    </div>
    
    <!-- === 内容滚动容器（固定宽度+微调） === -->
    <div class="contract-content-container">
        <div style="overflow-x: auto;">
            <table class="table table-bordered table-hover" style="width: 1200px; transform: translateX(-0.5px);">
                <tbody>
                    {% for contract in page_obj %}
                    <tr>
                        <td><input type="checkbox" name="ids" value="{{ contract.id }}" style="margin: 0 auto; display: block;"></td>
                        <td>{{ forloop.counter0|add:page_obj.start_index }}</td>
                        <td>{{ contract.get_contract_type_display|default:"-" }}</td>
                        <td>{{ contract.project_code|default:"-" }}</td>
                        <td>{{ contract.contract_code|default:"-" }}</td>
                        <td style="text-align: left; padding-left: 12px;">{{ contract.project_name|default:"-" }}</td>
                        <td>
                            {% if contract.status == 'active' %}
                            <span class="badge bg-success">已生效</span>
                            {% elif contract.status == 'expired' %}
                            <span class="badge bg-danger">已过期</span>
                            {% else %}
                            <span class="badge bg-secondary">草稿</span>
                            {% endif %}
                        </td>
                        <td>{{ contract.contract_party_a|default:"-" }}</td>
                        <td>{{ contract.contract_party_b|default:"-" }}</td>
                        <td style="text-align: right; padding-right: 12px;">{{ contract.contract_amount_10k|floatformat:2|default:"0.00" }}</td>
                        <td style="text-align: right; padding-right: 12px;">{{ contract.project_investment_10k|floatformat:2|default:"0.00" }}</td>
                        <td>{{ contract.signing_time|date:"Y-m-d"|default:"-" }}</td>
                        <td>{{ contract.project_address|default:"-" }}</td>
                        <td style="text-align: left; padding-left: 12px;">{{ contract.remark|default:"无" }}</td>
                        <td style="text-align: left; padding-left: 10px;">
                            <a href="{% url 'contract_view' contract.id %}" class="btn btn-sm btn-info me-1" style="margin-right: 2px !important; padding: 4px 8px !important; font-size: 0.8rem !important;">查看</a>
                            <a href="{% url 'contract_edit' contract.id %}" class="btn btn-sm btn-warning me-1" style="margin-right: 2px !important; padding: 4px 8px !important; font-size: 0.8rem !important;">编辑</a>
                            <button type="button" class="btn btn-sm btn-danger" 
                                    onclick="deleteContract({{ contract.id }}, '{{ contract.contract_code|escapejs }}')"
                                    style="padding: 4px 8px !important; font-size: 0.8rem !important;">
                                删除
                            </button>
                        </td>
                    </tr>
                    {% empty %}
                    <tr>
                        <td colspan="15" class="text-center">暂无合同数据</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <!-- === 底部批量删除按钮 === -->
    {% if page_obj %}
    <div class="mt-3">
        <button type="button" class="btn btn-danger" onclick="confirmBatchDelete()" id="batch-delete-btn">
            批量删除 (0条)
        </button>
    </div>
    {% endif %}
</form>

<nav aria-label="Page navigation">
    <ul class="pagination justify-content-center">
        {% if page_obj.has_previous %}
        <li class="page-item">
            <a class="page-link" href="?page={{ page_obj.previous_page_number }}&status={{ selected_status }}&contract_type={{ selected_type }}&keyword={{ keyword }}">«</a>
        </li>
        {% endif %}

        {% for num in page_obj.paginator.page_range %}
            {% if num > page_obj.number|add:'-3' and num < page_obj.number|add:'4' %}
                {% if num == page_obj.number %}
                <li class="page-item active"><span class="page-link">{{ num }}</span></li>
                {% else %}
                <li class="page-item">
                    <a class="page-link" href="?page={{ num }}&status={{ selected_status }}&contract_type={{ selected_type }}&keyword={{ keyword }}">{{ num }}</a>
                </li>
                {% endif %}
            {% endif %}
        {% endfor %}

        {% if page_obj.has_next %}
        <li class="page-item">
            <a class="page-link" href="?page={{ page_obj.next_page_number }}&status={{ selected_status }}&contract_type={{ selected_type }}&keyword={{ keyword }}">»</a>
        </li>
        {% endif %}
    </ul>
</nav>

<p class="text-center mt-3">
    显示 {{ page_obj.start_index }}-{{ page_obj.end_index }} 条，共 {{ page_obj.paginator.count }} 条
</p>

<script>
// 全选/取消全选
document.getElementById('select-all').addEventListener('change', function() {
    const checkboxes = document.querySelectorAll('input[name="ids"]');
    checkboxes.forEach(cb => cb.checked = this.checked);
    updateBatchDeleteText();
});

// 动态更新批量删除按钮文本
function updateBatchDeleteText() {
    const checked = document.querySelectorAll('input[name="ids"]:checked');
    const count = checked.length;
    const button = document.getElementById('batch-delete-btn');
    if (button) {
        button.textContent = `批量删除 (${count}条)`;
    }
}

// 批量删除确认
function confirmBatchDelete() {
    const checked = document.querySelectorAll('input[name="ids"]:checked');
    if (checked.length === 0) {
        alert('请至少选择一条记录');
        return;
    }
    
    // 获取选中合同的编号
    const contractCodes = [];
    checked.forEach(checkbox => {
        const row = checkbox.closest('tr');
        const codeCell = row.cells[4]; // 合同编号列（索引4）
        contractCodes.push(codeCell.textContent.trim());
    });
    
    const codes = contractCodes.join(', ');
    if (confirm(`确定批量删除选中的 ${checked.length} 条合同？\n\n涉及合同：${codes}`)) {
        document.getElementById('batch-form').submit();
    }
}

// 单个合同删除
function deleteContract(contractId, contractCode) {
    if (confirm(`确定删除合同【${contractCode}】？`)) {
        // 创建临时表单提交删除请求
        const form = document.createElement('form');
        form.method = 'post';
        form.action = `{% url 'contract_delete' 0 %}`.replace('/0/', '/' + contractId + '/');
        form.style.display = 'none';
        
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = '{{ csrf_token }}';
        
        form.appendChild(csrfInput);
        document.body.appendChild(form);
        form.submit();
    }
}

// 导入功能
function handleImport(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('excel_file', file);
    formData.append('csrfmiddlewaretoken', '{{ csrf_token }}');
    
    fetch('{% url "contract_import" %}', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(html => {
        location.reload();
    });
}

// 列宽拖拽初始化（同步调整两个表格）
document.addEventListener('DOMContentLoaded', function() {
    // 动态调整容器高度
    const headerContainer = document.querySelector('.contract-header-container');
    const contentContainer = document.querySelector('.contract-content-container');
    const topBar = document.querySelector('.contract-top-bar');
    if (topBar && contentContainer) {
        const topHeight = topBar.offsetHeight + headerContainer.offsetHeight;
        contentContainer.style.maxHeight = `calc(100vh - ${topHeight + 60}px)`;
    }
    
    // 获取两个表格的表头元素
    const headerTable = document.querySelector('.contract-header-container table');
    const contentTable = document.querySelector('.contract-content-container table');
    
    if (!headerTable || !contentTable) return;
    
    const resizer = document.createElement('div');
    resizer.className = 'dragging-indicator';
    document.body.appendChild(resizer);
    
    let startX, startWidth, currentTh, currentTdIndex, tableOffsetLeft;
    
    const headerHeaders = headerTable.querySelectorAll('thead th');
    headerHeaders.forEach((th, index) => {
        if (index === 0) return; // 跳过第一列（复选框列）
        if (index === headerHeaders.length - 1) return; // 跳过最后一列（操作列）
        
        const grip = document.createElement('div');
        grip.className = 'resizable-grip';
        th.appendChild(grip);
        
        grip.addEventListener('mousedown', (e) => {
            e.preventDefault();
            e.stopPropagation();
            currentTh = th;
            currentTdIndex = index;
            
            startX = e.clientX;
            startWidth = th.offsetWidth;
            tableOffsetLeft = headerTable.getBoundingClientRect().left;
            
            resizer.style.display = 'block';
            resizer.style.left = (tableOffsetLeft + th.offsetLeft + th.offsetWidth) + 'px';
            
            document.addEventListener('mousemove', resize);
            document.addEventListener('mouseup', stopResize);
        });
    });
    
    function resize(e) {
        const diff = e.clientX - startX;
        const newWidth = startWidth + diff;
        if (newWidth < 80) return; // 最小宽度限制
        
        // 调整表头列宽
        currentTh.style.width = newWidth + 'px';
        
        // 同步调整内容表格对应列宽
        const contentRows = contentTable.querySelectorAll('tr');
        contentRows.forEach(row => {
            const cell = row.cells[currentTdIndex];
            if (cell) {
                cell.style.width = newWidth + 'px';
            }
        });
        
        // 动态更新CSS规则（确保所有行都应用新宽度）
        const styleId = `dynamic-width-${currentTdIndex}`;
        let styleElement = document.getElementById(styleId);
        if (!styleElement) {
            styleElement = document.createElement('style');
            styleElement.id = styleId;
            document.head.appendChild(styleElement);
        }
        
        // 使用nth-child选择器确保精确匹配
        styleElement.textContent = `
            .contract-header-container table th:nth-child(${currentTdIndex + 1}),
            .contract-content-container table td:nth-child(${currentTdIndex + 1}) {
                width: ${newWidth}px !important;
            }
        `;
        
        // 更新蓝色基准线位置
        resizer.style.left = (tableOffsetLeft + currentTh.offsetLeft + newWidth) + 'px';
    }
    
    function stopResize() {
        resizer.style.display = 'none';
        document.removeEventListener('mousemove', resize);
        document.removeEventListener('mouseup', stopResize);
    }
    
    // 批量删除按钮更新事件
    const selectAll = document.getElementById('select-all');
    if (selectAll) {
        selectAll.addEventListener('change', updateBatchDeleteText);
    }
    
    const checkboxes = document.querySelectorAll('input[name="ids"]');
    checkboxes.forEach(cb => {
        cb.addEventListener('change', updateBatchDeleteText);
    });
    
    updateBatchDeleteText();
});
</script>
{% endblock %}