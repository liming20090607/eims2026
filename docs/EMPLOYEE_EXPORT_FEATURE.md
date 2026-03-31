# 人员花名册导出功能实现说明

## 功能概述

为人员花名册（员工信息管理）模块增加了完整的 Excel 导出功能，导出的数据与 `Employee` 模型的所有字段完全一致。

## 核心特性

✅ **完整字段导出**：包含模型定义的 24 个字段  
✅ **智能筛选**：根据当前筛选条件导出对应的数据  
✅ **格式优化**：中文表头、数值转换、日期格式化  
✅ **样式美化**：表格边框、列宽调整、首行冻结  

## 导出字段清单

### 基本信息（7 个字段）
| 序号 | 字段名 | 中文标签 | 数据类型 | 转换规则 |
|------|--------|----------|----------|----------|
| 1 | employee_code | 员工编号 | Char | 原值 |
| 2 | name | 姓名 | Char | 原值 |
| 3 | gender | 性别 | Integer | 0→男，1→女，2→其他 |
| 4 | id_card | 身份证号 | Char | 原值 |
| 5 | native_place | 籍贯 | Char | 原值 |
| 6 | ethnic | 民族 | Char | han→汉族，hui→回族等 |
| 7 | education | 学历 | Char | bachelor→本科等 |

### 联系方式（6 个字段）
| 序号 | 字段名 | 中文标签 | 数据类型 | 转换规则 |
|------|--------|----------|----------|----------|
| 8 | address | 住址 | Char | 原值（空→""） |
| 9 | home_phone | 固定电话 | Char | 原值（空→""） |
| 10 | mobile | 手机号 | Char | 原值 |
| 11 | emergency_contact | 应急联系人 | Char | 原值（空→""） |
| 12 | emergency_phone | 应急电话 | Char | 原值（空→""） |
| 13 | wechat | 微信 | Char | 原值（空→""） |

### 职务信息（5 个字段）
| 序号 | 字段名 | 中文标签 | 数据类型 | 转换规则 |
|------|--------|----------|----------|----------|
| 14 | admin_position | 行政职务 | Char | 原值（空→""） |
| 15 | tech_position | 技术职务 | Char | 原值（空→""） |
| 16 | professional_qualification | 执业资格 | Char | 原值（空→""） |
| 17 | professional_title | 职称 | Char | 原值（空→""） |
| 18 | job_qualification | 任职资格 | Char | 原值（空→""） |

### 时间信息（4 个字段）
| 序号 | 字段名 | 中文标签 | 数据类型 | 转换规则 |
|------|--------|----------|----------|----------|
| 19 | entry_time | 入职时间 | Date | YYYY-MM-DD |
| 20 | leave_time | 离职时间 | Date | YYYY-MM-DD |
| 21 | operator | 操作人 | Char | 原值（空→""） |
| 22 | create_time | 创建时间 | DateTime | YYYY-MM-DD HH:MM:SS |
| 23 | update_time | 更新时间 | DateTime | YYYY-MM-DD HH:MM:SS |
| 24 | remark | 备注 | Text | 原值（空→""） |

## 技术实现

### 1. 视图函数

**文件**: `eims_app/views/views_employee.py`

```python
@user_passes_test(is_superuser)
def employee_export(request):
    """导出员工信息为 Excel（包含模型所有字段）"""
    
    # 获取筛选参数
    search_key = request.GET.get('keyword', '')
    education = request.GET.get('education', '')
    ethnic = request.GET.get('ethnic', '')
    
    # 基础查询集（只导出未删除的）
    queryset = Employee.objects.filter(is_deleted=False).order_by('employee_code')
    
    # 应用筛选条件
    if search_key:
        queryset = queryset.filter(
            Q(name__icontains=search_key) |
            Q(employee_code__icontains=search_key) |
            Q(mobile__icontains=search_key) |
            Q(id_card__icontains=search_key) |
            Q(native_place__icontains=search_key) |
            Q(admin_position__icontains=search_key) |
            Q(tech_position__icontains=search_key)
        ).distinct()
    
    if education:
        queryset = queryset.filter(education=education)
    
    if ethnic:
        queryset = queryset.filter(ethnic=ethnic)
    
    # 创建工作簿
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "员工花名册"
    
    # 定义表头（24 个字段）
    headers = [
        '员工编号', '姓名', '性别', '身份证号', '籍贯', '民族', '学历',
        '住址', '固定电话', '手机号', '应急联系人', '应急电话', '微信',
        '行政职务', '技术职务', '执业资格', '职称', '任职资格',
        '入职时间', '离职时间',
        '操作人', '创建时间', '更新时间', '备注'
    ]
    
    # 设置表头样式
    header_font = Font(bold=True, size=11)
    header_alignment = Alignment(horizontal="center", vertical="center")
    thin_border = Border(...)
    
    # 写入表头
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.font = header_font
        cell.alignment = header_alignment
        cell.border = thin_border
    
    # 字段映射和选择字典
    field_mapping = {...}
    gender_dict = dict(Employee.GENDER_CHOICES)
    ethnic_dict = dict(Employee.ETHNIC_CHOICES)
    education_dict = dict(Employee.EDUCATION_CHOICES)
    
    # 填充数据行
    for row_idx, employee in enumerate(queryset, 2):
        # 逐列写入数据，处理选择字段和日期格式化
        ws.cell(row=row_idx, column=1, value=employee.employee_code or '')
        ws.cell(row=row_idx, column=2, value=employee.name or '')
        
        # 性别转换
        gender_value = gender_dict.get(employee.gender, employee.gender) if employee.gender is not None else ''
        ws.cell(row=row_idx, column=3, value=gender_value)
        
        # ... 其他字段类似处理
        
        # 设置整行样式
        for col_num in range(1, len(headers) + 1):
            cell = ws.cell(row=row_idx, column=col_num)
            cell.alignment = Alignment(horizontal="left", vertical="center")
            cell.border = thin_border
    
    # 调整列宽
    column_widths = [15, 12, 8, 20, ...]
    for col_idx, width in enumerate(column_widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(col_idx)].width = width
    
    # 冻结首行
    ws.freeze_panes = 'A2'
    
    # 写入内存并返回
    from io import BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    filename = f'员工花名册_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response
```

### 2. 路由配置

**文件**: `eims_app/urls.py`

```python
# 导入视图函数
from .views.views_employee import (
    employee_list, employee_add, employee_detail, 
    employee_edit, employee_delete, employee_batch_delete,
    employee_export
)

# 添加 URL 路由
path('employee/export/', employee_export, name='employee_export'),
```

### 3. 前端模板

**文件**: `eims_app/templates/employee/list.html`

```html
<div class="btn-group" role="group">
    <a href="{% url 'eims_app:employee_export' %}?{% if search_key %}keyword={{ search_key }}&{% endif %}{% if selected_education %}education={{ selected_education }}&{% endif %}{% if selected_ethnic %}ethnic={{ selected_ethnic }}&{% endif %}" class="btn btn-success">
        <i class="bi bi-file-earmark-excel"></i> 导出 Excel
    </a>
    <a href="{% url 'eims_app:employee_add' %}" class="btn btn-primary ms-2">
        <i class="bi bi-plus-circle"></i> 添加员工
    </a>
</div>
```

## 使用流程

### 场景 1：导出全部数据

```
1. 访问人员花名册页面：http://localhost:8000/employee/
   ↓
2. 点击"导出 Excel"按钮
   ↓
3. 浏览器下载文件：员工花名册_20260329_120000.xlsx
   ↓
4. 打开 Excel，查看所有员工记录（24 列）
```

### 场景 2：按条件筛选后导出

```
1. 访问人员花名册页面
   ↓
2. 输入搜索关键词："张三"
   ↓
3. 选择学历："本科"
   ↓
4. 点击"搜索"按钮
   ↓
5. 点击"导出 Excel"按钮
   ↓
6. 下载的 Excel 只包含：
      - 姓名包含"张三"的员工
      - 且学历为"本科"
```

## 关键参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 文件格式 | .xlsx | Excel 2007+ 格式 |
| 工作表名称 | 员工花名册 | Sheet 名称 |
| 总列数 | 24 列 | 对应模型 24 个字段 |
| 列宽 | 8-30 | 根据内容自动调整 |
| 冻结 | A2 | 冻结首行标题 |
| 文件名 | 员工花名册_YYYYMMDD_HHMMSS.xlsx | 带时间戳 |

## 数据转换规则

### 1. 选择字段转换

**性别** (gender):
```python
gender_dict = {0: '男', 1: '女', 2: '其他'}
gender_value = gender_dict.get(employee.gender, employee.gender)
```

**民族** (ethnic):
```python
ethnic_dict = {
    'han': '汉族',
    'hui': '回族',
    'man': '满族',
    'mongol': '蒙古族',
    'tibetan': '藏族',
    'uyghur': '维吾尔族',
    'other': '其他'
}
ethnic_value = ethnic_dict.get(employee.ethnic, employee.ethnic)
```

**学历** (education):
```python
education_dict = {
    'primary': '小学',
    'junior': '初中',
    'senior': '高中',
    'college': '大专',
    'bachelor': '本科',
    'master': '硕士',
    'doctor': '博士'
}
education_value = education_dict.get(employee.education, employee.education)
```

### 2. 日期字段格式化

**入职时间/离职时间**:
```python
entry_time_str = employee.entry_time.strftime('%Y-%m-%d') if employee.entry_time else ''
leave_time_str = employee.leave_time.strftime('%Y-%m-%d') if employee.leave_time else ''
```

**创建时间/更新时间**:
```python
create_time_str = employee.create_time.strftime('%Y-%m-%d %H:%M:%S') if employee.create_time else ''
update_time_str = employee.update_time.strftime('%Y-%m-%d %H:%M:%S') if employee.update_time else ''
```

### 3. 空值处理

所有可选字段（address, home_phone 等）如果为空，统一转换为空字符串：
```python
ws.cell(row=row_idx, column=8, value=employee.address or '')
```

## 样式设置

### 表头样式
```python
header_font = Font(bold=True, size=11)
header_alignment = Alignment(horizontal="center", vertical="center")
thin_border = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin")
)
```

### 数据行样式
```python
cell.alignment = Alignment(horizontal="left", vertical="center")
cell.border = thin_border
```

### 列宽配置
```python
column_widths = [
    15,  # 员工编号
    12,  # 姓名
    8,   # 性别
    20,  # 身份证号
    15,  # 籍贯
    8,   # 民族
    10,  # 学历
    30,  # 住址
    15,  # 固定电话
    15,  # 手机号
    12,  # 应急联系人
    15,  # 应急电话
    15,  # 微信
    20,  # 行政职务
    20,  # 技术职务
    25,  # 执业资格
    20,  # 职称
    25,  # 任职资格
    12,  # 入职时间
    12,  # 离职时间
    12,  # 操作人
    20,  # 创建时间
    20,  # 更新时间
    30,  # 备注
]
```

## 依赖库

```python
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side
from datetime import datetime
from io import BytesIO
```

确保已安装 openpyxl：
```bash
pip install openpyxl
```

## 权限控制

导出功能仅限超级管理员访问：
```python
@user_passes_test(is_superuser)
def employee_export(request):
    ...
```

## 筛选条件继承

导出时会保留当前的筛选条件：
```html
<a href="{% url 'eims_app:employee_export' %}?{% if search_key %}keyword={{ search_key }}&{% endif %}{% if selected_education %}education={{ selected_education }}&{% endif %}{% if selected_ethnic %}ethnic={{ selected_ethnic }}&{% endif %}">
```

支持的筛选参数：
- `keyword` - 搜索关键词（姓名/编号/手机号/身份证等）
- `education` - 学历筛选
- `ethnic` - 民族筛选

## 测试步骤

1. **访问页面**：
   ```
   http://localhost:8000/employee/
   ```

2. **点击导出按钮**：
   - 绿色按钮，带 Excel 图标
   - 位置：右上角，在"添加员工"左侧

3. **检查下载文件**：
   - 文件名：`员工花名册_20260329_120000.xlsx`
   - 文件大小：约 10-20KB（取决于数据量）

4. **打开 Excel 验证**：
   - ✅ 工作表名称：员工花名册
   - ✅ 表头：24 列，加粗居中，有边框
   - ✅ 数据行数：与数据库记录一致
   - ✅ 字段值：中文显示（性别/民族/学历）
   - ✅ 日期格式：YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS
   - ✅ 首行冻结：滚动时表头固定

5. **测试筛选导出**：
   - 输入搜索条件
   - 点击搜索
   - 点击导出
   - 验证 Excel 中只有筛选后的数据

## 对比旧版本

### 之前的问题
❌ 没有导出功能  
❌ 无法批量导出数据  
❌ 需要手动复制粘贴  

### 现在的优势
✅ 一键导出所有字段  
✅ 数据与模型完全一致  
✅ 支持筛选条件导出  
✅ 格式美观，可直接打印  
✅ 中文标签，易于理解  

## 相关文件清单

### 后端文件
- ✅ `eims_app/views/views_employee.py` - 新增 `employee_export()` 函数
- ✅ `eims_app/models/model_employee.py` - Employee 模型（已存在）

### 前端文件
- ✅ `eims_app/templates/employee/list.html` - 添加导出按钮

### 配置文件
- ✅ `eims_app/urls.py` - 添加 `/employee/export/` 路由

## 注意事项

### 1. 数据完整性
- 只导出 `is_deleted=False` 的记录（未删除的）
- 所有 24 个字段都会导出，包括系统字段（operator, create_time 等）

### 2. 性能考虑
- 如果数据量很大（>10000 条），导出可能需要几秒钟
- 建议先筛选再导出，减少文件大小

### 3. 浏览器兼容性
- 支持所有现代浏览器（Chrome, Firefox, Edge, Safari）
- IE 浏览器可能需要额外配置

### 4. 文件命名
- 文件名包含时间戳，避免重复覆盖
- 格式：`员工花名册_YYYYMMDD_HHMMSS.xlsx`

## 完成时间

2026 年 3 月 29 日

---

**开发者备注**：此导出功能完整实现了模型所有字段的导出，确保数据与数据库完全一致。支持智能筛选、格式转换和样式美化，满足日常办公需求。
