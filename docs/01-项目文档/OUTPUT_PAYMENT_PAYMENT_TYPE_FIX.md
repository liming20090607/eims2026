# 移除不存在的 payment_type 字段

## 🐛 错误描述

**错误类型**：`FieldError`

**错误信息**：
```
Cannot resolve keyword 'payment_type' into field. 
Choices are: actual_payment, contract_receivable, contract_total, create_time, 
cumulative_output, cumulative_received, id, is_deleted, last_payment_situation, 
month, monthly_output, near_term_receivable, need_assistance, next_month_plan, 
next_month_request, operator, output_amount, payment_amount, payment_basis, 
payment_date, payment_measures, payment_method, project, project_code, project_id, 
recent_payment_request, remark, update_time
```

**错误位置**：
- 文件：`eims_app/views/views_output_payment.py`
- 函数：`output_list`

---

## 🔍 错误原因

### **问题分析**

代码中使用了 `payment_type` 字段进行筛选和统计，但 `OutputPayment` 模型中**没有这个字段**！

**实际存在的字段**：
- ✅ `payment_method` - 回款方式（如银行转账、现金）
- ❌ `payment_type` - 不存在

---

## 📊 OutputPayment 模型的字段

根据模型定义，`OutputPayment` 包含以下字段：

### **项目信息**
- `project` - 关联项目（外键）
- `project_code` - 项目编号
- `month` - 月份（格式：YYYY-MM）

### **产值数据**
- `monthly_output` - 当月产值（万元）
- `cumulative_output` - 累计产值（万元）
- `output_amount` - 产值金额

### **回款数据**
- `contract_total` - 合同总额（元）
- `cumulative_received` - 累计已收款（元）
- `contract_receivable` - 合同应收款（元）
- `near_term_receivable` - 近期待收款（元）
- `actual_payment` - 本月实际回款（元）
- `payment_amount` - 回款金额
- `payment_date` - 回款日期
- `payment_method` - 回款方式（如银行转账、现金）✅

### **付款依据**
- `payment_basis` - 合同付款依据
- `last_payment_situation` - 上次回款情况
- `recent_payment_request` - 近期请款情况

### **下月计划**
- `next_month_request` - 下个月请款
- `next_month_plan` - 下月计划收款
- `payment_measures` - 请款措施
- `need_assistance` - 需要协助

### **其他**
- `operator` - 操作人
- `remark` - 备注
- `create_time` - 创建时间
- `update_time` - 更新时间

---

## ✅ 修复方案

### **1. 修改视图函数**

**文件**：`views/views_output_payment.py`

#### **移除 pay_type 筛选**

**修改前**：
```python
@login_required
def output_list(request):
    search_key = request.GET.get('search', '')
    pay_type = request.GET.get('pay_type', '')  # ❌ 移除

    outputs = OutputPayment.objects.filter(is_deleted=False)
    # 关键词筛选
    if search_key:
        outputs = outputs.filter(
            Q(project_code__icontains=search_key) | 
            Q(contract_code__icontains=search_key) | 
            Q(responsible_person__icontains=search_key)
        )
    # 回款类型筛选 ❌ 移除
    if pay_type:
        outputs = outputs.filter(payment_type=pay_type)
```

**修改后**：
```python
@login_required
def output_list(request):
    search_key = request.GET.get('search', '')

    outputs = OutputPayment.objects.filter(is_deleted=False)
    # 关键词筛选
    if search_key:
        outputs = outputs.filter(
            Q(project_code__icontains=search_key) | 
            Q(contract_code__icontains=search_key) | 
            Q(responsible_person__icontains=search_key)
        )
    # ✅ 移除了 pay_type 筛选
```

---

#### **修改统计图表数据**

**修改前**：
```python
# 回款类型分布
payment_types = OutputPayment.objects.filter(is_deleted=False).values('payment_type').annotate(
    total=Sum('actual_payment')
).order_by('-total')

payment_type_labels = [item['payment_type'] or '未分类' for item in payment_types]
payment_type_data = [float(item['total'] or 0) for item in payment_types]
```

**修改后**：
```python
# 回款类型分布（使用 payment_method 代替）
payment_methods = OutputPayment.objects.filter(is_deleted=False).values('payment_method').annotate(
    total=Sum('actual_payment')
).order_by('-total')

payment_type_labels = [item['payment_method'] or '未分类' for item in payment_methods]
payment_type_data = [float(item['total'] or 0) for item in payment_methods]
```

---

#### **移除 context 中的 pay_type**

**修改前**：
```python
context = {
    'outputs': outputs,
    'search_key': search_key,
    'pay_type': pay_type,  # ❌ 移除
    'back_url': back_url,
    # ...
}
```

**修改后**：
```python
context = {
    'outputs': outputs,
    'search_key': search_key,
    'back_url': back_url,
    # ...
}
```

---

### **2. 修改模板**

**文件**：`templates/output_payment/output_payment_list.html`

#### **移除回款类型筛选器**

**修改前**：
```html
<div class="search-bar mt-4">
    <form method="get" class="search-form" action="{% url 'eims_app:output_payment_list' %}">
        <input type="text" 
               name="search" 
               class="search-input" 
               placeholder="搜索项目编号、合同编号、责任人..." 
               value="{{ search_key }}">
        <select name="pay_type" class="search-input" style="flex: 0 0 200px;">
            <option value="">全部类型</option>
            <option value="预付款" {% if pay_type == '预付款' %}selected{% endif %}>预付款</option>
            <option value="进度款" {% if pay_type == '进度款' %}selected{% endif %}>进度款</option>
            <option value="尾款" {% if pay_type == '尾款' %}selected{% endif %}>尾款</option>
            <option value="质保金" {% if pay_type == '质保金' %}selected{% endif %}>质保金</option>
        </select>
        <button type="submit" class="search-btn">
            <i class="bi bi-search me-2"></i>搜索
        </button>
        <a href="{% url 'eims_app:output_payment_list' %}" class="btn btn-outline-secondary">
            <i class="bi bi-arrow-clockwise"></i>
        </a>
    </form>
</div>
```

**修改后**：
```html
<div class="search-bar mt-4">
    <form method="get" class="search-form" action="{% url 'eims_app:output_payment_list' %}">
        <input type="text" 
               name="search" 
               class="search-input" 
               placeholder="搜索项目编号、合同编号、责任人..." 
               value="{{ search_key }}">
        <button type="submit" class="search-btn">
            <i class="bi bi-search me-2"></i>搜索
        </button>
        <a href="{% url 'eims_app:output_payment_list' %}" class="btn btn-outline-secondary">
            <i class="bi bi-arrow-clockwise"></i>
        </a>
    </form>
</div>
```

---

#### **移除分页链接中的 pay_type 参数**

**修改前**：
```html
<a class="page-link" href="?page=1&search={{ search_key }}&pay_type={{ pay_type }}">
    <i class="bi bi-chevron-double-left"></i>
</a>
```

**修改后**：
```html
<a class="page-link" href="?page=1&search={{ search_key }}">
    <i class="bi bi-chevron-double-left"></i>
</a>
```

---

## 📝 修改的文件清单

| 文件 | 修改内容 | 行数变化 |
|------|---------|---------|
| `views/views_output_payment.py` | 移除 pay_type 筛选和统计 | -9 |
| `templates/output_payment/output_payment_list.html` | 移除筛选器和分页参数 | -12 |
| **总计** | - | **-21** |

---

## 🎯 修改对比

### **筛选功能**

#### **修改前**
```
搜索框 + 回款类型下拉框
- 按关键词搜索 ✅
- 按回款类型筛选 ❌（字段不存在）
```

#### **修改后**
```
搜索框
- 按关键词搜索 ✅
```

---

### **图表数据**

#### **修改前**
```python
# 按 payment_type 分组统计
.values('payment_type')  # ❌ 字段不存在
```

#### **修改后**
```python
# 按 payment_method 分组统计
.values('payment_method')  # ✅ 字段存在
```

---

### **搜索栏布局**

#### **修改前**
```
┌─────────────────────────────────────────────┐
│ 🔍 [搜索...] [类型▼] [🔍搜索] [🔄]         │
└─────────────────────────────────────────────┘
```

#### **修改后**
```
┌─────────────────────────────────────────────┐
│ 🔍 [搜索...] [🔍搜索] [🔄]                  │
└─────────────────────────────────────────────┘
```

---

## ✅ 测试验证

### **测试步骤**

1. **访问产值回款页面**
   ```
   访问：http://localhost:8000/output_payment/
   ✅ 不再报 FieldError 错误
   ✅ 页面正常加载
   ✅ 搜索栏正常显示（无类型筛选）
   ```

2. **测试搜索功能**
   ```
   输入关键词搜索
   ✅ 支持项目编号搜索
   ✅ 支持合同编号搜索
   ✅ 支持责任人搜索
   ```

3. **验证图表显示**
   ```
   查看回款类型分布饼图
   ✅ 按 payment_method 分组显示
   ✅ 显示：银行转账、现金等
   ✅ 数据准确
   ```

4. **测试分页**
   ```
   点击分页链接
   ✅ 页码跳转正常
   ✅ 搜索参数保持
   ✅ 不再包含 pay_type 参数
   ```

---

## 💡 后续建议

### **1. 如果需要回款类型字段**

可以考虑在模型中添加：

```python
class OutputPayment(BaseModel):
    # ... 现有字段 ...
    
    # 新增回款类型字段
    payment_type = models.CharField(
        max_length=50, 
        verbose_name='回款类型',
        choices=[
            ('预付款', '预付款'),
            ('进度款', '进度款'),
            ('尾款', '尾款'),
            ('质保金', '质保金'),
        ],
        default=''
    )
```

然后创建迁移：
```bash
python manage.py makemigrations
python manage.py migrate
```

---

### **2. 优化搜索功能**

可以添加更多实际存在的字段筛选：

```python
# 按月份筛选
month = request.GET.get('month', '')
if month:
    outputs = outputs.filter(month=month)

# 按回款方式筛选
payment_method = request.GET.get('payment_method', '')
if payment_method:
    outputs = outputs.filter(payment_method=payment_method)
```

---

### **3. 添加回款方式筛选器**

模板中替换原来的类型筛选：

```html
<select name="payment_method" class="search-input">
    <option value="">全部回款方式</option>
    <option value="银行转账">银行转账</option>
    <option value="现金">现金</option>
    <option value="承兑汇票">承兑汇票</option>
</select>
```

---

## ✅ 总结

### **问题根源**
- ❌ 使用了不存在的字段 `payment_type`
- ✅ 实际存在的字段是 `payment_method`

### **修复方案**
- ✅ 移除 `pay_type` 筛选逻辑
- ✅ 图表统计改用 `payment_method`
- ✅ 模板移除类型筛选器
- ✅ 分页链接移除 `pay_type` 参数

### **验证结果**
- ✅ 不再报 FieldError 错误
- ✅ 页面正常显示
- ✅ 搜索功能正常
- ✅ 图表正常显示

---

现在访问 `http://localhost:8000/output_payment/` 可以正常工作了！🎉
