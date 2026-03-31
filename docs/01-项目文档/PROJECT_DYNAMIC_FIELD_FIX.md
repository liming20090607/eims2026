# 项目动态字段修复

## 🐛 问题描述

在测试"新增项目动态"功能时出现错误：

```
TypeError at /project_ledger/1/add-dynamic/
ProjectDynamic() got unexpected keyword arguments: 'contract_status', 'risk_or_problem', 'solution_suggestion'
```

**原因**: `add_dynamic` 视图函数和模板中使用了不存在的字段名，而 `ProjectDynamic` 模型中实际并没有这些字段。

---

## 🔍 问题分析

### **错误代码位置**

**文件**: `e:\EIMS2026\eims_app\views\views_project.py` (第 536-565 行)

**错误代码**:
```python
dynamic = ProjectDynamic(
    project=project,
    project_code=project.project_code,
    project_progress=request.POST.get('project_progress', ''),
    project_status=request.POST.get('project_status', ''),
    contract_status=request.POST.get('contract_status', ''),      # ❌ 不存在的字段
    risk_or_problem=request.POST.get('risk_or_problem', ''),      # ❌ 不存在的字段
    solution_suggestion=request.POST.get('solution_suggestion', ''), # ❌ 不存在的字段
    operator=request.user.username
)
```

---

## ✅ 解决方案

### **1. 查看模型实际字段**

**文件**: `e:\EIMS2026\eims_app\models\model_project_dynamic.py`

**实际字段**:
```python
class ProjectDynamic(BaseModel):
    project = models.ForeignKey('ProjectDetail', on_delete=models.CASCADE)
    project_code = models.CharField(max_length=50)
    
    project_progress = models.CharField(max_length=100, blank=True, verbose_name='项目进度')
    project_status = models.CharField(max_length=20, choices=PROJECT_STATUS_CHOICES, blank=True, verbose_name='项目状态')
    
    notice_entry = models.DateField(blank=True, null=True, verbose_name='通知进场')
    delay_status = models.CharField(max_length=200, blank=True, verbose_name='延期情况')
    
    planned_start_time = models.DateField(blank=True, null=True, verbose_name='计划开工时间')
    actual_start_time = models.DateField(blank=True, null=True, verbose_name='实际开工时间')
    planned_completion = models.DateField(blank=True, null=True, verbose_name='预计竣工时间')
    
    personnel_change = models.CharField(max_length=200, blank=True, verbose_name='本月人员变动')
    
    operator = models.CharField(max_length=100, blank=True, verbose_name='操作人')
    remark = models.TextField(blank=True, verbose_name='备注')
```

**PROJECT_STATUS_CHOICES**:
```python
PROJECT_STATUS_CHOICES = [
    ('not_started', '未开工'),
    ('normal_construction', '正常施工'),
    ('stopped', '在停工'),
    ('completed', '已完工')
]
```

---

### **2. 修复视图函数**

**文件**: `e:\EIMS2026\eims_app\views\views_project.py`

**修改后代码**:
```python
@login_required
@user_passes_test(is_superuser)
def add_dynamic(request, pk):
    """添加项目动态 - 新页面"""
    from eims_app.models.model_project_dynamic import ProjectDynamic
    from eims_app.models.model_project_detail import ProjectDetail
    
    project = get_object_or_404(ProjectDetail, pk=pk)
    
    if request.method == 'POST':
        dynamic = ProjectDynamic(
            project=project,
            project_code=project.project_code,
            project_progress=request.POST.get('project_progress', ''),
            project_status=request.POST.get('project_status', ''),
            notice_entry=parse_date(request.POST.get('notice_entry')),           # ✅ 使用正确的字段
            delay_status=request.POST.get('delay_status', ''),                   # ✅ 使用正确的字段
            planned_start_time=parse_date(request.POST.get('planned_start_time')), # ✅ 使用正确的字段
            actual_start_time=parse_date(request.POST.get('actual_start_time')),   # ✅ 使用正确的字段
            planned_completion=parse_date(request.POST.get('planned_completion')), # ✅ 使用正确的字段
            personnel_change=request.POST.get('personnel_change', ''),             # ✅ 使用正确的字段
            operator=request.user.username
        )
        dynamic.save()
        messages.success(request, '成功添加项目动态')
        return redirect('eims_app:project_ledger_detail', pk=pk)
    
    context = {
        'project': project,
    }
    return render(request, 'project_ledger/add_dynamic.html', context)
```

**变更说明**:
- ❌ 删除：`contract_status`, `risk_or_problem`, `solution_suggestion`
- ✅ 新增：`notice_entry`, `delay_status`, `planned_start_time`, `actual_start_time`, `planned_completion`, `personnel_change`
- ✅ 使用 `parse_date()` 处理日期字段

---

### **3. 修复 HTML 模板**

**文件**: `e:\EIMS2026\eims_app\templates\project_ledger\add_dynamic.html`

#### **变更前** (错误的字段):
```html
<div class="row mb-3">
    <div class="col-md-6">
        <label class="form-label">项目进度 <span class="text-danger">*</span></label>
        <input type="text" class="form-control" name="project_progress" required>
    </div>
    <div class="col-md-6">
        <label class="form-label">项目状态 <span class="text-danger">*</span></label>
        <select class="form-select" name="project_status" required>
            <option value="">请选择状态</option>
            <option value="planning">筹备中</option>
            <option value="in_progress">进行中</option>
            <option value="delayed">延期</option>
            <option value="completed">已完成</option>
            <option value="suspended">暂停</option>
        </select>
    </div>
</div>

<div class="row mb-3">
    <div class="col-md-6">
        <label class="form-label">合同状态 <span class="text-danger">*</span></label>
        <select class="form-select" name="contract_status" required>
            <option value="">请选择状态</option>
            <option value="normal">正常</option>
            <option value="warning">预警</option>
            <option value="risk">风险</option>
            <option value="dispute">纠纷</option>
        </select>
    </div>
    <div class="col-md-6">
        <label class="form-label">风险或问题</label>
        <textarea class="form-control" name="risk_or_problem" rows="3"></textarea>
    </div>
</div>

<div class="mb-3">
    <label class="form-label">解决建议</label>
    <textarea class="form-control" name="solution_suggestion" rows="3"></textarea>
</div>
```

#### **修改后** (正确的字段):
```html
<div class="row mb-3">
    <div class="col-md-6">
        <label class="form-label">项目进度 <span class="text-danger">*</span></label>
        <input type="text" class="form-control" name="project_progress" required 
               placeholder="如：地基施工中/主体封顶/装修阶段">
    </div>
    <div class="col-md-6">
        <label class="form-label">项目状态 <span class="text-danger">*</span></label>
        <select class="form-select" name="project_status" required>
            <option value="">请选择状态</option>
            <option value="not_started">未开工</option>
            <option value="normal_construction">正常施工</option>
            <option value="stopped">在停工</option>
            <option value="completed">已完工</option>
        </select>
    </div>
</div>

<div class="row mb-3">
    <div class="col-md-4">
        <label class="form-label">通知进场日期</label>
        <input type="date" class="form-control" name="notice_entry">
    </div>
    <div class="col-md-8">
        <label class="form-label">延期情况</label>
        <textarea class="form-control" name="delay_status" rows="2" placeholder="描述延期情况"></textarea>
    </div>
</div>

<div class="row mb-3">
    <div class="col-md-4">
        <label class="form-label">计划开工时间</label>
        <input type="date" class="form-control" name="planned_start_time">
    </div>
    <div class="col-md-4">
        <label class="form-label">实际开工时间</label>
        <input type="date" class="form-control" name="actual_start_time">
    </div>
    <div class="col-md-4">
        <label class="form-label">预计竣工时间</label>
        <input type="date" class="form-control" name="planned_completion">
    </div>
</div>

<div class="mb-3">
    <label class="form-label">本月人员变动</label>
    <textarea class="form-control" name="personnel_change" rows="2" placeholder="如：新增 3 人/离职 1 人"></textarea>
</div>
```

**变更说明**:
- ❌ 删除字段：合同状态、风险或问题、解决建议
- ✅ 新增字段：通知进场日期、延期情况、计划开工时间、实际开工时间、预计竣工时间、本月人员变动
- ✅ 更新项目状态选项为模型定义的选项

---

## 📊 字段对照表

| 原错误字段 | 修正后字段 | 字段类型 | 必填 | 说明 |
|-----------|-----------|---------|------|------|
| contract_status | notice_entry | DateField | 否 | 通知进场日期 |
| risk_or_problem | delay_status | CharField | 否 | 延期情况描述 |
| solution_suggestion | planned_start_time | DateField | 否 | 计划开工时间 |
| - | actual_start_time | DateField | 否 | 实际开工时间 |
| - | planned_completion | DateField | 否 | 预计竣工时间 |
| - | personnel_change | CharField | 否 | 本月人员变动 |

**保留字段**:
- ✅ `project_progress` - 项目进度（必填）
- ✅ `project_status` - 项目状态（必填）

---

## 🎯 现在的表单结构

### **项目基本信息（只读）**
- 项目编号 - 自动填充
- 项目名称 - 自动填充

### **项目动态信息**
**必填项**:
- 项目进度 - 文本输入（如：地基施工中/主体封顶/装修阶段）
- 项目状态 - 下拉选择（未开工/正常施工/在停工/已完工）

**可选项**:
- 通知进场日期 - 日期选择器
- 延期情况 - 多行文本
- 计划开工时间 - 日期选择器
- 实际开工时间 - 日期选择器
- 预计竣工时间 - 日期选择器
- 本月人员变动 - 多行文本（如：新增 3 人/离职 1 人）

---

## ✅ 测试验证

### **测试步骤**:
1. 访问项目详情页：`http://127.0.0.1:8000/project_ledger/1/`
2. 点击"项目动态"子窗体右上角的 **"+ 新增"** 按钮
3. 填写表单：
   - 项目进度：`地基施工中`
   - 项目状态：`正常施工`
   - 通知进场日期：`2026-03-01`
   - 计划开工时间：`2026-03-10`
   - 预计竣工时间：`2026-12-31`
   - 本月人员变动：`新增监理员 2 名`
4. 点击"保存"

### **预期结果**:
- ✅ 成功保存记录
- ✅ 显示成功消息："成功添加项目动态"
- ✅ 自动跳转到项目详情页
- ✅ 项目动态列表中显示新添加的记录

---

## 📝 注意事项

### **1. 模型字段一致性**
在创建或修改表单功能时，必须确保：
- ✅ 视图函数中使用的字段与模型定义一致
- ✅ 模板中的 `name` 属性与视图函数期望的参数一致
- ✅ 字段类型匹配（日期字段用 `parse_date()` 处理）

### **2. 状态选项**
项目状态的选项必须与模型中的 `PROJECT_STATUS_CHOICES` 一致：
- `not_started` - 未开工
- `normal_construction` - 正常施工
- `stopped` - 在停工
- `completed` - 已完工

**不要使用**未在模型中定义的选项值（如 `planning`, `in_progress`, `delayed` 等）。

### **3. 日期处理**
所有日期字段都需要使用 `parse_date()` 工具函数处理：
```python
from utils.helpers import parse_date

# 在视图中
notice_entry = parse_date(request.POST.get('notice_entry'))
planned_start_time = parse_date(request.POST.get('planned_start_time'))
```

---

## 🔧 相关文件

### **修改的文件**:
1. `e:\EIMS2026\eims_app\views\views_project.py` (第 536-565 行)
   - 修复 `add_dynamic` 视图函数

2. `e:\EIMS2026\eims_app\templates\project_ledger\add_dynamic.html` (第 88-151 行)
   - 修复表单字段和选项

### **参考文件**:
1. `e:\EIMS2026\eims_app\models\model_project_dynamic.py`
   - `ProjectDynamic` 模型定义

2. `e:\EIMS2026\utils\helpers.py`
   - `parse_date()` 工具函数

---

## 💡 经验教训

### **教训**:
在实现新功能时，应该：
1. ✅ **首先查看模型定义**，了解实际可用的字段
2. ✅ **不要假设字段名**，以模型为准
3. ✅ **检查 Choice 字段**的可选值
4. ✅ **保持视图、模板、模型三者一致**

### **最佳实践**:
```python
# 正确做法
# 1. 先查看模型
from eims_app.models.model_project_dynamic import ProjectDynamic

# 2. 确认字段
print(ProjectDynamic._meta.get_fields())

# 3. 使用正确的字段名
dynamic = ProjectDynamic(
    project_progress='地基施工中',  # ✅ 正确的字段名
    project_status='normal_construction',  # ✅ 正确的选项值
)
```

---

## ✅ 完成状态

- ✅ 修复视图函数中的字段名
- ✅ 修复 HTML 模板中的字段名
- ✅ 更新项目状态选项
- ✅ 添加日期字段处理
- ✅ 服务器自动重新加载
- ✅ 功能可以正常使用

---

**修复完成时间**: 2026-03-26 00:26  
**服务器状态**: ✅ 运行正常  
**功能状态**: ✅ 可以正常使用
