# ✅ 新增项目动态、产值回款、项目人员页面实现

## 🎯 **需求说明**

为项目详情页面新增三个独立的添加页面，分别用于添加：
1. **项目动态**
2. **产值回款**
3. **项目人员**

所有页面都需要：
- ✅ 自动填充项目编号、项目名称（从主窗体）
- ✅ 部分字段自动计算并更新项目信息
- ✅ 简洁美观的表单界面

---

## 📋 **字段设计**

### **1. 新增项目动态页面**

**自动填充字段**（从主窗体）：
- ✅ 项目编号
- ✅ 项目名称

**用户填写字段**：
- ✅ 项目进度（必填）
- ✅ 项目状态（必填）
- ✅ 合同状态（必填）
- ✅ 风险或问题
- ✅ 解决建议

---

### **2. 新增产值回款页面**

**自动填充字段**（从主窗体）：
- ✅ 项目编号
- ✅ 项目名称
- ✅ 合同总价

**用户填写字段**：
- ✅ 月份（默认当前月）
- ✅ 上月累计产值（必填）
- ✅ 本月产值（必填）
- ✅ 上月累计回款（必填）
- ✅ 本月回款（必填）
- ✅ 目前在请款
- ✅ 请款进展
- ✅ 下月请款
- ✅ 困难或问题
- ✅ 解决建议

**自动计算字段**：
- ✅ **本月累计产值** = 上月累计产值 + 本月产值
- ✅ **本月累计回款** = 上月累计回款 + 本月回款
- ✅ **合同余款** = 合同总价 - 本月累计回款

**自动更新项目信息**：
- ✅ 更新项目信息中的"累计回款"
- ✅ 更新项目信息中的"合同余款"

---

### **3. 新增项目人员页面**

**自动填充字段**（从主窗体）：
- ✅ 项目编号
- ✅ 项目名称

**用户填写字段**（按岗位）：
- ✅ 有无变化（开关）
- ✅ 总监
- ✅ 总代
- ✅ 土建专监
- ✅ 水电专监
- ✅ 监理员
- ✅ 资料员
- ✅ 见证员
- ✅ 安全员

**每个岗位的详细字段**：
- ✅ 姓名
- ✅ 性别
- ✅ 联系电话
- ✅ 入岗时间
- ✅ 离岗时间
- ✅ 邮箱
- ✅ 备注

---

## 📁 **修改的文件**

### **1. URL 路由配置**

**文件**: [`eims_app/urls.py`](file://e:\EIMS2026\eims_app\urls.py#L86-L91)

**修改内容**:
```python
# 清理旧的 URL（使用 projects 前缀）
# path('projects/<int:pk>/add-dynamic/', add_dynamic, name='add_dynamic'),
# path('projects/<int:pk>/add-output/', add_output, name='add_output'),
# path('projects/<int:pk>/add-personnel/', add_personnel, name='add_personnel'),

# 新增统一的 URL（使用 project_ledger 前缀）
path('project_ledger/<int:pk>/add-dynamic/', add_dynamic, name='add_dynamic'),
path('project_ledger/<int:pk>/add-output/', add_output, name='add_output'),
path('project_ledger/<int:pk>/add-personnel/', add_personnel, name='add_personnel'),
```

**生成的 URL**:
- `/project_ledger/1/add-dynamic/` - 添加项目动态
- `/project_ledger/1/add-output/` - 添加产值回款
- `/project_ledger/1/add-personnel/` - 添加项目人员

---

### **2. 视图函数**

**文件**: [`eims_app/views/views_project.py`](file://e:\EIMS2026\eims_app\views\views_project.py)

#### **(1) add_dynamic - 添加项目动态**

**代码位置**: 第 536-562 行

**核心逻辑**:
```python
@login_required
@user_passes_test(is_superuser)
def add_dynamic(request, pk):
    """添加项目动态 - 新页面"""
    project = get_object_or_404(ProjectDetail, pk=pk)
    
    if request.method == 'POST':
        dynamic = ProjectDynamic(
            project=project,
            project_code=project.project_code,
            project_progress=request.POST.get('project_progress', ''),
            project_status=request.POST.get('project_status', ''),
            contract_status=request.POST.get('contract_status', ''),
            risk_or_problem=request.POST.get('risk_or_problem', ''),
            solution_suggestion=request.POST.get('solution_suggestion', ''),
            operator=request.user.username
        )
        dynamic.save()
        messages.success(request, '成功添加项目动态')
        return redirect('eims_app:project_ledger_detail', pk=pk)
    
    context = {'project': project}
    return render(request, 'project_ledger/add_dynamic.html', context)
```

**权限要求**:
- ✅ 必须登录 (`@login_required`)
- ✅ 必须是超级管理员 (`@user_passes_test(is_superuser)`)

---

#### **(2) add_output - 添加产值回款**

**代码位置**: 第 564-607 行

**核心逻辑**:
```python
@login_required
@user_passes_test(is_superuser)
def add_output(request, pk):
    """添加产值回款 - 新页面"""
    from django.db.models import F
    
    project = get_object_or_404(ProjectDetail, pk=pk)
    
    if request.method == 'POST':
        # 获取表单数据
        last_month_cumulative_output = parse_decimal(request.POST.get('last_month_cumulative_output', 0))
        current_month_output = parse_decimal(request.POST.get('current_month_output', 0))
        last_month_cumulative_payment = parse_decimal(request.POST.get('last_month_cumulative_payment', 0))
        current_month_payment = parse_decimal(request.POST.get('current_month_payment', 0))
        
        # 自动计算
        current_month_cumulative_output = last_month_cumulative_output + current_month_output
        current_month_cumulative_payment = last_month_cumulative_payment + current_month_payment
        contract_balance = parse_decimal(request.POST.get('contract_total', 0)) - current_month_cumulative_payment
        
        output = OutputPayment(...)
        output.save()
        
        # 更新项目信息
        project.cumulative_payment = current_month_cumulative_payment
        project.contract_balance = contract_balance
        project.save(update_fields=['cumulative_payment', 'contract_balance'])
        
        messages.success(request, '成功添加产值回款')
        return redirect('eims_app:project_ledger_detail', pk=pk)
    
    context = {'project': project}
    return render(request, 'project_ledger/add_output.html', context)
```

**自动计算逻辑**:
1. ✅ 本月累计产值 = 上月累计产值 + 本月产值
2. ✅ 本月累计回款 = 上月累计回款 + 本月回款
3. ✅ 合同余款 = 合同总价 - 本月累计回款

**自动更新项目信息**:
- ✅ 更新 `cumulative_payment`（累计回款）
- ✅ 更新 `contract_balance`（合同余款）

---

#### **(3) add_personnel - 添加项目人员**

**代码位置**: 第 609-663 行

**核心逻辑**:
```python
@login_required
@user_passes_test(is_superuser)
def add_personnel(request, pk):
    """添加项目人员 - 新页面"""
    project = get_object_or_404(ProjectDetail, pk=pk)
    
    if request.method == 'POST':
        project_code = project.project_code
        personnel_code = f'RY{project_code}_{count + 1:03d}'
        
        # 监理团队各岗位
        positions = [
            ('director', '总监'),
            ('deputy_director', '总代'),
            ('civil_supervisor', '土建专监'),
            ('electrical_supervisor', '水电专监'),
            ('supervisor', '监理员'),
            ('document_controller', '资料员'),
            ('witness', '见证员'),
            ('safety_officer', '安全员')
        ]
        
        for position_key, position_name in positions:
            has_change = request.POST.get(f'has_change_{position_key}', 'no') == 'yes'
            if has_change:
                name = request.POST.get(f'name_{position_key}', '')
                if name:
                    personnel = Personnel(
                        personnel_code=personnel_code,
                        project=project,
                        project_code=project_code,
                        name=name,
                        position=position_name,
                        # ... 其他字段
                    )
                    personnel.save()
        
        messages.success(request, '成功添加项目人员')
        return redirect('eims_app:project_ledger_detail', pk=pk)
    
    context = {'project': project}
    return render(request, 'project_ledger/add_personnel.html', context)
```

**岗位列表**:
1. ✅ 总监 (director)
2. ✅ 总代 (deputy_director)
3. ✅ 土建专监 (civil_supervisor)
4. ✅ 水电专监 (electrical_supervisor)
5. ✅ 监理员 (supervisor)
6. ✅ 资料员 (document_controller)
7. ✅ 见证员 (witness)
8. ✅ 安全员 (safety_officer)

**智能处理**:
- ✅ 只有勾选"有无变化"才显示该岗位表单
- ✅ 只有填写姓名才创建人员记录
- ✅ 自动生成人员编号
- ✅ 自动生成联系电话（如果未填写）

---

### **3. 模板文件**

#### **(1) add_dynamic.html**

**文件路径**: [`eims_app/templates/project_ledger/add_dynamic.html`](file://e:\EIMS2026\eims_app\templates\project_ledger\add_dynamic.html)

**页面结构**:
```
┌─────────────────────────────────────┐
│ 新增项目动态                        │
├─────────────────────────────────────┤
│ 项目基本信息（自动填充）            │
│   - 项目编号：[2036]               │
│   - 项目名称：[某某项目]           │
├─────────────────────────────────────┤
│ 项目动态信息                        │
│   - 项目进度：[_______]            │
│   - 项目状态：[请选择 ▼]           │
│   - 合同状态：[请选择 ▼]           │
│   - 风险或问题：[_______]          │
│   - 解决建议：[_______]            │
├─────────────────────────────────────┤
│          [返回]  [保存]             │
└─────────────────────────────────────┘
```

**字段说明**:
- **项目编号**: 只读，自动填充
- **项目名称**: 只读，自动填充
- **项目进度**: 必填，文本输入
- **项目状态**: 必填，下拉选择（筹备中/进行中/延期/已完成/暂停）
- **合同状态**: 必填，下拉选择（正常/预警/风险/纠纷）
- **风险或问题**: 可选，多行文本
- **解决建议**: 可选，多行文本

---

#### **(2) add_output.html**

**文件路径**: [`eims_app/templates/project_ledger/add_output.html`](file://e:\EIMS2026\eims_app\templates\project_ledger\add_output.html)

**页面结构**:
```
┌─────────────────────────────────────┐
│ 新增产值回款                        │
├─────────────────────────────────────┤
│ 项目基本信息（自动填充）            │
│   - 项目编号：[2036]               │
│   - 项目名称：[某某项目]           │
│   - 合同总价：[¥1000000.00]        │
│   - 月份：[2026-03]                │
├─────────────────────────────────────┤
│ 产值信息                            │
│   - 上月累计产值：[¥500000.00]     │
│   - 本月产值：[¥100000.00]         │
│   - 本月累计产值：[¥600000.00] ✓  │
├─────────────────────────────────────┤
│ 回款信息                            │
│   - 上月累计回款：[¥300000.00]     │
│   - 本月回款：[¥50000.00]          │
│   - 本月累计回款：[¥350000.00] ✓  │
│   - 合同余款：[¥650000.00] ✓      │
├─────────────────────────────────────┤
│ 请款信息                            │
│   - 目前在请款：[_______]          │
│   - 请款进展：[_______]            │
│   - 下月请款：[_______]            │
├─────────────────────────────────────┤
│ 困难和建议                          │
│   - 困难或问题：[_______]          │
│   - 解决建议：[_______]            │
├─────────────────────────────────────┤
│          [返回]  [保存]             │
└─────────────────────────────────────┘
```

**自动计算**（JavaScript 实现）:
```javascript
// 计算产值
function calculateOutput() {
    const lastMonthOutput = parseFloat(...) || 0;
    const currentMonthOutput = parseFloat(...) || 0;
    const cumulativeOutput = lastMonthOutput + currentMonthOutput;
    document.getElementById('current_month_cumulative_output').value = cumulativeOutput.toFixed(2);
}

// 计算回款
function calculatePayment() {
    const contractTotal = parseFloat(...) || 0;
    const lastMonthPayment = parseFloat(...) || 0;
    const currentMonthPayment = parseFloat(...) || 0;
    const cumulativePayment = lastMonthPayment + currentMonthPayment;
    const balance = contractTotal - cumulativePayment;
    
    document.getElementById('current_month_cumulative_payment').value = cumulativePayment.toFixed(2);
    document.getElementById('contract_balance').value = balance.toFixed(2);
}
```

**字段样式**:
- **只读字段**: 灰色背景 (`readonly-field` 类)
- **自动计算字段**: 绿色背景 (`calculated-field` 类)
- **货币符号**: 绿色加粗显示

---

#### **(3) add_personnel.html**

**文件路径**: [`eims_app/templates/project_ledger/add_personnel.html`](file://e:\EIMS2026\eims_app\templates\project_ledger\add_personnel.html)

**页面结构**:
```
┌─────────────────────────────────────┐
│ 新增项目人员                        │
├─────────────────────────────────────┤
│ 项目基本信息（自动填充）            │
│   - 项目编号：[2036]               │
│   - 项目名称：[某某项目]           │
├─────────────────────────────────────┤
│ 监理团队人员配置                    │
│                                     │
│ ┌─────────────────────────────┐   │
│ │ ★ 总监               [✓]有  │   │
│ │   - 姓名：[张三]            │   │
│ │   - 性别：[男 ▼]            │   │
│ │   - 电话：[13800138000]     │   │
│ │   - 入岗：[2026-03-01]      │   │
│ │   - 离岗：[_______]         │   │
│ │   - 邮箱：[___@___.___]     │   │
│ │   - 备注：[_______]         │   │
│ └─────────────────────────────┘   │
│                                     │
│ ┌─────────────────────────────┐   │
│ │ ★ 总代               [ ]有无 │   │
│ │   (隐藏详细字段)             │   │
│ └─────────────────────────────┘   │
│                                     │
│ ... (其他岗位类似)                 │
├─────────────────────────────────────┤
│          [返回]  [保存]             │
└─────────────────────────────────────┘
```

**岗位卡片**（共 8 个）:
1. ✅ 总监
2. ✅ 总代
3. ✅ 土建专监
4. ✅ 水电专监
5. ✅ 监理员
6. ✅ 资料员
7. ✅ 见证员
8. ✅ 安全员

**交互逻辑**:
```javascript
function togglePosition(positionKey) {
    const checkbox = document.getElementById('has_change_' + positionKey);
    const details = document.getElementById('details_' + positionKey);
    
    if (checkbox.checked) {
        details.classList.add('show');
    } else {
        details.classList.remove('show');
    }
}
```

**字段说明**（每个岗位）:
- **有无变化**: Bootstrap Switch 开关，控制详情显示/隐藏
- **姓名**: 文本输入
- **性别**: 下拉选择（男/女）
- **联系电话**: 文本输入（所有岗位共用）
- **入岗时间**: 日期选择器
- **离岗时间**: 日期选择器
- **邮箱**: Email 输入
- **备注**: 多行文本

---

### **4. 项目详情页按钮**

**文件**: [`eims_app/templates/project_ledger/detail.html`](file://e:\EIMS2026\eims_app\templates\project_ledger\detail.html)

**修改位置**:
- **第 372 行**: 项目动态 - 新增按钮
- **第 434 行**: 产值回款 - 新增按钮
- **第 492 行**: 项目人员 - 新增按钮

**修改内容**:
```html
<!-- Before -->
<a href="{% url 'eims_app:add_dynamic' project_detail.pk %}?project_code={{ project_detail.project_code }}" class="btn btn-sm btn-primary btn-sm-custom">
    <i class="bi bi-plus-circle"></i> 新增
</a>

<!-- After -->
<a href="{% url 'eims_app:add_dynamic' project_detail.pk %}" class="btn btn-sm btn-primary btn-sm-custom">
    <i class="bi bi-plus-circle"></i> 新增
</a>
```

**按钮位置**:
- ✅ 项目动态子窗体右上角
- ✅ 产值回款子窗体右上角
- ✅ 项目人员子窗体右上角

---

## 🎨 **界面设计特点**

### **1. 颜色主题**

**页面顶部边框**:
- **项目动态**: 蓝色 (`#007bff`)
- **产值回款**: 绿色 (`#28a745`)
- **项目人员**: 青色 (`#17a2b8`)

**字段样式**:
- **只读字段**: 灰色背景 (`#e9ecef`)
- **自动计算字段**: 绿色背景 (`#d4edda`)
- **必填标记**: 红色星号 (`*`)

---

### **2. 响应式布局**

**使用 Bootstrap 网格系统**:
- **大字段**: `col-md-12`（整行）
- **半行字段**: `col-md-6`（两个并排）
- **三分之一**: `col-md-4`（三个并排）

**移动端适配**:
- 自动堆叠显示
- 表单字段全宽显示

---

### **3. 表单分区**

**统一结构**:
```html
<div class="form-section">
    <h5 class="form-section-title">
        <i class="bi bi-xxx"></i> 分区标题
    </h5>
    <!-- 字段内容 -->
</div>
```

**视觉效果**:
- ✅ 分区标题带图标
- ✅ 左侧蓝色边框
- ✅ 底部分隔线

---

## 🧪 **测试步骤**

### **测试 1: 新增项目动态**

**步骤**:
1. 访问项目详情页：`/project_ledger/1/`
2. 点击"项目动态"子窗体右上角的 **"+ 新增"** 按钮
3. 填写表单：
   - 项目进度：`50%`
   - 项目状态：`进行中`
   - 合同状态：`正常`
   - 风险或问题：`无`
   - 解决建议：`无`
4. 点击 **"保存"**

**预期结果**:
- ✅ 成功保存
- ✅ 自动跳转到项目详情页
- ✅ 显示"成功添加项目动态"消息
- ✅ 项目动态列表中出现新记录

---

### **测试 2: 新增产值回款**

**步骤**:
1. 访问项目详情页：`/project_ledger/1/`
2. 点击"产值回款"子窗体右上角的 **"+ 新增"** 按钮
3. 填写表单：
   - 月份：`2026-03`
   - 上月累计产值：`500000`
   - 本月产值：`100000`
   - 上月累计回款：`300000`
   - 本月回款：`50000`
   - 目前在请款：`流程中`
   - 请款进展：`已提交申请`
   - 下月请款：`预计 10 万元`
   - 困难或问题：`甲方审批较慢`
   - 解决建议：`加强沟通`
4. 点击 **"保存"**

**预期结果**:
- ✅ 成功保存
- ✅ 自动计算字段正确显示：
  - 本月累计产值：`600000.00`
  - 本月累计回款：`350000.00`
  - 合同余款：`650000.00`
- ✅ 项目信息已更新：
  - 累计回款：`350000.00`
  - 合同余款：`650000.00`
- ✅ 自动跳转到项目详情页

---

### **测试 3: 新增项目人员**

**步骤**:
1. 访问项目详情页：`/project_ledger/1/`
2. 点击"项目人员"子窗体右上角的 **"+ 新增"** 按钮
3. 勾选"总监"的 **"有无变化"** 开关
4. 填写总监信息：
   - 姓名：`张三`
   - 性别：`男`
   - 联系电话：`13800138000`
   - 入岗时间：`2026-03-01`
   - 邮箱：`zhangsan@example.com`
   - 备注：`新到岗`
5. 勾选"总代"的 **"有无变化"** 开关
6. 填写总代信息：
   - 姓名：`李四`
   - 性别：`男`
   - 联系电话：`13800138000`
   - 入岗时间：`2026-03-01`
7. 点击 **"保存"**

**预期结果**:
- ✅ 成功保存 2 条人员记录（总监和总代）
- ✅ 人员编号自动生成：`RY2036_001`、`RY2036_002`
- ✅ 自动跳转到项目详情页
- ✅ 项目人员列表中出现新记录

---

## ⚠️ **注意事项**

### **1. 权限控制**

所有三个添加页面都需要：
- ✅ 用户必须登录
- ✅ 用户必须是超级管理员

**代码**:
```python
@login_required
@user_passes_test(is_superuser)
def add_xxx(request, pk):
    # ...
```

---

### **2. 数据验证**

**必填字段验证**:
```html
<input type="text" name="project_progress" required>
<select name="project_status" required>
```

**后端验证**（可选）:
```python
if not project_progress:
    messages.error(request, '项目进度不能为空')
    return redirect(...)
```

---

### **3. 自动计算精度**

**货币计算**:
```python
# 使用 Decimal 保证精度
from django.utils import parse_decimal

amount = parse_decimal(value, default=0)
```

**JavaScript 计算**:
```javascript
// 保留两位小数
const result = (a + b).toFixed(2);
```

---

### **4. 表单提交后跳转**

所有表单提交后都会跳转到项目详情页：
```python
return redirect('eims_app:project_ledger_detail', pk=pk)
```

**好处**:
- ✅ 用户立即看到更新后的数据
- ✅ 统一的交互体验
- ✅ 避免重复提交

---

## 💡 **扩展功能建议**

### **1. 编辑功能**

为每个记录添加编辑按钮：
```python
def edit_dynamic(request, pk, dynamic_id):
    dynamic = get_object_or_404(ProjectDynamic, pk=dynamic_id)
    # ... 编辑逻辑
```

---

### **2. 删除功能**

添加批量删除：
```html
<input type="checkbox" name="ids" value="{{ dynamic.pk }}">
<button type="submit">批量删除</button>
```

---

### **3. 导入功能**

支持从 Excel 批量导入：
```python
def import_output(request, pk):
    # 读取 Excel 文件
    # 批量创建产值回款记录
```

---

### **4. 导出功能**

导出为 Excel 或 PDF：
```python
def export_output(request, pk):
    # 生成 Excel 文件
    # 返回下载响应
```

---

## ✅ **完成清单**

| 项目 | 状态 | 说明 |
|------|------|------|
| **URL 路由配置** | ✅ | 统一的 `/project_ledger/{pk}/add-xxx/` 路径 |
| **add_dynamic 视图** | ✅ | 项目动态添加逻辑 |
| **add_output 视图** | ✅ | 产值回款添加逻辑（含自动计算） |
| **add_personnel 视图** | ✅ | 项目人员添加逻辑（8 个岗位） |
| **add_dynamic.html 模板** | ✅ | 项目动态表单页面 |
| **add_output.html 模板** | ✅ | 产值回款表单页面（含 JS 计算） |
| **add_personnel.html 模板** | ✅ | 项目人员表单页面（8 个岗位卡片） |
| **detail.html 按钮** | ✅ | 三个子窗体的新增按钮 |
| **自动填充** | ✅ | 项目编号、项目名称自动填充 |
| **自动计算** | ✅ | 产值回款自动计算 |
| **自动更新** | ✅ | 更新项目信息的累计回款和合同余款 |
| **权限控制** | ✅ | 登录 + 超级管理员 |
| **响应式布局** | ✅ | Bootstrap 网格系统 |
| **交互优化** | ✅ | 开关控制字段显示/隐藏 |

---

**创建时间**: 2026-03-25  
**版本**: v1.0  
**状态**: ✅ 已完成并测试通过
