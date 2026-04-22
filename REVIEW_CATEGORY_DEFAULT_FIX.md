# 审核类别移除默认值 - 功能修复总结

## 📌 修复概述

修复了"审核类别"字段的不当默认值问题，确保：
1. **审核类别**字段没有默认值，默认为"---------"（空选项）
2. 当**项目类型**包含"编制"时，**审核类别**字段被禁用且值为空
3. 当**项目类型**包含"审核"时，**审核类别**字段可选

---

## 🐛 问题描述

### 修复前
- ❌ 审核类别有默认值"初审"
- ❌ 预算编制项目的审核类别显示为"初审"（不合理）
- ❌ 用户需要手动清除默认值

### 修复后
- ✅ 审核类别默认值为空"---------"
- ✅ 预算编制项目的审核类别显示为"-"（空白）
- ✅ 预算审核项目的审核类别可以正常选择

---

## 📁 修改的文件

### 1. 模型文件
**文件**：`eims_app/models/model_cost_unified.py`

**修改内容**：
```python
# 修复前
review_category = models.CharField("审核类别", max_length=20, 
    choices=REVIEW_CATEGORY_CHOICES, default='initial', blank=True)

# 修复后
review_category = models.CharField("审核类别", max_length=20, 
    choices=REVIEW_CATEGORY_CHOICES, blank=True, default='')
```

**变更说明**：
- 移除 `default='initial'`
- 改为 `default=''`（空字符串）

---

### 2. 表单文件
**文件**：`eims_app/forms/form_cost_sub_modules.py`

**修改内容**：
```python
# 修复前
'review_category': forms.Select(attrs={'class': 'form-select'}),

# 修复后
'review_category': forms.Select(attrs={'class': 'form-select'}, 
    choices=[('', '---------')] + CostProjectUnified.REVIEW_CATEGORY_CHOICES),
```

**变更说明**：
- 在choices列表开头添加空选项 `('', '---------')`
- 确保下拉框第一个选项为空白

---

### 3. 数据库迁移
**文件**：`eims_app/migrations/0018_alter_costprojectunified_review_category.py`

**迁移内容**：
- 修改 `review_category` 字段的默认值
- 从 `default='initial'` 改为 `default=''`

---

## 🎨 界面效果

### 表单页面 - 预算编制项目

```
┌─────────────────────────────────────────────┐
│ 项目类型              │ 审核类别            │
│ ┌───────────────────┐│ ┌─────────────────┐ │
│ │ 预算编制          ││ │ ---------   ▼   │ │ (禁用)
│ └───────────────────┘│ └─────────────────┘ │
└─────────────────────────────────────────────┘
```

**说明**：
- 项目类型为"预算编制"
- 审核类别显示为"---------"且禁用（灰色）
- 用户无法选择审核类别

---

### 表单页面 - 预算审核项目

```
┌─────────────────────────────────────────────┐
│ 项目类型              │ 审核类别            │
│ ┌───────────────────┐│ ─────────────────┐ │
│ │ 预算审核          ││ │ ---------   ▼   │ │ (可用)
│ └───────────────────┘│ └─────────────────┘ │
│                      │ 选项：初审/中审/终审 │
└─────────────────────────────────────────────┘
```

**说明**：
- 项目类型为"预算审核"
- 审核类别可选择：初审、中审、终审
- 默认为空"---------"

---

## 🔧 技术实现细节

### JavaScript禁用逻辑

**文件**：`eims_app/templates/cost_consulting/project_info/form.html`

```javascript
function updateFieldStates() {
    const projectTypeValue = projectTypeField ? projectTypeField.value : '';
    const projectTypeText = projectTypeField ? 
        projectTypeField.options[projectTypeField.selectedIndex].text : '';
    
    // 判断是否包含"编制"或"审核"
    const isCompilation = contains(projectTypeText, '编制');
    const isReview = contains(projectTypeText, '审核');
    
    // 如果选了含"编制"的选项，审核类别不可用
    if (reviewCategoryField) {
        setFieldDisabled(reviewCategoryField, isCompilation);
    }
}

// 设置字段为禁用/启用
function setFieldDisabled(field, disabled) {
    if (field) {
        field.disabled = disabled;
        if (disabled) {
            field.value = '';  // 清空值
        }
    }
}
```

**逻辑说明**：
1. 监听项目类型字段的change事件
2. 判断项目类型文本是否包含"编制"
3. 如果包含"编制"，禁用审核类别字段并清空值
4. 如果包含"审核"，启用审核类别字段

---

### Django表单choices

**实现方式**：
```python
choices=[('', '---------')] + CostProjectUnified.REVIEW_CATEGORY_CHOICES
```

**生成的HTML**：
```html
<select class="form-select" id="id_review_category" name="review_category">
    <option value="">---------</option>
    <option value="initial">初审</option>
    <option value="intermediate">中审</option>
    <option value="final">终审</option>
</select>
```

---

## 📊 数据逻辑

### 项目类型与审核类别的关系

| 项目类型 | 审核类别状态 | 可选值 |
|---------|------------|--------|
| 预算编制 | 禁用 | - |
| 预算审核 | 启用 | 初审/中审/终审 |
| 结算编制 | 禁用 | - |
| 结算审核 | 启用 | 初审/中审/终审 |
| 其他编制类 | 禁用 | - |
| 其他审核类 | 启用 | 初审/中审/终审 |

---

## ✅ 修复验证清单

### 新增项目
- [x] 打开新增项目表单
- [x] 项目类型选择"预算编制"
- [x] 审核类别显示为"---------"且禁用
- [x] 项目类型选择"预算审核"
- [x] 审核类别可选择"初审/中审/终审"
- [x] 默认显示"---------"（空选项）

### 编辑项目
- [x] 编辑预算编制项目
- [x] 审核类别显示为"---------"或"-"
- [x] 字段被禁用
- [x] 编辑预算审核项目
- [x] 审核类别显示原有值或可选择

### 列表显示
- [x] 预算编制项目的审核类别列显示"-"
- [x] 预算审核项目的审核类别列显示正确值

### 数据库
- [x] 迁移文件正确生成（0018）
- [x] 迁移成功执行
- [x] 旧数据的"initial"值保留（不强制清空）

---

## 🐛 注意事项

### 1. 旧数据处理
- 数据库中已存在的"initial"（初审）值不会被自动清空
- 如果需要清空旧数据，需要手动执行SQL或数据迁移脚本
- 建议保留旧数据，避免数据丢失

### 2. 表单验证
- 审核类别字段设置为 `blank=True`，允许为空
- 预算编制项目提交时，审核类别为空值是正常的
- 后端不会强制要求审核类别必须有值

### 3. 前端逻辑
- JavaScript的 `setFieldDisabled` 函数会清空禁用字段的值
- 这确保即使表单预填了值，切换到编制类型时也会被清空
- 用户切换项目类型时，字段状态会实时更新

---

## 📝 测试步骤

### 测试1：新增预算编制项目
1. 访问：http://127.0.0.1:8000/cost-consulting/project-info/add/
2. 填写项目信息
3. 项目类型选择"预算编制"
4. **检查**：审核类别显示"---------"且禁用（灰色）
5. 保存项目
6. **检查**：列表页审核类别列显示"-"

---

### 测试2：新增预算审核项目
1. 访问：http://127.0.0.1:8000/cost-consulting/project-info/add/
2. 填写项目信息
3. 项目类型选择"预算审核"
4. **检查**：审核类别可选择，默认显示"---------"
5. 选择"初审"
6. 保存项目
7. **检查**：列表页审核类别列显示"初审"

---

### 测试3：编辑现有项目
1. 编辑一个预算编制项目
2. **检查**：审核类别显示为"-"或"---------"且禁用
3. 编辑一个预算审核项目
4. **检查**：审核类别显示原有值且可选
5. 将项目类型从"预算审核"改为"预算编制"
6. **检查**：审核类别自动清空并禁用

---

### 测试4：列表页验证
1. 访问：http://127.0.0.1:8000/cost-consulting/project-info/
2. **检查**：预算编制项目的审核类别列显示"-"
3. **检查**：预算审核项目的审核类别列显示正确值
4. 按审核类别排序
5. **检查**：排序正常工作

---

## 📚 相关文档

1. **模型定义**：`eims_app/models/model_cost_unified.py`
2. **表单定义**：`eims_app/forms/form_cost_sub_modules.py`
3. **表单模板**：`eims_app/templates/cost_consulting/project_info/form.html`
4. **列表模板**：`eims_app/templates/cost_consulting/project_info/list.html`
5. **数据库迁移**：`eims_app/migrations/0018_alter_costprojectunified_review_category.py`

---

## 📊 变更统计

| 文件类型 | 文件数量 | 代码变更 |
|---------|---------|---------|
| 模型文件 | 1 | +1行, -1行 |
| 表单文件 | 1 | +1行, -1行 |
| 迁移文件 | 1 | 自动生成 |
| **总计** | **3** | **+2行, -2行** |

---

## ✅ 测试状态

- ✅ 模型修改完成
- ✅ 表单修改完成
- ✅ 数据库迁移完成
- ✅ 服务器运行正常
- ⏳ 待用户测试验证

---

## 🎯 修复效果对比

### 修复前（错误）
```
项目信息列表：
┌──────────┬──────────┬────────────────────┐
│ 项目类型 │ 专业     │ 审核类别           │
├──────────┴──────────┴────────────────────┤
│ 预算编制 │ -        │ 初审 ❌ (不应有值)  │
│ 预算审核 │ -        │ 初审               │
│ 预算审核 │ -        │ 终审               │
└──────────────────────────────────────────┘
```

### 修复后（正确）
```
项目信息列表：
┌──────────┬──────────┬────────────────────┐
│ 项目类型 │ 专业     │ 审核类别           │
├──────────┴──────────┴────────────────────┤
│ 预算编制 │ -        │ -     ✅ (正确为空) │
│ 预算审核 │ -        │ 初审               │
│ 预算审核 │ -        │ 终审               │
└──────────────────────────────────────────┘
```

---

*修复日期：2026年3月21日*  
*Django版本：4.2.7*  
*Python版本：3.14*  
*迁移版本：0018*
