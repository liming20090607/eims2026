# 人员花名册导出功能增强说明

## 更新概述

在原有导出功能基础上，增加了"导出所选"功能，并将原按钮更名为"导出全部"。现在支持两种导出模式：
1. **导出全部**：导出所有符合筛选条件的员工信息
2. **导出所选**：只导出用户手动勾选的员工信息

## 新增功能

### 1. 按钮布局

在原"导出"按钮右侧添加了新的"导出所选"按钮：

```
┌─────────────────────────────────────────────────┐
│  员工信息管理                                    │
│                                                  │
│  [📊 导出全部] [📊 导出所选] [+ 添加员工]        │
└─────────────────────────────────────────────────┘
```

**按钮说明**：
- **导出全部**（绿色）：导出当前筛选条件下的所有员工记录
- **导出所选**（绿色）：导出用户手动勾选的员工记录
- **添加员工**（蓝色）：添加新员工

### 2. JavaScript 函数

新增了 `exportSelected()` 函数：

```javascript
function exportSelected() {
    const checkboxes = document.querySelectorAll('.item-checkbox:checked');
    
    // 检查是否选择了员工
    if (checkboxes.length === 0) {
        alert('请至少选择一个员工才能导出！');
        return;
    }
    
    // 创建临时表单
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '{% url "eims_app:employee_export" %}';
    
    // 添加 CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfToken) {
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = csrfToken.value;
        form.appendChild(csrfInput);
    }
    
    // 添加选中的 ID
    checkboxes.forEach(cb => {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'employee_ids';
        input.value = cb.value;
        form.appendChild(input);
    });
    
    document.body.appendChild(form);
    form.submit();
    
    // 清理表单
    setTimeout(() => {
        document.body.removeChild(form);
    }, 1000);
}
```

### 3. 视图函数增强

修改了 `employee_export()` 视图函数，支持 POST 请求和 ID 列表：

```python
@user_passes_test(is_superuser)
def employee_export(request):
    """导出员工信息为 Excel - 支持全部导出或按 ID 列表导出"""
    
    # 获取筛选参数
    search_key = request.GET.get('keyword', '')
    education = request.GET.get('education', '')
    ethnic = request.GET.get('ethnic', '')
    
    # 获取选中的 ID 列表（POST 请求）
    selected_ids = None
    if request.method == 'POST':
        selected_ids = request.POST.getlist('employee_ids')
    
    # 基础查询集
    queryset = Employee.objects.filter(is_deleted=False).order_by('employee_code')
    
    # 如果有选中的 ID，只导出这些
    if selected_ids:
        queryset = queryset.filter(id__in=selected_ids)
    else:
        # 否则应用筛选条件
        if search_key:
            queryset = queryset.filter(
                Q(name__icontains=search_key) | ...
            ).distinct()
        
        if education:
            queryset = queryset.filter(education=education)
        
        if ethnic:
            queryset = queryset.filter(ethnic=ethnic)
    
    # ... 后续 Excel 生成代码不变
```

## 使用流程

### 场景 1：导出全部（原有功能）

```
1. 访问人员花名册页面
   ↓
2. （可选）输入筛选条件并搜索
   ↓
3. 点击"导出全部"按钮
   ↓
4. 下载 Excel 文件，包含所有符合筛选条件的记录
```

**特点**：
- 导出当前筛选条件下的**所有**记录
- 不需要手动选择
- 适合批量导出

### 场景 2：导出所选（新增功能）

```
1. 访问人员花名册页面
   ↓
2. 勾选需要导出的员工（复选框）
   ↓
3. 点击"导出所选"按钮
   ↓
4. 下载 Excel 文件，只包含勾选的记录
```

**特点**：
- 只导出**手动勾选**的记录
- 不受筛选条件限制
- 适合精准导出特定人员

## 字段完整性

### 导出的 24 个字段（完全一致）

无论使用"导出全部"还是"导出所选"，都会导出模型的所有字段：

| 类别 | 字段数量 | 字段列表 |
|------|----------|----------|
| 基本信息 | 7 | 员工编号、姓名、性别、身份证号、籍贯、民族、学历 |
| 联系方式 | 6 | 住址、固定电话、手机号、应急联系人、应急电话、微信 |
| 职务信息 | 5 | 行政职务、技术职务、执业资格、职称、任职资格 |
| 时间信息 | 6 | 入职时间、离职时间、操作人、创建时间、更新时间、备注 |
| **总计** | **24** | ✅ 全部字段 |

### 数据转换规则

**选择字段自动转换为中文**：
- 性别：`0 → 男`, `1 → 女`, `2 → 其他`
- 民族：`han → 汉族`, `hui → 回族`, etc.
- 学历：`bachelor → 本科`, `master → 硕士`, etc.

**日期字段格式化**：
- 入职/离职时间：`YYYY-MM-DD`
- 创建/更新时间：`YYYY-MM-DD HH:MM:SS`

**空值处理**：
- 所有空字段显示为空字符串（不是"None"或"null"）

## 技术实现细节

### 1. HTML 结构

```html
<div class="btn-group" role="group">
    <!-- 导出全部按钮 -->
    <a href="{% url 'eims_app:employee_export' %}?..." 
       class="btn btn-success" 
       id="exportAllBtn">
        <i class="bi bi-file-earmark-excel"></i> 导出全部
    </a>
    
    <!-- 导出所选按钮 -->
    <button type="button" 
            class="btn btn-success ms-2" 
            id="exportSelectedBtn" 
            onclick="exportSelected()">
        <i class="bi bi-file-earmark-excel"></i> 导出所选
    </button>
    
    <!-- 添加员工按钮 -->
    <a href="{% url 'eims_app:employee_add' %}" 
       class="btn btn-primary ms-2">
        <i class="bi bi-plus-circle"></i> 添加员工
    </a>
</div>
```

### 2. 表单提交机制

**导出全部**：GET 请求
```
GET /employee/export/?keyword=张三&education=bachelor
```

**导出所选**：POST 请求
```
POST /employee/export/
Content-Type: application/x-www-form-urlencoded

csrfmiddlewaretoken=xxx&employee_ids=1&employee_ids=3&employee_ids=5
```

### 3. 视图逻辑分支

```python
if request.method == 'POST':
    # 导出所选模式
    selected_ids = request.POST.getlist('employee_ids')
    queryset = Employee.objects.filter(id__in=selected_ids)
else:
    # 导出全部模式
    queryset = Employee.objects.filter(is_deleted=False)
    # 应用 GET 参数中的筛选条件
    if search_key:
        queryset = queryset.filter(...)
```

## 对比表格

| 特性 | 导出全部 | 导出所选 |
|------|----------|----------|
| 请求方式 | GET | POST |
| 数据来源 | 筛选条件 | 手动勾选 |
| 参数传递 | URL 参数 | POST 表单 |
| 适用场景 | 批量导出 | 精准导出 |
| 是否需要选择 | ❌ 否 | ✅ 是 |
| 受筛选影响 | ✅ 是 | ❌ 否 |
| 按钮类型 | `<a>` 链接 | `<button>` 按钮 |

## 修改的文件

### 1. 视图文件
**文件**: `eims_app/views/views_employee.py`

**修改内容**:
- ✅ 增加 POST 请求处理逻辑
- ✅ 增加 `selected_ids` 参数获取
- ✅ 增加 ID 过滤逻辑
- ✅ 修改函数文档字符串

**代码行数变化**: +9 行

### 2. 模板文件
**文件**: `eims_app/templates/employee/list.html`

**修改内容**:
- ✅ 修改原按钮文字："导出 Excel" → "导出全部"
- ✅ 新增"导出所选"按钮
- ✅ 新增 `exportSelected()` JavaScript 函数
- ✅ 添加按钮 ID 属性

**代码行数变化**: +46 行

## 测试步骤

### 测试"导出全部"

1. **访问页面**：
   ```
   http://localhost:8000/employee/
   ```

2. **不选择任何员工**

3. **点击"导出全部"按钮**

4. **验证结果**：
   - ✅ 下载 Excel 文件
   - ✅ 包含所有员工记录
   - ✅ 24 个字段齐全

### 测试"导出所选"

1. **访问页面**：
   ```
   http://localhost:8000/employee/
   ```

2. **勾选 2-3 个员工**（复选框）

3. **点击"导出所选"按钮**

4. **验证结果**：
   - ✅ 下载 Excel 文件
   - ✅ 只包含勾选的员工记录
   - ✅ 24 个字段齐全
   - ✅ 记录数 = 勾选数

### 测试边界情况

1. **未选择员工时点击"导出所选"**：
   ```
   预期：弹出提示"请至少选择一个员工才能导出！"
   ```

2. **全选后点击"导出所选"**：
   ```
   预期：导出所有可见的员工记录
   ```

3. **跨页选择后点击"导出所选"**：
   ```
   注意：只能导出当前页面的勾选记录
   原因：分页后复选框会重置
   ```

## 注意事项

### 1. CSRF Token

导出所选功能需要 CSRF token，通过 JavaScript 动态获取：
```javascript
const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
```

确保页面中有 CSRF token（通常在表单中）。

### 2. 复选框名称

复选框的 name 必须是 `employee_ids`，与视图函数中的参数一致：
```html
<input type="checkbox" name="employee_ids" value="{{ employee.id }}" class="item-checkbox">
```

### 3. 文件大小

- **导出全部**：可能生成大文件（如果数据量大）
- **导出所选**：文件大小取决于选择的数量

建议：如果数据量很大（>1000 条），先筛选再导出所选。

### 4. 浏览器兼容性

- Chrome ✅
- Firefox ✅
- Edge ✅
- Safari ✅

### 5. 性能考虑

- 导出全部：服务器需要查询数据库
- 导出所选：服务器直接按 ID 查询，速度更快

## 优势分析

### 相比之前版本

| 方面 | 之前 | 现在 |
|------|------|------|
| 导出方式 | 仅全部导出 | 全部导出 + 所选导出 |
| 精准度 | 低（只能全量） | 高（可精确到个人） |
| 灵活性 | 一般 | 优秀 |
| 用户体验 | 好 | 更好 |

### 实际应用场景

**场景 1：月度统计**
- 需求：导出所有本月入职的员工
- 方案：搜索"本月" → 导出全部

**场景 2：部门报表**
- 需求：导出特定几个人的信息
- 方案：勾选目标人员 → 导出所选

**场景 3：证书年审**
- 需求：导出证书即将到期的人员
- 方案：筛选 → 勾选 → 导出所选

## 完成时间

2026 年 3 月 29 日

---

**开发者备注**：此增强功能在保留原有"导出全部"功能的基础上，新增了更灵活的"导出所选"功能，满足了用户对特定人员进行精准导出的需求。两种方式互为补充，提升了系统的易用性。
