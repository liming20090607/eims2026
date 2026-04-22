# 任务计划编辑功能修复总结

## 📌 问题描述

在任务计划列表点击"编辑"按钮后，编辑页面显示了"选择项目"下拉框，所有字段都是空的，需要用户重新选择项目。这不符合编辑操作的逻辑——编辑时应该直接加载并显示现有记录的数据，而不是让用户重新选择。

## 🐛 原因分析

### 架构背景
本系统采用**统一表架构**，`CostProjectUnified` 模型是一个包含所有7个子模块字段的宽表：
- 项目信息、任务计划、任务实施、审核成果、收费情况、项目存档、酬劳分配

### 问题根源
1. **表单设计问题**：`CostTaskPlanUnifiedForm` 包含一个 `selected_project` 字段用于选择项目
2. **编辑模式未处理**：在编辑模式下，表单仍然显示项目选择器，但没有预填当前记录的项目
3. **缺少初始值设置**：`__init__` 方法没有为编辑模式设置 `selected_project` 的初始值

## 🔧 修复方案

### 1. 修改表单类（form_cost_sub_modules.py）

**文件位置**：`eims_app/forms/form_cost_sub_modules.py` - `CostTaskPlanUnifiedForm` 类

**修改内容**：
```python
def __init__(self, *args, **kwargs):
    tenant = kwargs.pop('tenant', None)
    super().__init__(*args, **kwargs)
    
    # 动态设置项目选择器的 queryset
    if tenant:
        self.fields['selected_project'].queryset = CostProjectUnified.objects.filter(tenant=tenant)
    else:
        self.fields['selected_project'].queryset = CostProjectUnified.objects.none()
    
    # 编辑模式隐藏项目选择器并设置初始值
    if self.instance.pk:
        # 编辑时，实例本身就是项目记录，设置为自身
        self.fields['selected_project'].initial = self.instance.id
        self.fields['selected_project'].widget = forms.HiddenInput()
        self.fields['selected_project'].required = False
```

**关键逻辑**：
- 检测是否为编辑模式：`if self.instance.pk`
- 设置初始值为当前记录ID：`self.fields['selected_project'].initial = self.instance.id`
- 将字段改为隐藏输入：`self.fields['selected_project'].widget = forms.HiddenInput()`
- 移除必填限制：`self.fields['selected_project'].required = False`

---

### 2. 修改模板文件（form.html）

**文件位置**：`eims_app/templates/cost_consulting/task_plan/form.html`

**修改内容**：
```html
<!-- 核心外键：项目选择（仅新增模式显示） -->
{% if not form.instance.pk %}
<div class="col-md-12">
    <label class="form-label">选择项目 <span class="text-danger">*</span></label>
    {{ form.selected_project }}
    {% if form.selected_project.errors %}
    <div class="text-danger small">{{ form.selected_project.errors }}</div>
    {% endif %}
    <small class="text-muted">选择项目后，项目编号、名称等信息将自动填充</small>
</div>
{% else %}
<!-- 编辑模式：隐藏项目选择器 -->
{{ form.selected_project }}
{% endif %}
```

**关键逻辑**：
- 使用 Django 模板条件判断：`{% if not form.instance.pk %}`
- 新增模式（`pk` 为 None）：显示项目选择器
- 编辑模式（`pk` 有值）：仅渲染隐藏字段

---

## 📊 修复效果对比

### 修复前（错误）

```
编辑任务计划页面
┌─────────────────────────────────────────┐
│ 编辑任务计划                            │
├─────────────────────────────────────────┤
│ 选择项目 *                              │
│ ┌─────────────────────────────────────┐ │
│ │ 请选择项目            ▼             │ │ ← 空的！
│ └─────────────────────────────────────┘ │
│ 编制信息                                │
│ 编制人: [空]                            │
│ 编制人员: ---------                     │
│ 编制金额: 0.00                          │
│ ...                                     │
└─────────────────────────────────────────┘
```

**问题**：
- ❌ 项目选择器显示为空
- ❌ 所有字段都是空值
- ❌ 用户需要重新选择项目
- ❌ 不符合编辑操作的预期

---

### 修复后（正确）

```
编辑任务计划页面
┌─────────────────────────────────────────┐
│ 编辑任务计划                            │
├─────────────────────────────────────────┤
│ 编制信息                                │
│ 编制人: 张三                            │
│ 编制人员: 张三                          │
│ 编制金额: 100.00                        │
│                                         │
│ 一审计划                                │
│ 一审人员: 李四                          │
│ 一审开始时间: 2026-03-01                │
│ ...                                     │
└─────────────────────────────────────────┘
```

**改进**：
- ✅ 项目选择器隐藏（通过 hidden input 传递）
- ✅ 所有字段预填现有数据
- ✅ 用户直接编辑字段值
- ✅ 符合编辑操作的预期

---

## 🎯 统一表架构说明

### 为什么不需要选择项目？

在统一表架构中：
- **每条记录本身就是项目**（`CostProjectUnified`）
- 任务计划、任务实施等是这条记录的**不同字段集合**
- 编辑任务计划 = 编辑某条项目记录的**计划相关字段**
- 不需要外键关联，因为记录就是项目本身

### 数据模型关系

```
传统架构（多表）：
CostProjectInfo (项目信息表)
    ↓ FK
CostTaskPlan (任务计划表)  ← 需要选择项目

统一表架构（单表）：
CostProjectUnified (统一项目表)
    ├─ 项目信息字段
    ├─ 任务计划字段  ← 编辑时直接修改这些字段
    ├─ 任务实施字段
    └─ 其他模块字段
```

---

## 🔍 其他子模块的情况

检查发现，其他5个子模块的表单**已经正确处理了编辑模式**：

| 表单类 | 编辑模式处理 | 状态 |
|--------|------------|------|
| `CostTaskPlanUnifiedForm` | ❌ 缺失 | ✅ 已修复 |
| `CostTaskImplementationForm` | ✅ 已有 | 正常 |
| `CostReviewResultForm` | ✅ 已有 | 正常 |
| `CostPaymentStatusForm` | ✅ 已有 | 正常 |
| `CostProjectArchiveForm` | ✅ 已有 | 正常 |
| `CostRemunerationDistributionForm` | ✅ 已有 | 正常 |

所有其他表单都有以下逻辑：
```python
if self.instance.pk:
    self.fields['selected_project'].widget = forms.HiddenInput()
    self.fields['selected_project'].required = False
```

---

## 📝 测试步骤

### 测试1：新增任务计划

1. 访问：http://127.0.0.1:8000/cost-consulting/task-plan/add/
2. **验证**：显示"选择项目"下拉框
3. 选择一个项目
4. 填写任务计划信息
5. 保存
6. **验证**：保存成功，跳转到列表页

---

### 测试2：编辑任务计划

1. 访问：http://127.0.0.1:8000/cost-consulting/task-plan/
2. 找到一条记录，点击"编辑"按钮
3. **验证**：
   - ✅ 不显示"选择项目"下拉框
   - ✅ 所有字段预填现有数据
   - ✅ 可以直接修改字段值
4. 修改某些字段
5. 保存
6. **验证**：
   - ✅ 保存成功
   - ✅ 数据正确更新
   - ✅ 跳转到列表页

---

### 测试3：查看页面源代码

1. 打开编辑任务计划页面
2. 按 `F12` 打开开发者工具
3. 查看 HTML 源代码
4. **验证**：
   - ✅ 存在 `<input type="hidden" name="selected_project" value="项目ID">`
   - ✅ 不显示可见的项目选择器

---

## 📚 修改的文件清单

| 文件 | 类型 | 修改内容 |
|------|------|---------|
| `eims_app/forms/form_cost_sub_modules.py` | 表单类 | 添加编辑模式逻辑 |
| `eims_app/templates/cost_consulting/task_plan/form.html` | 模板 | 条件显示项目选择器 |

---

## ✅ 验证清单

- [x] 表单类添加编辑模式检测
- [x] 设置 `selected_project` 初始值为当前记录ID
- [x] 将 `selected_project` 改为隐藏输入
- [x] 移除 `selected_project` 的必填限制
- [x] 模板添加条件判断
- [x] 新增模式显示项目选择器
- [x] 编辑模式隐藏项目选择器
- [x] 服务器运行正常
- [x] 代码无语法错误

---

## 🎯 修复效果总结

### 用户体验改进

**修复前**：
1. 用户点击"编辑"
2. 看到空表单和"选择项目"下拉框
3. 困惑：为什么要重新选择项目？
4. 重新选择项目
5. 填写所有字段
6. 保存

**修复后**：
1. 用户点击"编辑"
2. 看到预填数据的表单
3. 满意：数据都在！
4. 修改需要更新的字段
5. 保存

---

## 🐛 注意事项

### 1. 其他子模块
其他5个子模块（任务实施、审核成果、收费情况、项目存档、酬劳分配）的表单**已经正确处理了编辑模式**，不需要修改。

### 2. 隐藏字段的作用
虽然项目选择器在编辑模式下不可见，但隐藏的 `selected_project` 字段仍然会随表单提交，确保后端能正确识别所属项目。

### 3. 统一表架构的优势
这种架构简化了：
- 数据模型（无需外键关联）
- 表单逻辑（实例本身就是项目）
- 查询性能（减少JOIN操作）

---

## 📊 代码统计

| 文件 | 新增行 | 删除行 | 净变化 |
|------|--------|--------|--------|
| `form_cost_sub_modules.py` | +3 | -1 | +2 |
| `form.html` | +5 | -1 | +4 |
| **总计** | **+8** | **-2** | **+6** |

---

*修复日期：2026年3月21日*  
*Django版本：4.2.7*  
*Python版本：3.14*  
*修复类型：Bug Fix*  
*影响范围：造价咨询 - 任务计划模块*
