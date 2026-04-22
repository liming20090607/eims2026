/**
 * 动态选项添加通用组件
 * 
 * 使用方法:
 * 1. 在 HTML 中添加"+ 新增"按钮，调用 addDynamicChoice() 函数
 * 2. 传入类别、下拉框 ID 等参数
 * 3. 用户添加后自动更新下拉列表
 */

/**
 * 显示添加动态选项的模态框
 * @param {string} category - 选项类别，如 "project.project_status"
 * @param {string} selectElementId - 目标下拉框元素 ID
 * @param {string} [categoryName=''] - 类别中文名称（可选）
 */
function addDynamicChoice(category, selectElementId, categoryName = '') {
    // 如果没有指定类别名称，从类别代码推断
    if (!categoryName) {
        const parts = category.split('.');
        categoryName = parts[parts.length - 1].replace(/_/g, ' ');
    }
    
    // 创建模态框 HTML
    const modalHtml = `
        <div class="modal fade" id="addChoiceModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <form id="addChoiceForm">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="bi bi-plus-circle"></i> 添加${categoryName}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-3">
                                <label class="form-label">选项代码 <span class="text-danger">*</span></label>
                                <input type="text" class="form-control" name="code" required 
                                       placeholder="请输入英文代码（如：custom_status）"
                                       pattern="[a-z][a-z0-9_]*"
                                       title="必须以字母开头，只能包含小写字母、数字和下划线">
                                <div class="form-text">说明：用于数据库存储的代码，如 not_started</div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">选项名称 <span class="text-danger">*</span></label>
                                <input type="text" class="form-control" name="name" required 
                                       placeholder="请输入中文名称（如：自定义状态）">
                                <div class="form-text">说明：显示在下拉列表中的名称</div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            <button type="submit" class="btn btn-primary">
                                <i class="bi bi-check-circle"></i> 确定
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
    
    // 添加到页面
    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = modalHtml;
    document.body.appendChild(modalContainer);
    
    // 显示模态框
    const modal = new bootstrap.Modal(document.getElementById('addChoiceModal'));
    modal.show();
    
    // 处理表单提交
    document.getElementById('addChoiceForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const code = formData.get('code');
        const name = formData.get('name');
        
        // 发送到服务器
        fetch('/api/dynamic-choices/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                category: category,
                code: code,
                name: name
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 添加到下拉列表
                const selectElement = document.getElementById(selectElementId);
                if (selectElement) {
                    const option = document.createElement('option');
                    option.value = data.data.code;
                    option.textContent = data.data.name;
                    selectElement.appendChild(option);
                    
                    // 选中新添加的选项
                    selectElement.value = data.data.code;
                }
                
                // 显示成功消息
                showMessage('success', '添加成功');
                
                // 关闭模态框
                modal.hide();
                
                // 移除模态框
                setTimeout(() => {
                    modalContainer.remove();
                }, 300);
            } else {
                showMessage('danger', data.message || '添加失败');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage('danger', '网络错误，请稍后重试');
        });
    });
    
    // 模态框关闭时清理
    document.getElementById('addChoiceModal').addEventListener('hidden.bs.modal', function() {
        modalContainer.remove();
    });
}

/**
 * 获取 CSRF Token
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * 显示提示消息
 * @param {string} type - 消息类型：'success', 'danger', 'warning', 'info'
 * @param {string} message - 消息内容
 */
function showMessage(type, message) {
    // 检查是否已有消息容器
    let messageContainer = document.getElementById('dynamic-choice-message');
    if (!messageContainer) {
        messageContainer = document.createElement('div');
        messageContainer.id = 'dynamic-choice-message';
        messageContainer.style.position = 'fixed';
        messageContainer.style.top = '20px';
        messageContainer.style.right = '20px';
        messageContainer.style.zIndex = '9999';
        document.body.appendChild(messageContainer);
    }
    
    // 创建消息元素
    const messageEl = document.createElement('div');
    messageEl.className = `alert alert-${type} alert-dismissible fade show`;
    messageEl.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    messageContainer.innerHTML = '';
    messageContainer.appendChild(messageEl);
    
    // 3 秒后自动消失
    setTimeout(() => {
        messageEl.classList.remove('show');
        setTimeout(() => {
            messageContainer.innerHTML = '';
        }, 150);
    }, 3000);
}

/**
 * 加载动态选项到下拉列表
 * @param {string} category - 选项类别
 * @param {string} selectElementId - 目标下拉框元素 ID
 */
function loadDynamicChoices(category, selectElementId) {
    fetch(`/api/dynamic-choices/${category}/`)
        .then(response => response.json())
        .then(choices => {
            const selectElement = document.getElementById(selectElementId);
            if (selectElement && choices.length > 0) {
                // 保留第一个选项（通常是"请选择"）
                const firstOption = selectElement.options[0];
                selectElement.innerHTML = '';
                if (firstOption && !firstOption.value) {
                    selectElement.appendChild(firstOption);
                }
                
                // 添加动态选项
                choices.forEach(choice => {
                    const option = document.createElement('option');
                    option.value = choice.code;
                    option.textContent = choice.name;
                    selectElement.appendChild(option);
                });
            }
        })
        .catch(error => {
            console.error('加载动态选项失败:', error);
        });
}
