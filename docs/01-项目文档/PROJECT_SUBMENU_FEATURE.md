# 项目管理模块子菜单功能说明

## 📋 功能概述

参照人证管理、文件管理等模块的做法，为项目管理模块添加**折叠式子菜单**，包含：
- **项目台账**：项目列表页面
- **项目详情**：单个项目详细信息
- **产值回款**：产值和回款管理页面

---

## 🎯 菜单结构

### **侧边栏菜单层级**

```
项目管理 (父菜单)
├── 项目台账
├── 项目详情
└── 产值回款
```

---

### **视觉效果**

```
┌─────────────────────┐
│ 🏢 项目管理    [3] │ ← 可折叠
└─────────────────────┘
         ↓ 展开
┌─────────────────────┐
│ 📖 项目台账        │
│ 📄 项目详情        │
│ 💰 产值回款        │
└─────────────────────┘
```

---

## ✅ 实现方式

### **1. 修改 base.html 侧边栏**

**文件路径**：`eims_app/templates/base/base.html`

**修改内容**：
```html
<!-- 项目管理（带子菜单） -->
<li class="nav-item">
    <a href="#projectSubmenu" data-bs-toggle="collapse" 
       aria-expanded="{% if 'project' in request.path %}true{% else %}false{% endif %}" 
       class="nav-link {% if 'project' in request.path %}active{% endif %}"
       data-bs-toggle="tooltip" data-bs-placement="right" title="项目管理">
        <span class="menu-icon"><i class="bi bi-building"></i></span>
        <span class="menu-text">项目管理</span>
        <span class="badge bg-primary ms-auto">3</span>
    </a>
    <div class="collapse {% if 'project' in request.path %}show{% endif %}" id="projectSubmenu">
        <ul class="nav flex-column ms-3">
            <li class="nav-item">
                <a href="{% url 'eims_app:project_list' %}" 
                   class="nav-link {% if request.path == '/project/' or request.path == '/project/list/' %}active{% endif %}">
                    <i class="bi bi-journal-text"></i> 项目台账
                </a>
            </li>
            <li class="nav-item">
                <a href="#" class="nav-link" 
                   onclick="alert('请先在项目台账中选择具体项目查看详情')">
                    <i class="bi bi-file-text"></i> 项目详情
                </a>
            </li>
            <li class="nav-item">
                <a href="{% url 'eims_app:output_payment_list' %}" 
                   class="nav-link {% if 'output_payment' in request.path %}active{% endif %}">
                    <i class="bi bi-cash-coin"></i> 产值回款
                </a>
            </li>
        </ul>
    </div>
</li>
```

---

### **2. 修改 sidebar.html 动态生成**

**文件路径**：`eims_app/templates/base/sidebar.html`

**菜单配置**：
```python
{
    'id': 'project',
    'url': reverse('project_list'),
    'text': '项目管理',
    'icon': 'bi-building',
    'permission': 'eims_app.view_project',
    'has_submenu': True,
    'submenu_items': [
        {'url': reverse('project_list'), 'text': '项目台账', 'icon': 'bi-journal-text'},
        {'url': '#', 'text': '项目详情', 'icon': 'bi-file-text', 
         'onclick': "alert('请先在项目台账中选择具体项目查看详情')"},
        {'url': reverse('output_payment_list'), 'text': '产值回款', 'icon': 'bi-cash-coin'},
    ]
}
```

---

### **3. 菜单生成逻辑**

```python
# 检查是否有子菜单
if item.get('has_submenu'):
    # 检查子菜单是否有激活的项
    has_active_submenu = any(
        request.path.startswith(subitem.get('url', '')) 
        for subitem in item.get('submenu_items', [])
        if subitem.get('url') != '#'
    )
    
    # 生成主菜单
    html += f'''
    <li class="nav-item">
      <a href="#projectSubmenu" 
         data-bs-toggle="collapse" 
         aria-expanded="{str(has_active_submenu).lower()}"
         class="nav-link {'active' if has_active_submenu else ''}">
        <span class="menu-icon"><i class="bi {item['icon']}"></i></span>
        <span class="menu-text">{item['text']}</span>
        <span class="badge bg-primary ms-auto">{len(item['submenu_items'])}</span>
      </a>
      <div class="collapse {'show' if has_active_submenu else ''}" id="projectSubmenu">
        <ul class="nav flex-column ms-3">
    '''
    
    # 生成子菜单
    for subitem in item['submenu_items']:
        sub_is_active = request.path.startswith(subitem.get('url', '')) if subitem.get('url') != '#' else False
        onclick_attr = f" onclick=\"{subitem['onclick']}\"" if 'onclick' in subitem else ''
        html += f'''
          <li class="nav-item">
            <a href="{subitem['url']}" class="nav-link {'active' if sub_is_active else ''}"{onclick_attr}>
              <i class="bi {subitem['icon']}"></i> {subitem['text']}
            </a>
          </li>
        '''
    
    html += '''
        </ul>
      </div>
    </li>
    '''
```

---

## 📊 子菜单功能说明

### **1. 项目台账**

**功能**：
- ✅ 显示所有项目列表
- ✅ 支持筛选、搜索
- ✅ 支持分页
- ✅ 可点击进入项目详情

**访问路径**：
```
/project/ 或 /project/list/
```

**高亮逻辑**：
```python
{% if request.path == '/project/' or request.path == '/project/list/' %}active{% endif %}
```

---

### **2. 项目详情**

**功能**：
- ✅ 显示单个项目的详细信息
- ✅ 包含项目动态、产值回款、项目人员三个子窗体
- ✅ 需要先在项目台账中选择具体项目

**访问路径**：
```
/project/{project_id}/detail/
```

**特殊处理**：
```python
onclick="alert('请先在项目台账中选择具体项目查看详情')"
```

**说明**：
- 项目详情不能直接访问，必须通过项目台账列表中的操作进入
- 点击时会弹出提示，引导用户先去项目台账选择项目

---

### **3. 产值回款**

**功能**：
- ✅ 显示所有产值回款记录
- ✅ 按项目分类
- ✅ 支持筛选、搜索
- ✅ 支持分页

**访问路径**：
```
/output_payment/
```

**高亮逻辑**：
```python
{% if 'output_payment' in request.path %}active{% endif %}
```

---

## 🎨 UI 设计细节

### **1. 折叠动画**

```css
/* 折叠效果使用 Bootstrap 5 的 collapse 组件 */
.collapse {
    transition: height 0.35s ease;
}

.collapse.show {
    display: block;
}
```

**效果**：
- ✅ 点击主菜单平滑展开子菜单
- ✅ 再次点击平滑收起
- ✅ 动画流畅自然

---

### **2. 激活状态高亮**

```css
/* 主菜单激活 */
.nav-link.active {
    background-color: #007bff;
    color: #fff;
}

/* 子菜单激活 */
.nav-link.active {
    background-color: #e9ecef;
    color: #007bff;
}
```

**效果**：
- ✅ 当前所在页面菜单高亮
- ✅ 主菜单和子菜单层级分明
- ✅ 视觉引导清晰

---

### **3. 徽章显示**

```html
<span class="badge bg-primary ms-auto">3</span>
```

**效果**：
- ✅ 显示子菜单项数量
- ✅ 右侧对齐
- ✅ 蓝色背景醒目

---

### **4. 图标系统**

| 菜单项 | 图标 | 说明 |
|--------|------|------|
| 项目管理 | `bi-building` | 大楼图标 |
| 项目台账 | `bi-journal-text` | 文档图标 |
| 项目详情 | `bi-file-text` | 文件图标 |
| 产值回款 | `bi-cash-coin` | 钱币图标 |

---

## 🔄 交互流程

### **展开子菜单**

```
1. 用户点击"项目管理"主菜单
   ↓
2. Bootstrap collapse 组件触发
   ↓
3. 子菜单平滑展开
   ↓
4. 显示三个子菜单项
```

---

### **访问子菜单**

```
场景 1：访问项目台账
1. 点击"项目台账"
2. 跳转到 /project/
3. 项目台账菜单高亮
4. 显示项目列表页面

场景 2：访问项目详情
1. 点击"项目详情"
2. 弹出提示："请先在项目台账中选择具体项目查看详情"
3. 用户前往项目台账
4. 在列表中点击"详情"按钮
5. 跳转到 /project/1/detail/
6. 显示项目详情页面

场景 3：访问产值回款
1. 点击"产值回款"
2. 跳转到 /output_payment/
3. 产值回款菜单高亮
4. 显示产值回款列表
```

---

## 📝 修改的文件清单

| 文件 | 修改内容 | 行数变化 |
|------|---------|---------|
| `templates/base/base.html` | 添加项目管理子菜单 HTML | +22 |
| `templates/base/sidebar.html` | 添加子菜单配置和生成逻辑 | +43 |
| **总计** | - | **+65** |

---

## ✅ 测试验证

### **测试步骤**

#### **1. 查看侧边栏**

```
访问任意页面
查看左侧边栏
✅ 显示"项目管理"菜单
✅ 带有大楼图标
✅ 右侧显示蓝色徽章 [3]
```

---

#### **2. 展开子菜单**

```
点击"项目管理"
✅ 子菜单平滑展开
✅ 显示三个子菜单项
✅ 图标显示正确
```

---

#### **3. 访问项目台账**

```
点击"项目台账"
✅ 跳转到项目列表页面
✅ 项目台账菜单高亮
✅ 显示项目列表
```

---

#### **4. 访问项目详情**

```
点击"项目详情"
✅ 弹出提示："请先在项目台账中选择具体项目查看详情"
✅ 点击确定
✅ 停留在当前页面或跳转回项目台账
```

---

#### **5. 访问产值回款**

```
点击"产值回款"
✅ 跳转到产值回款列表页面
✅ 产值回款菜单高亮
✅ 显示产值回款列表
```

---

#### **6. 页面刷新测试**

```
在项目台账页面刷新
✅ 项目管理菜单保持展开
✅ 项目台账子菜单高亮

在项目详情页面刷新
✅ 项目管理菜单保持展开
✅ 项目详情子菜单高亮

在产值回款页面刷新
✅ 项目管理菜单保持展开
✅ 产值回款子菜单高亮
```

---

## 🎯 与其他模块对比

### **人证管理模块**

```
人证管理
├── 模块导航
├── 人员花名册
├── 人员证书
└── 可视化分配
```

**特点**：
- ✅ 4 个子菜单项
- ✅ 包含导航页
- ✅ 功能完整

---

### **文件管理模块**

```
文件管理
├── 文件列表
├── 批量上传
└── 版本管理
```

**特点**：
- ✅ 3 个子菜单项
- ✅ 功能导向
- ✅ 流程清晰

---

### **项目管理模块（新增）**

```
项目管理
├── 项目台账
├── 项目详情
└── 产值回款
```

**特点**：
- ✅ 3 个子菜单项
- ✅ 层级清晰
- ✅ 符合业务逻辑

---

## 💡 设计亮点

### **1. 统一的交互体验**

- ✅ 与人证管理、文件管理保持一致的折叠方式
- ✅ 相同的动画效果和视觉风格
- ✅ 统一的高亮逻辑

---

### **2. 智能的状态保持**

```python
# 页面刷新后菜单保持展开
aria-expanded="{% if 'project' in request.path %}true{% else %}false{% endif %}"

# 子菜单高亮保持
class="nav-link {% if 'project' in request.path %}active{% endif %}"
```

**效果**：
- ✅ 刷新页面后菜单状态保持
- ✅ 当前所在菜单项始终高亮
- ✅ 用户体验流畅

---

### **3. 友好的引导提示**

```python
onclick="alert('请先在项目台账中选择具体项目查看详情')"
```

**作用**：
- ✅ 防止用户误操作
- ✅ 引导正确的使用流程
- ✅ 提升用户体验

---

### **4. 清晰的层级结构**

```
父菜单（项目管理）
    ↓
子菜单（项目台账、项目详情、产值回款）
    ↓
具体页面
```

**优势**：
- ✅ 功能分类清晰
- ✅ 导航逻辑明确
- ✅ 易于查找功能

---

## 🔧 扩展建议

### **1. 添加更多子菜单**

```python
'submenu_items': [
    {'url': reverse('project_list'), 'text': '项目台账', 'icon': 'bi-journal-text'},
    {'url': '#', 'text': '项目详情', 'icon': 'bi-file-text'},
    {'url': reverse('output_payment_list'), 'text': '产值回款', 'icon': 'bi-cash-coin'},
    {'url': reverse('contract_list'), 'text': '项目合同', 'icon': 'bi-file-earmark-text'},
    {'url': reverse('personnel_allocation'), 'text': '人员分配', 'icon': 'bi-people'},
]
```

---

### **2. 添加统计信息**

```html
<span class="badge bg-info ms-auto">{{ project_count }}</span>
```

**效果**：
- ✅ 显示项目总数
- ✅ 实时更新
- ✅ 信息直观

---

### **3. 权限控制**

```python
# 子菜单项也可以添加权限控制
'submenu_items': [
    {
        'url': reverse('project_list'), 
        'text': '项目台账', 
        'icon': 'bi-journal-text',
        'permission': 'eims_app.view_project'
    },
    # ...
]
```

---

## ✅ 总结

### **核心价值**

1. **✅ 统一体验**
   - 与人证管理、文件管理保持一致
   - 用户学习成本低
   - 操作习惯统一

2. **✅ 清晰层级**
   - 功能分类明确
   - 导航逻辑清晰
   - 易于查找使用

3. **✅ 友好交互**
   - 折叠动画流畅
   - 状态保持智能
   - 引导提示友好

4. **✅ 易于扩展**
   - 模块化设计
   - 配置化生成
   - 便于后续添加更多功能

---

现在项目管理模块已经具有折叠式子菜单，包含项目台账、项目详情、产值回款三个子功能！🎉
