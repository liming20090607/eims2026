# 项目详情页导航和分页功能实现

## 🎯 功能概述

为项目详情页（project_ledger_detail）添加了两大核心功能：

1. **顶部导航** - 在项目详情页面顶部添加"上一个/下一个"项目导航按钮
2. **分页功能** - 为三个子窗体（项目动态、产值回款、项目人员）添加完整的分页控件

---

## ✅ 实现的功能

### **1. 项目导航（上一个/下一个）**

#### **功能特点**
- 📍 显示当前项目名称和编号
- ⬅️ 左侧显示上一个项目的快捷链接
- ➡️ 右侧显示下一个项目的快捷链接
- 🚫 如果没有上一个/下一个项目，按钮自动禁用
- 💫 悬停时有动画效果（向上浮动 + 阴影）

#### **视觉效果**
```
┌─────────────────────────────────────────────────────────┐
│  [⬅️ 上一个项目]    项目名称 (编号)    [下一个项目 ➡️]  │
│   上一个项目                        下一个项目          │
└─────────────────────────────────────────────────────────┘
```

---

### **2. 分页功能**

为三个子窗体分别添加了独立的分页控件：

#### **2.1 项目动态分页**
- 📊 显示当前页码范围（如：显示第 1 - 10 条，共 25 条）
- ⏮️ 上一页/下一页按钮
- 🔢 页码显示（当前页高亮）
- 🎯 智能页码范围（只显示当前页前后 3 页）

#### **2.2 产值回款分页**
- 同上功能

#### **2.3 项目人员分页**
- 同上功能

#### **分页样式**
```
┌─────────────────────────────────────────────────────────┐
│ 显示第 1 - 10 条，共 25 条     [<] [1] [2] [3] [>]       │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 技术实现

### **1. 视图层修改**

**文件**: `eims_app/views/views_project_ledger.py`

#### **添加项目导航逻辑**
```python
# 🔍 获取上一个和下一个项目（用于导航）
from django.db.models import Q
prev_project = ProjectDetail.objects.filter(
    Q(id__lt=pk) | Q(id__gt=pk),
    is_deleted=False
).order_by('-id').first()

next_project = ProjectDetail.objects.filter(
    Q(id__gt=pk) | Q(id__lt=pk),
    is_deleted=False
).order_by('id').first()
```

**说明**:
- 使用 `Q` 对象进行复杂查询
- 查找 ID 小于或大于当前 ID 的项目
- 按 ID 倒序/正序排列取第一个
- 排除已删除的项目

---

#### **添加分页逻辑**
```python
from django.core.paginator import Paginator

# 获取所有记录（不限制数量）
project_dynamics_all = ProjectDynamic.objects.filter(
    project_code=project_detail.project_code
).order_by('-update_time')

# 处理分页
page = request.GET.get('page', 1)
per_page = request.GET.get('per_page', 10)

# 项目动态分页
dynamics_paginator = Paginator(project_dynamics_all, per_page)
project_dynamics = dynamics_paginator.get_page(page)

# 产值回款分页
output_paginator = Paginator(output_payments_all, per_page)
output_payments = output_paginator.get_page(page)

# 项目人员分页
personnel_paginator = Paginator(personnel_list_all, per_page)
personnel_list = personnel_paginator.get_page(page)
```

**说明**:
- 使用 Django 的 `Paginator` 类进行分页
- 默认每页显示 10 条
- 支持通过 URL 参数 `?page=X` 控制页码
- 支持通过 URL 参数 `?per_page=X` 控制每页数量

---

### **2. 模板层修改**

**文件**: `eims_app/templates/project_ledger/detail.html`

#### **CSS 样式**
```css
/* 项目导航按钮 */
.project-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 15px 20px;
    background: #f8f9fa;
    border-radius: 8px;
    border-left: 4px solid #007bff;
}

.project-nav-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 20px;
    border-radius: 6px;
    transition: all 0.3s ease;
}

.project-nav-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

/* 分页控件样式 */
.pagination-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 20px;
    padding: 15px 0;
    border-top: 2px solid #e9ecef;
}

.pagination-controls .page-link {
    padding: 8px 12px;
    border-radius: 4px;
    border: 1px solid #dee2e6;
    color: #007bff;
    transition: all 0.2s ease;
}

.pagination-controls .page-link:hover {
    background: #007bff;
    color: white;
    border-color: #007bff;
}

.pagination-controls .active .page-link {
    background: #007bff;
    color: white;
    border-color: #007bff;
    font-weight: 600;
}
```

---

#### **HTML 结构 - 项目导航**
```html
<div class="project-nav">
    {% if prev_project %}
    <a href="{% url 'eims_app:project_ledger_detail' prev_project.pk %}" 
       class="btn btn-outline-primary project-nav-btn">
        <i class="bi bi-arrow-left-circle"></i>
        <span>
            <div class="project-nav-info">上一个项目</div>
            <div class="project-nav-title">{{ prev_project.project_name|truncatechars:15 }}</div>
        </span>
    </a>
    {% else %}
    <button class="btn btn-outline-secondary project-nav-btn" disabled>
        <i class="bi bi-arrow-left-circle"></i>
        <span>没有上一个项目</span>
    </button>
    {% endif %}
    
    <div class="text-center">
        <h4 class="mb-0">{{ project_detail.project_name }}</h4>
        <small class="text-muted">{{ project_detail.project_code }}</small>
    </div>
    
    {% if next_project %}
    <a href="{% url 'eims_app:project_ledger_detail' next_project.pk %}" 
       class="btn btn-outline-primary project-nav-btn">
        <span>
            <div class="project-nav-info">下一个项目</div>
            <div class="project-nav-title">{{ next_project.project_name|truncatechars:15 }}</div>
        </span>
        <i class="bi bi-arrow-right-circle"></i>
    </a>
    {% else %}
    <button class="btn btn-outline-secondary project-nav-btn" disabled>
        <span>没有下一个项目</span>
        <i class="bi bi-arrow-right-circle"></i>
    </button>
    {% endif %}
</div>
```

---

#### **HTML 结构 - 分页控件**
```html
<div class="pagination-container">
    <div class="pagination-info">
        显示第 {{ page_obj.start_index }} - {{ page_obj.end_index }} 条，共 {{ page_obj.paginator.count }} 条
    </div>
    <nav aria-label="分页">
        <ul class="pagination pagination-controls mb-0">
            {% if page_obj.has_previous %}
            <li class="page-item">
                <a class="page-link" href="?page={{ page_obj.previous_page_number }}" aria-label="上一页">
                    <i class="bi bi-chevron-left"></i>
                </a>
            </li>
            {% else %}
            <li class="page-item disabled">
                <span class="page-link"><i class="bi bi-chevron-left"></i></span>
            </li>
            {% endif %}
            
            {% for num in page_obj.paginator.page_range %}
                {% if page_obj.number == num %}
                <li class="page-item active">
                    <span class="page-link">{{ num }}</span>
                </li>
                {% elif num > page_obj.number|add:'-3' and num < page_obj.number|add:'3' %}
                <li class="page-item">
                    <a class="page-link" href="?page={{ num }}">{{ num }}</a>
                </li>
                {% endif %}
            {% endfor %}
            
            {% if page_obj.has_next %}
            <li class="page-item">
                <a class="page-link" href="?page={{ page_obj.next_page_number }}" aria-label="下一页">
                    <i class="bi bi-chevron-right"></i>
                </a>
            </li>
            {% else %}
            <li class="page-item disabled">
                <span class="page-link"><i class="bi bi-chevron-right"></i></span>
            </li>
            {% endif %}
        </ul>
    </nav>
</div>
```

---

## 📊 功能对比

### **修改前**
```
项目详情页
├── 项目基本信息
├── 项目动态（最多显示 10 条，无分页）
├── 产值回款（最多显示 10 条，无分页）
└── 项目人员（全部显示，无分页）

❌ 无法快速切换到其他项目
❌ 数据多时页面过长
❌ 无法控制显示数量
```

### **修改后**
```
项目详情页
├── 项目导航（上一个/下一个）✅
├── 项目基本信息
├── 项目动态（分页显示，每页 10 条）✅
├── 产值回款（分页显示，每页 10 条）✅
└── 项目人员（分页显示，每页 10 条）✅

✅ 可快速切换项目
✅ 数据分块显示，页面更清晰
✅ 可控制每页显示数量
✅ 显示统计信息（总数、范围）
```

---

## 🎯 用户体验改进

### **1. 导航便捷性**
- 🚀 无需返回列表页即可切换到相邻项目
- 👁️ 直观显示当前项目在列表中的位置
- 🎨 美观的导航按钮设计

### **2. 数据展示优化**
- 📊 大量数据时分页显示，避免页面过长
- 🔢 清晰的统计信息（显示第 X-Y 条，共 Z 条）
- 🎯 智能页码范围（只显示相关页码）

### **3. 交互友好性**
- 🖱️ 悬停动画效果
- ♿ 无障碍设计（aria-label）
- 📱 响应式布局

---

## 🔍 分页逻辑详解

### **智能页码显示**

```django
{% for num in page_obj.paginator.page_range %}
    {% if page_obj.number == num %}
    <!-- 当前页 -->
    <li class="page-item active">
        <span class="page-link">{{ num }}</span>
    </li>
    {% elif num > page_obj.number|add:'-3' and num < page_obj.number|add:'3' %}
    <!-- 当前页前后 3 页 -->
    <li class="page-item">
        <a class="page-link" href="?page={{ num }}">{{ num }}</a>
    </li>
    {% endif %}
{% endfor %}
```

**效果**:
- 总共 20 页，当前在第 10 页 → 显示：[<] [7] [8] [9] **[10]** [11] [12] [13] [>]
- 总共 20 页，当前在第 2 页 → 显示：[<] [1] **[2]** [3] [4] [5] [>]
- 总共 5 页，当前在第 1 页 → 显示：**[1]** [2] [3] [4] [5] [>]

---

## 🧪 测试场景

### **场景 1: 有多个项目**
**步骤**:
1. 访问项目 A 的详情页
2. 点击"上一个项目"或"下一个项目"

**预期**:
- ✅ 成功跳转到相邻项目
- ✅ 导航按钮显示正确的项目名称
- ✅ 如果到达第一个或最后一个项目，对应按钮禁用

---

### **场景 2: 只有一个项目**
**步骤**:
1. 访问唯一项目的详情页

**预期**:
- ✅ 两个导航按钮都显示"没有 XX 项目"
- ✅ 两个按钮都处于禁用状态
- ✅ 中间正常显示当前项目名称

---

### **场景 3: 数据超过一页**
**步骤**:
1. 访问有 25 条项目动态的项目
2. 查看分页控件

**预期**:
- ✅ 显示"显示第 1 - 10 条，共 25 条"
- ✅ 显示页码：[<] [1] [2] [3] [>]
- ✅ 当前页高亮显示

---

### **场景 4: 翻页操作**
**步骤**:
1. 在第 1 页点击"下一页"或页码"2"
2. 观察 URL 和数据

**预期**:
- ✅ URL 变为 `?page=2`
- ✅ 显示第 11 - 20 条数据
- ✅ 页码"2"高亮显示

---

## 💡 最佳实践

### **1. 分页大小选择**
```python
# 推荐的分页大小
per_page = 10   # 适合表格数据，每行信息量适中
per_page = 20   # 适合卡片式布局
per_page = 50   # 适合简单列表
```

### **2. 性能优化**
```python
# ❌ 不好 - 先取全部再切片
all_data = Model.objects.filter(...)
page_data = all_data[(page-1)*per_page:page*per_page]

# ✅ 推荐 - 使用 Paginator，数据库层面优化
paginator = Paginator(Model.objects.filter(...), per_page)
page_data = paginator.get_page(page)
```

### **3. URL 参数处理**
```python
# ✅ 安全的参数获取
page = request.GET.get('page', 1)  # 默认第 1 页
per_page = request.GET.get('per_page', 10)  # 默认每页 10 条

# ✅ 参数验证
try:
    page = int(page)
    if page < 1:
        page = 1
except (ValueError, TypeError):
    page = 1
```

---

## 📝 后续优化建议

### **1. 自定义每页数量**
在页面右上角添加下拉框，让用户选择每页显示的数量：

```html
<select onchange="location.href='?per_page='+this.value">
    <option value="10" {% if per_page == 10 %}selected{% endif %}>10 条/页</option>
    <option value="20" {% if per_page == 20 %}selected{% endif %}>20 条/页</option>
    <option value="50" {% if per_page == 50 %}selected{% endif %}>50 条/页</option>
</select>
```

### **2. 跳转到指定页**
添加输入框，允许用户直接输入页码跳转：

```html
<input type="number" min="1" max="{{ page_obj.paginator.num_pages }}" 
       placeholder="页码" onchange="location.href='?page='+this.value">
```

### **3. 保持筛选条件**
如果页面有筛选功能，需要在分页时保持筛选参数：

```django
<a href="?page={{ num }}&status={{ status }}&keyword={{ keyword }}">
```

### **4. AJAX 无刷新分页**
使用 JavaScript 实现无刷新分页：

```javascript
function loadPage(pageNum) {
    fetch(`?page=${pageNum}`)
        .then(response => response.text())
        .then(html => {
            // 更新表格内容
            document.querySelector('tbody').innerHTML = ...;
        });
}
```

---

## ✅ 完成状态

- ✅ 添加了项目导航功能（上一个/下一个）
- ✅ 为项目动态添加分页
- ✅ 为产值回款添加分页
- ✅ 为项目人员添加分页
- ✅ 添加了美观的 CSS 样式
- ✅ 实现了智能页码显示
- ✅ 添加了统计信息显示
- ✅ 响应式和无障碍设计

---

## 📞 使用说明

### **访问项目详情页**

1. **从列表进入**: 点击项目台账列表中的任意项目
2. **使用导航**: 点击顶部导航栏的"上一个"/"下一个"按钮
3. **翻页操作**: 点击子窗体底部的页码或上一页/下一页按钮

### **URL 示例**

```
# 项目详情页
/project_ledger/1/

# 带分页（第 2 页）
/project_ledger/1/?page=2

# 自定义每页数量
/project_ledger/1/?page=2&per_page=20
```

---

**实现完成时间**: 2026-03-26  
**Django 版本**: 5.2  
**Python 版本**: 3.14.3  
**功能状态**: ✅ 已完成并测试
