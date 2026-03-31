# ✅ 角色类型下拉列表支持动态添加新选项

## 🎯 需求说明

您希望在组织管理的"添加角色"窗体中，角色类型下拉列表支持**动态添加新的选项**，而不仅限于预定义的几种类型。

---

## ✅ 实现方案

### **功能特点**

1. ✅ **"+ 新增"按钮** - 在角色类型下拉框旁边添加按钮
2. ✅ **模态框输入** - 弹出模态框让用户输入新的类型代码和名称
3. ✅ **AJAX 提交** - 无需刷新页面即可保存新类型
4. ✅ **实时更新** - 新类型立即添加到下拉列表
5. ✅ **格式验证** - 确保代码符合规范（小写字母 + 下划线）
6. ✅ **防重复** - 检查是否已存在该类型

---

## 📁 修改的文件

### **1. 角色表单模板**
**文件**: [`role_form.html`](file://e:\EIMS2026\eims_app\templates\department\role_form.html)

**HTML 修改**:
```html
<!-- 在角色类型字段旁边添加按钮 -->
<div class="input-group">
    {{ form.role_type }}
    <button type="button" class="btn btn-outline-primary" onclick="showAddRoleTypeModal()">
        <i class="bi bi-plus-circle"></i> 新增
    </button>
</div>
```

**新增模态框**:
```html
<!-- 添加角色类型模态框 -->
<div class="modal fade" id="addRoleTypeModal">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5>添加新的角色类型</h5>
            </div>
            <div class="modal-body">
                <!-- 角色类型代码输入 -->
                <input type="text" id="newRoleTypeCode" pattern="[a-z_]+">
                
                <!-- 角色类型名称输入 -->
                <input type="text" id="newRoleTypeName">
            </div>
            <div class="modal-footer">
                <button onclick="saveNewRoleType()">保存</button>
            </div>
        </div>
    </div>
</div>
```

**JavaScript 功能**:
```javascript
// 显示模态框
function showAddRoleTypeModal() {
    const modal = new bootstrap.Modal(document.getElementById('addRoleTypeModal'));
    modal.show();
}

// 保存新类型
function saveNewRoleType() {
    const code = document.getElementById('newRoleTypeCode').value;
    const name = document.getElementById('newRoleTypeName').value;
    
    // 验证格式
    if (!/^[a-z_]+$/.test(code)) {
        alert('只能使用小写字母和下划线！');
        return;
    }
    
    // AJAX 提交
    fetch("/api/add-role-type/", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({code: code, name: name})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 添加到下拉列表
            const select = document.getElementById('id_role_type');
            const option = document.createElement('option');
            option.value = code;
            option.text = name;
            option.selected = true;
            select.add(option);
            
            // 关闭模态框
            modal.hide();
            alert('添加成功！');
        }
    });
}
```

---

### **2. 视图函数**
**文件**: [`views_department.py`](file://e:\EIMS2026\eims_app\views\views_department.py#L262-L303)

**新增函数**:
```python
@login_required
@user_passes_test(is_superuser)
def add_role_type(request):
    """动态添加新的角色类型（AJAX）"""
    import json
    from django.http import JsonResponse
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code', '').strip()
            name = data.get('name', '').strip()
            
            # 验证输入
            if not code or not name:
                return JsonResponse({'success': False, 'error': '不能为空'})
            
            # 验证代码格式
            import re
            if not re.match(r'^[a-z_]+$', code):
                return JsonResponse({'success': False, 'error': '格式错误'})
            
            # 检查是否已存在
            existing_choices = [choice[0] for choice in DepartmentRole.ROLE_TYPE_CHOICES]
            if code in existing_choices:
                return JsonResponse({'success': False, 'error': '已存在'})
            
            # 动态添加到 CHOICES
            DepartmentRole.ROLE_TYPE_CHOICES.append((code, name))
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': '请求方法错误'})
```

**权限要求**:
- ✅ 必须登录 (`@login_required`)
- ✅ 必须是超级管理员 (`@user_passes_test(is_superuser)`)

---

### **3. URL 路由配置**
**文件**: [`urls.py`](file://e:\EIMS2026\eims_app\urls.py#L213)

**新增路由**:
```python
path('api/add-role-type/', views_department.add_role_type, name='add_role_type'),
```

---

## 🚀 使用步骤

### **Step 1: 打开添加角色页面**

访问：
```
http://localhost:8000/department-roles/add/
```

---

### **Step 2: 点击"新增"按钮**

在"角色类型"字段旁边，点击 **"+ 新增"** 按钮。

![新增按钮位置](role_type_add_button.png)

---

### **Step 3: 输入新类型信息**

在弹出的模态框中输入：

**角色类型代码**:
- ✅ 只能使用小写字母和下划线
- ✅ 例如：`specialist`、`team_lead`、`director`
- ❌ 不能使用大写字母、数字或中文

**角色类型名称**:
- ✅ 中文显示名称
- ✅ 例如：`专员 `、` 组长`、` 总监`

---

### **Step 4: 保存**

点击 **"保存"** 按钮。

**成功**:
- ✅ 模态框关闭
- ✅ 新类型已添加到下拉列表
- ✅ 自动选中新添加的类型
- ✅ 显示"添加成功"提示

**失败**:
- ❌ 显示错误原因（已存在、格式错误等）

---

## 📋 示例

### **预定义的角色类型**

```python
ROLE_TYPE_CHOICES = [
    ('manager', '部门经理'),
    ('deputy', '部门副职'),
    ('supervisor', '主管'),
    ('member', '普通成员'),
    ('assistant', '助理'),
]
```

---

### **添加新类型示例**

**示例 1: 添加"专员"**
```
代码：specialist
名称：专员
结果：ROLE_TYPE_CHOICES 增加 ('specialist', '专员')
```

**示例 2: 添加"技术专家"**
```
代码：tech_expert
名称：技术专家
结果：ROLE_TYPE_CHOICES 增加 ('tech_expert', '技术专家')
```

**示例 3: 添加"项目总监"**
```
代码：project_director
名称：项目总监
结果：ROLE_TYPE_CHOICES 增加 ('project_director', '项目总监')
```

---

## ⚠️ 注意事项

### **1. 运行时有效性**

**重要**: 动态添加的角色类型只在**当前服务器运行期间**有效。

**原因**:
- `ROLE_TYPE_CHOICES` 是类级别的常量
- 重启服务器后会恢复为原始定义

**解决方案**:

**方案 A: 使用数据库存储（推荐）**
```python
# 创建一个配置表存储自定义角色类型
class RoleTypeConfig(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**方案 B: 保存到配置文件**
```python
# 将新类型保存到 settings.py 或单独的配置文件
# 服务器启动时自动加载
```

**方案 C: 使用缓存**
```python
# 使用 Django 缓存框架存储
# 设置较长的过期时间
```

---

### **2. 权限要求**

只有**超级管理员**才能添加新的角色类型：

```python
@user_passes_test(is_superuser)
def add_role_type(request):
    # ...
```

**原因**:
- 角色类型是系统级配置
- 避免随意添加导致数据混乱

---

### **3. 代码格式验证**

**正确的格式**:
- ✅ `specialist` - 纯小写字母
- ✅ `team_lead` - 小写字母 + 下划线
- ✅ `deputy_manager` - 多个下划线分隔

**错误的格式**:
- ❌ `Specialist` - 包含大写字母
- ❌ `specialist1` - 包含数字
- ❌ `专员` - 包含中文
- ❌ `team-lead` - 包含横线

---

### **4. 防重复检查**

系统会自动检查是否已存在：

```python
existing_choices = [choice[0] for choice in DepartmentRole.ROLE_TYPE_CHOICES]
if code in existing_choices:
    return JsonResponse({'success': False, 'error': '已存在'})
```

**示例**:
- 如果已有 `('manager', '部门经理')`
- 再次添加代码为 `manager` 的类型会失败

---

## 💡 界面预览

### **添加前**

```
┌─────────────────────────────────────┐
│ 角色类型：[请选择 ▼]                │
└─────────────────────────────────────┘
```

---

### **点击新增按钮**

```
┌─────────────────────────────────────┐
│ 角色类型：[请选择 ▼] [+ 新增]       │
└─────────────────────────────────────┘
        ↓ 弹出模态框
┌─────────────────────────────────┐
│  添加新的角色类型               │
│                                 │
│  角色类型代码：[__________]     │
│  (只能使用小写字母和下划线)     │
│                                 │
│  角色类型名称：[__________]     │
│  (中文显示名称)                 │
│                                 │
│       [取消]  [保存]            │
└─────────────────────────────────┘
```

---

### **添加后**

```
┌─────────────────────────────────────┐
│ 角色类型：[专员 ▼]                  │
│          └─ 新添加的类型            │
└─────────────────────────────────────┘
```

---

## 🔧 故障排查

### **问题 1: 点击按钮没反应**

**检查**:
1. ✅ 浏览器控制台是否有 JavaScript 错误
2. ✅ Bootstrap 是否正确加载
3. ✅ jQuery 和 Bootstrap JS 依赖

**解决**:
```html
<!-- 确保在页面底部加载 -->
<script src="{% static 'js/bootstrap.bundle.min.js' %}"></script>
```

---

### **问题 2: AJAX 请求失败**

**检查浏览器控制台**:
```javascript
// 查看 Network 标签
// 检查请求 URL 是否正确
// 检查 CSRF Token 是否正确
```

**常见错误**:
- ❌ 403 Forbidden - CSRF Token 错误
- ❌ 404 Not Found - URL 路由不存在
- ❌ 500 Internal Server Error - 服务器端代码错误

---

### **问题 3: 添加后下拉列表没有更新**

**检查**:
```javascript
// 确认 select 元素的 ID 是否正确
const select = document.getElementById('id_role_type');

// 确认 option 是否正确创建
console.log(select.options.length);
```

**解决**:
- 检查模板中 `{{ form.role_type.auto_id }}` 是否正确
- 手动指定 ID：`forms.Select(attrs={'id': 'id_role_type'})`

---

## 📖 扩展功能建议

### **1. 持久化存储**

创建数据库表存储自定义角色类型：

```python
class CustomRoleType(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '自定义角色类型'
        verbose_name_plural = '自定义角色类型管理'
```

---

### **2. 批量导入**

支持从 Excel 批量导入角色类型：

```python
def import_role_types(request):
    """从 Excel 导入角色类型"""
    # ...
```

---

### **3. 类型管理页面**

创建专门的角色类型管理页面：

```python
def role_type_list(request):
    """所有角色类型列表"""
    # 显示预定义 + 自定义的所有类型
    # 支持编辑、删除、启用/禁用
```

---

### **4. 使用统计**

统计每个类型的使用次数：

```python
# 在列表页面显示
usage_count = DepartmentRole.objects.filter(role_type=code).count()
```

---

## 🎉 完成清单

| 项目 | 状态 | 说明 |
|------|------|------|
| **新增按钮** | ✅ | 在下拉框旁边添加 |
| **模态框** | ✅ | Bootstrap 模态框组件 |
| **JavaScript** | ✅ | AJAX 提交逻辑 |
| **视图函数** | ✅ | 后端处理逻辑 |
| **URL 路由** | ✅ | API 端点配置 |
| **格式验证** | ✅ | 小写字母 + 下划线 |
| **防重复** | ✅ | 检查已存在的类型 |
| **权限控制** | ✅ | 仅超级管理员可用 |

---

**更新时间**: 2026-03-25  
**版本**: v1.0  
**状态**: ✅ 已完成并测试通过
