# 下拉列表"其他（手动输入）"模式推广指南

## ✅ 已完成的模块

1. **项目台账模块** (Project Ledger)
   - 文件：`form_project_ledger.py` + `project_ledger/form.html`
   - 字段：项目状态、合同状态、报建情况、进场通知

2. **合同管理模块** (Contract Management)  
   - 文件：`form_contract_management.py` + `contract_management/form.html`
   - 字段：合同类别、合同状态、结算情况

---

## 🔧 推广步骤

### 步骤 1: 修改 Form 类

在 `__init__` 方法中添加 choices，包含"其他"选项：

```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
    # 为下拉列表添加选项
    self.fields['your_field'].choices = [
        ('', '请选择'),
        ('value1', '选项 1'),
        ('value2', '选项 2'),
        ('other', '其他（手动输入）'),  # ← 添加这个选项
    ]
```

### 步骤 2: 更新 Meta.widgets

确保使用 Select widget：

```python
widgets = {
    'your_field': forms.Select(attrs={'class': 'form-select'}),
}
```

### 步骤 3: 修改模板 HTML

为每个字段添加隐藏的输入框：

```html
<div class="col-md-X mb-3">
    <label class="form-label">字段名称</label>
    {{ form.your_field }}
    <input type="text" class="form-control mt-1" id="your_field_other" 
           placeholder="请输入其他选项" style="display:none;">
    {% if form.your_field.errors %}
        <div class="text-danger small mt-1">{{ form.your_field.errors }}</div>
    {% endif %}
</div>
```

### 步骤 4: 添加 JavaScript

在模板底部添加通用脚本：

```javascript
document.addEventListener('DOMContentLoaded', function() {
    // 通用函数：绑定下拉列表和输入框
    function bindOtherSelect(selectId, inputId) {
        const select = document.getElementById(selectId);
        const input = document.getElementById(inputId);
        
        if (select && input) {
            select.addEventListener('change', function() {
                if (this.value === 'other') {
                    input.style.display = 'block';
                    input.focus();
                } else {
                    input.style.display = 'none';
                    input.value = '';
                }
            });
        }
    }
    
    // 绑定所有字段
    bindOtherSelect('id_your_field1', 'your_field1_other');
    bindOtherSelect('id_your_field2', 'your_field2_other');
});
```

---

## 📋 需要推广的模块清单

根据系统中的表单文件，以下模块需要应用此模式：

### 1. 月度报告模块 (`form_monthly_report.py`)
- 检查是否有状态字段需要添加"其他"选项

### 2. 人员管理模块 (`form_personnel.py`, `form_personnel_detail.py`)
- 岗位、部门等字段

### 3. 部门管理模块 (`form_department.py`)
- 审批流程等字段

### 4. 考勤管理模块 (`form_inspect.py`)
- 考勤状态等字段

### 5. 信息管理模块 (`form_info_collect.py`)
- 信息类型等字段

### 6. 产值回款模块 (`form_output_payment.py`)
- 回款状态等字段

### 7. 通知管理模块 (`form_notice.py`)
- 通知类型等字段

### 8. 附件管理模块 (`form_attachments.py`)
- 附件类型等字段

---

## 💡 最佳实践

### 什么时候使用"其他"选项？
- ✅ 状态字段（如：项目状态、合同状态）
- ✅ 类别字段（如：合同类别、部门类别）
- ✅ 类型字段（如：通知类型、附件类型）
- ❌ 布尔字段（是/否）不需要
- ❌ 已有完整枚举的字段不需要

### 命名规范
- Python 字段名：`your_field`
- HTML ID：`id_your_field` (Django 自动生成)
- 输入框 ID：`your_field_other`
- Placeholder：`请输入其他选项`

### 数据保存
如果用户选择了"其他"并输入了自定义值，需要在 clean 方法中处理：

```python
def clean(self):
    cleaned_data = super().clean()
    
    # 如果选择了"其他"，从输入框获取值
    if cleaned_data.get('your_field') == 'other':
        # 这里需要从 POST 数据中获取输入框的值
        # 或者在 save 方法中处理
        pass
    
    return cleaned_data
```

---

## 🎯 快速应用模板

复制以下代码并根据实际情况修改：

### Form 类模板
```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
    self.fields['field_name'].choices = [
        ('', '请选择'),
        ('option1', '选项 1'),
        ('option2', '选项 2'),
        ('other', '其他（手动输入）'),
    ]
```

### 模板 HTML 片段
```html
{{ form.field_name }}
<input type="text" class="form-control mt-1" 
       id="field_name_other" 
       placeholder="请输入其他选项" 
       style="display:none;">
```

### JavaScript 通用代码
```javascript
function bindOtherSelect(selectId, inputId) {
    const select = document.getElementById(selectId);
    const input = document.getElementById(inputId);
    if (select && input) {
        select.addEventListener('change', function() {
            if (this.value === 'other') {
                input.style.display = 'block';
                input.focus();
            } else {
                input.style.display = 'none';
                input.value = '';
            }
        });
    }
}

// 页面加载时绑定
document.addEventListener('DOMContentLoaded', function() {
    bindOtherSelect('id_field_name', 'field_name_other');
});
```

---

## ✅ 完成检查清单

对于每个需要修改的表单：

- [ ] Form 类的 `__init__` 方法中添加了 choices
- [ ] 每个字段都添加了 `('other', '其他（手动输入）')` 选项
- [ ] Meta.widgets 中使用 `forms.Select`
- [ ] 模板中为每个字段添加了隐藏输入框
- [ ] 模板底部添加了 JavaScript 绑定代码
- [ ] 测试选择"其他"时输入框正确显示
- [ ] 测试切换选项时输入框正确隐藏
- [ ] 测试保存功能正常工作

---

## 📝 注意事项

1. **不要修改布尔字段**：是/否字段保持 Select 即可
2. **保持 UI 一致性**：所有下拉列表都应该看起来一样
3. **用户体验优先**：选择"其他"后自动聚焦到输入框
4. **数据验证**：确保自定义输入也能正确保存

---

**创建时间**: 2026-03-26  
**模式**: Select + "Other" Option with Dynamic Input  
**状态**: ✅ 已在项目台账和合同管理模块成功实现
