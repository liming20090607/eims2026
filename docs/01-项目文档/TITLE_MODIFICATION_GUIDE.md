# 页面标题修改指南

## 📍 两个标题的位置

### 当前显示效果

```
┌─────────────────────────────────────────────┐
│ 创建月度报告              [首页 > 月度报告]   │
│ 填报项目月度动态信息                         │
└─────────────────────────────────────────────┘
  ↑                        ↑
  主标题                    面包屑导航
  副标题
```

---

## 🔧 修改方法

### **方法 1：在视图中修改（推荐）**

**文件位置**：`eims_app/views/views_monthly_report.py`

**代码位置**：第 111-116 行

```python
context = {
    'form': form,
    'title': '创建月度报告',      # ← 改这里：主标题
    'action': '创建',
    'subtitle': '填报项目月度动态信息',  # ← 改这里：副标题
}
```

**修改示例**：

```python
# 改成其他标题
context = {
    'form': form,
    'title': '新增月报',          # 主标题
    'action': '新增',
    'subtitle': '填写项目本月情况',  # 副标题
}
```

---

### **方法 2：在模板中修改**

**文件位置**：`eims_app/templates/monthly_report/form.html`

**代码位置**：第 8 行

```django
{% include 'components/page_title.html' with title=title subtitle=subtitle|default:'填报项目月度动态信息' %}
```

**说明**：
- `title=title`：使用视图传入的 `title` 变量
- `subtitle=subtitle|default:'...'`：优先使用视图传入的 `subtitle`，如果没有则使用默认值

**修改示例**：

```django
{# 直接写死副标题 #}
{% include 'components/page_title.html' with title=title subtitle='自定义副标题' %}

{# 完全去掉副标题 #}
{% include 'components/page_title.html' with title=title %}
```

---

### **方法 3：修改组件模板**

**文件位置**：`eims_app/templates/components/page_title.html`

**作用**：控制标题的显示样式和逻辑

**当前代码**：

```django
<div>
  <h1 class="h3 mb-0">
    {% if icon %}
      <i class="fas {{ icon }} me-2 text-primary"></i>
    {% endif %}
    {{ title }}
  </h1>
  {% if subtitle %}
    <p class="text-muted mb-0 mt-1 small">{{ subtitle }}</p>
  {% endif %}
</div>
```

**修改建议**：

```django
{# 如果想改变副标题样式 #}
{% if subtitle %}
  <p class="text-secondary mb-0 mt-2" style="font-size: 0.9rem;">
    {{ subtitle }}
  </p>
{% endif %}

{# 如果想添加图标 #}
<h1 class="h3 mb-0">
  <i class="bi bi-file-earmark-text me-2 text-primary"></i>
  {{ title }}
</h1>
```

---

## 📊 三种修改方式对比

| 方式 | 位置 | 优点 | 缺点 | 适用场景 |
|------|------|------|------|---------|
| **视图修改** | views.py | ✅ 灵活<br>✅ 可动态变化<br>✅ 符合 MVC 模式 | ❌ 需要改 Python 代码 | 推荐用于不同页面 |
| **模板修改** | templates/ | ✅ 简单直观<br>✅ 无需改 Python | ❌ 每个模板都要改 | 适合单个页面定制 |
| **组件修改** | components/ | ✅ 全局生效<br>✅ 统一样式 | ❌ 影响所有页面 | 适合统一调整样式 |

---

## 🎯 推荐做法

### **最佳实践**：在视图中修改

**原因**：
1. ✅ 符合 Django MTV 架构
2. ✅ 逻辑清晰，易于维护
3. ✅ 可以针对不同情况设置不同标题
4. ✅ 不影响其他页面

**示例代码**：

```python
@login_required
def monthly_report_create(request):
    # ... 省略其他代码 ...
    
    context = {
        'form': form,
        'title': '创建月度报告',
        'action': '创建',
        'subtitle': '填报项目月度动态信息',
    }
    
    return render(request, 'monthly_report/form.html', context)
```

---

## 💡 常见修改场景

### **场景 1：编辑页面标题**

```python
# views/views_monthly_report.py
@login_required
def monthly_report_update(request, pk):
    """编辑月度报告"""
    report = get_object_or_404(MonthlyReport, pk=pk)
    
    if request.method == 'POST':
        form = MonthlyReportForm(request.POST, instance=report, user=request.user)
        # ... 省略处理逻辑 ...
    else:
        form = MonthlyReportForm(instance=report, user=request.user)
    
    context = {
        'form': form,
        'title': '编辑月度报告',              # ← 编辑标题
        'action': '编辑',
        'subtitle': f'{report.project.project_name} - {report.report_year}年{report.report_month}月',  # ← 动态副标题
    }
    
    return render(request, 'monthly_report/form.html', context)
```

---

### **场景 2：查看详情页标题**

```python
# views/views_monthly_report.py
@login_required
def monthly_report_detail(request, pk):
    """月度报告详情"""
    report = get_object_or_404(MonthlyReport, pk=pk)
    
    context = {
        'report': report,
        'title': '月度报告详情',
        'subtitle': f'{report.project.project_name} - {report.report_year}年{report.report_month}月',
    }
    
    return render(request, 'monthly_report/detail.html', context)
```

---

### **场景 3：列表页标题**

```python
# views/views_monthly_report.py
@login_required
def monthly_report_list(request):
    """月度报告列表"""
    
    # ... 省略查询逻辑 ...
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'title': '月度报告',
        'subtitle': '查看所有项目的月度报告',
    }
    
    return render(request, 'monthly_report/list.html', context)
```

---

## 🎨 样式自定义

### **改变主标题大小**

**文件**：`components/page_title.html`

```django
{# 改大标题 #}
<h1 class="h2 mb-0">  <!-- h3 → h2 -->
  {{ title }}
</h1>

{# 或自定义尺寸 #}
<h1 class="mb-0" style="font-size: 1.75rem;">
  {{ title }}
</h1>
```

---

### **改变副标题颜色和样式**

```django
{% if subtitle %}
  {# 蓝色副标题 #}
  <p class="text-primary mb-0 mt-1 small">{{ subtitle }}</p>
  
  {# 灰色背景副标题 #}
  <p class="bg-light text-dark p-2 rounded mb-0 mt-2 small">
    {{ subtitle }}
  </p>
  
  {# 带图标的副标题 #}
  <p class="text-muted mb-0 mt-1 small">
    <i class="bi bi-info-circle me-1"></i>
    {{ subtitle }}
  </p>
{% endif %}
```

---

### **添加面包屑导航**

如果需要在视图中定义面包屑：

```python
# views/views_monthly_report.py
context = {
    'form': form,
    'title': '创建月度报告',
    'subtitle': '填报项目月度动态信息',
    'breadcrumb': [
        {'name': '月度报告', 'url': '/monthly-report/'},
        {'name': '创建', 'url': ''},
    ],
}
```

---

## ✅ 快速修改清单

### **只改主标题**
```python
# views.py
'title': '新的主标题',
```

### **只改副标题**
```python
# views.py
'subtitle': '新的副标题',
```

### **两个都改**
```python
# views.py
'title': '新的主标题',
'subtitle': '新的副标题',
```

### **去掉副标题**
```python
# views.py
# 不传 subtitle 参数即可
```

---

## 🔍 调试技巧

### **查看当前标题值**

在模板中添加调试代码：

```django
<!-- 在 form.html 顶部添加 -->
{% debug %}

<!-- 或简单打印 -->
<p>DEBUG: title={{ title }}, subtitle={{ subtitle }}</p>
```

---

### **检查视图传入的参数**

在视图中打印：

```python
print(f"Context: title={context['title']}, subtitle={context.get('subtitle', 'None')}")
```

---

## 📝 总结

### **三个关键文件**

| 文件 | 作用 | 修改内容 |
|------|------|---------|
| `views_monthly_report.py` | 视图逻辑 | 设置 title 和 subtitle 变量 |
| `form.html` | 页面模板 | 控制如何传递 subtitle |
| `page_title.html` | 标题组件 | 控制标题显示样式 |

### **推荐修改流程**

```
1. 打开 views_monthly_report.py
   ↓
2. 找到对应视图函数
   ↓
3. 修改 context 中的 title 和 subtitle
   ↓
4. 保存并刷新页面
   ↓
5. 完成！
```

### **常用标题建议**

| 页面类型 | 主标题 | 副标题 |
|---------|--------|--------|
| 创建页 | 创建月度报告 | 填报项目月度动态信息 |
| 编辑页 | 编辑月度报告 | 修改 XX 项目 X 月报告 |
| 详情页 | 月度报告详情 | XX 项目 - 2026 年 3 月 |
| 列表页 | 月度报告 | 查看所有项目的月度报告 |

---

现在您可以根据需要修改标题了！有任何问题随时问我。😊
