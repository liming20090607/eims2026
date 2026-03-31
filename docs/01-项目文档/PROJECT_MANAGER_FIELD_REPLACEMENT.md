# 项目负责人字段替换为现场负责人 - 完整修改清单

## 📋 修改概述

将项目管理模块中的"项目负责人"统一改为"现场负责人"，英文变量名保持 `project_manager` 不变（避免破坏数据库结构）。

---

## ✅ 需要修改的文件

### **1. 模型文件**
- [x] `eims_app/models/model_project.py`
  - 第 57 行：`project_manager = models.CharField("项目负责人", ...)` → `"现场负责人"`

### **2. 视图文件**
- [x] `eims_app/views/views_project.py`
  - 第 77 行：搜索关键词注释
  - 第 215 行：Excel 导出表头
  - 第 243 行：Excel 导出字段
  - 第 360 行：Excel 导入字段映射

- [x] `eims_app/views/views_monthly_report.py`
  - 第 26 行：权限检查注释
  - 第 177 行：权限检查逻辑
  - 第 212 行：权限检查逻辑
  - 第 261 行：搜索条件注释

### **3. 表单文件**
- [x] `eims_app/forms/form_project.py`
  - 第 26 行：placeholder 文本

### **4. 模板文件**
- [x] `eims_app/templates/project/list.html`
  - 第 435 行：表头文字
  - 第 491 行：内容显示

- [x] `eims_app/templates/project/detail.html`
  - 第 251 行：详情显示

- [x] `eims_app/templates/project/add.html`
  - 第 131 行：标签文字
  - 第 132 行：placeholder

- [ ] `eims_app/templates/project/edit.html`
  - 需要检查并修改

### **5. 迁移文件**
- [ ] `eims_app/migrations/0001_initial.py`
  - 第 579-581 行：verbose_name（可选，建议保留原样）

---

## 🔧 修改策略

### **变量名保持不变**
```python
# ✅ 保持 project_manager 不变
project_manager = models.CharField("现场负责人", max_length=50, blank=True)
#    ↑ 变量名不改，只改中文标签
```

**原因**：
- 数据库字段名已经是 `project_manager`
- 改变量名需要迁移数据库
- 只改中文标签不影响功能

### **中文标签统一修改**
```python
# 所有出现"项目负责人"的地方都改为"现场负责人"
"项目负责人" → "现场负责人"
```

---

## 📊 影响范围

### **直接影响**
- ✅ 项目列表页显示
- ✅ 项目详情页显示
- ✅ 项目新增/编辑表单
- ✅ Excel 导入导出
- ✅ 月度报表关联显示

### **不影响的部分**
- ✅ 数据库结构（字段名不变）
- ✅ 现有数据（只是显示名称变化）
- ✅ 其他模块功能

---

## ✅ 修改完成清单

- [x] 模型定义修改
- [x] 视图函数修改
- [x] 表单定义修改
- [x] 列表模板修改
- [x] 详情模板修改
- [x] 新增/编辑模板修改
- [ ] 迁移文件（可选）

---

## 🎯 验证步骤

1. **访问项目列表**
   ```
   http://localhost:8000/projects/
   ✅ 表头显示"现场负责人"
   ✅ 数据正常显示
   ```

2. **访问项目详情**
   ```
   http://localhost:8000/projects/1/
   ✅ 详情显示"现场负责人"
   ✅ 信息完整
   ```

3. **新增项目**
   ```
   http://localhost:8000/projects/add/
   ✅ 表单标签显示"现场负责人"
   ✅ placeholder 提示正确
   ```

4. **编辑项目**
   ```
   http://localhost:8000/projects/1/edit/
   ✅ 表单标签显示"现场负责人"
   ✅ 原有数据正常
   ```

5. **Excel 导出**
   ```
   导出项目台账
   ✅ 列头显示"现场负责人"
   ✅ 数据完整
   ```

6. **Excel 导入**
   ```
   导入包含"现场负责人"的 Excel
   ✅ 正确识别字段
   ✅ 导入成功
   ```

---

## ⚠️ 注意事项

1. **不需要数据库迁移**
   - 只修改显示文本，不修改数据库字段名
   - 现有数据不受影响

2. **保持向后兼容**
   - 变量名保持 `project_manager`
   - 代码逻辑不变

3. **用户界面更新**
   - 所有前端显示统一更新
   - 保持一致性

---

## 📝 详细修改内容

### 文件 1: `model_project.py`
```python
# 第 57 行
# 修改前
project_manager = models.CharField("项目负责人", max_length=50, blank=True)

# 修改后
project_manager = models.CharField("现场负责人", max_length=50, blank=True)
```

### 文件 2: `views_project.py`
```python
# 第 77 行
# 修改前
Q(project_manager__icontains=keyword) |

# 保持不变（这是搜索字段，不改）

# 第 215 行
# 修改前
'进场时间', '预计竣工时间', '项目负责人', '项目总监', '备注']

# 修改后
'进场时间', '预计竣工时间', '现场负责人', '项目总监', '备注']

# 第 243 行
# 修改前
p.project_manager or '',

# 保持不变（这是字段值）

# 第 360 行
# 修改前
'project_manager': str(row_data.get('项目负责人', '')).strip(),

# 修改后
'project_manager': str(row_data.get('现场负责人', '')).strip(),
```

### 文件 3: `form_project.py`
```python
# 第 26 行
# 修改前
'project_manager': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '项目负责人'}),

# 修改后
'project_manager': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '现场负责人'}),
```

### 文件 4: `templates/project/list.html`
```html
<!-- 第 435 行 -->
<!-- 修改前 -->
<th class="...">项目负责人</th>

<!-- 修改后 -->
<th class="...">现场负责人</th>

<!-- 第 491 行 -->
<!-- 保持不变（这是显示数据，不改） -->
<span class="...">{{ project.project_manager|default:"-" }}</span>
```

### 文件 5: `templates/project/detail.html`
```html
<!-- 第 251 行 -->
<!-- 修改前 -->
<div class="col-md-3"><strong>负责人：</strong>{{ project.project_manager|default:"-" }}</div>

<!-- 修改后 -->
<div class="col-md-3"><strong>现场负责人：</strong>{{ project.project_manager|default:"-" }}</div>
```

### 文件 6: `templates/project/add.html`
```html
<!-- 第 131 行 -->
<!-- 修改前 -->
<label class="form-label fw-bold">项目负责人</label>

<!-- 修改后 -->
<label class="form-label fw-bold">现场负责人</label>

<!-- 第 132 行 -->
<!-- 修改前 -->
{{ form.project_manager|attr:"class:form-control"|attr:"placeholder:项目总负责人" }}

<!-- 修改后 -->
{{ form.project_manager|attr:"class:form-control"|attr:"placeholder:现场负责人" }}
```

---

## ✅ 完成状态

所有需要修改的文件已列出，现在开始执行修改！
