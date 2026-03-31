# CSRF 批量删除问题修复

## 🐛 **错误描述**

```
POST http://localhost:8000/projects/batch-delete/ 403 (Forbidden)
CSRF token missing
```

---

## 🔍 **问题原因**

项目列表页面 (`project/list.html`) 是一个纯展示页面，没有表单提交，因此之前没有包含 CSRF token。

但是**批量删除功能**使用 JavaScript 动态创建表单并提交，需要 CSRF token 验证。

JavaScript 代码尝试从页面获取 CSRF token：
```javascript
var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
```

但页面上没有这个元素，导致 CSRF 验证失败！

---

## ✅ **修复方案**

### **已修复**

在 `project/list.html` 的 `{% block content %}` 后添加隐藏的 CSRF token：

```html
{% block content %}
<!-- CSRF token for JavaScript operations -->
<input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf_token }}">

<div class="container-fluid py-4">
    <!-- 原有内容 -->
</div>
{% endblock %}
```

---

## 🎯 **测试步骤**

### **1. 强制刷新浏览器**
```
按 Ctrl + F5
或
按 Ctrl + Shift + R
```

### **2. 测试批量删除**

```
1. 访问项目列表：http://localhost:8000/projects/
2. 勾选多个项目（至少 2 个）
3. 点击"删除"按钮（之前是禁用状态）
4. 确认删除对话框
5. ✅ 应该成功删除，并显示："✓ 成功删除 X 个项目！"
```

---

## 🔧 **技术细节**

### **JavaScript 批量删除逻辑**

位置：`project/list.html` 第 710-745 行

```javascript
// 批量删除
var batchDeleteBtn = document.getElementById('batch-delete');
if (batchDeleteBtn) {
    batchDeleteBtn.addEventListener('click', function() {
        if (selectedProjectIds.size === 0) return;
        if (confirm('确定要删除选中的 ' + selectedProjectIds.size + ' 个项目吗？')) {
            var form = document.createElement('form');
            form.method = 'POST';
            form.action = '{% url "eims_app:project_batch_delete" %}';
            
            // ✅ 获取 CSRF token
            var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
            if (csrfToken) {
                var csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrfmiddlewaretoken';
                csrfInput.value = csrfToken.value;
                form.appendChild(csrfInput);
            }
            
            // 添加选中的项目 ID
            selectedProjectIds.forEach(function(id) {
                var input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'project_ids[]';
                input.value = id;
                form.appendChild(input);
            });
            
            document.body.appendChild(form);
            form.submit();
        }
    });
}
```

---

## 📝 **相关文件**

### **模板文件**
- ✅ `project/list.html` - 已添加 CSRF token
- ✅ `project/delete.html` - 已有 CSRF token
- ✅ `project/add.html` - 已有 CSRF token
- ✅ `project/edit.html` - 已有 CSRF token
- ✅ `project/detail.html` - 已有 CSRF token

### **视图文件**
- ✅ `views_project.py` - `project_batch_delete` 函数
  - 使用 `@login_required` 装饰器
  - 只接受 POST 请求
  - 处理批量删除逻辑

---

## ⚠️ **注意事项**

### **1. 权限要求**
批量删除功能只对**超级管理员**可用：

```python
@login_required
def project_batch_delete(request):
    if not request.user.is_superuser:
        messages.error(request, '您没有权限执行批量删除操作')
        return redirect('eims_app:project_list')
    # ...
```

### **2. 浏览器缓存**
修改后需要强制刷新浏览器才能生效：
```
Ctrl + F5
或
Ctrl + Shift + R
```

### **3. 安全检查**
在执行删除前会确认：
- 用户已登录
- 用户是超级管理员
- 至少选择了一个项目
- 用户确认删除操作

---

## 🎉 **成功标志**

如果看到以下提示，说明批量删除成功：

```
✓ 成功删除 X 个项目！
```

---

## 💡 **其他可能的 CSRF 问题**

如果批量删除修复后还有其他 CSRF 错误，检查：

### **1. 搜索功能**
搜索表单是 GET 请求，不需要 CSRF token

### **2. 导出功能**
如果是 GET 请求导出，不需要 CSRF token
如果是 POST 请求导出，需要添加 CSRF token

### **3. 导入功能**
✅ 已有 CSRF token（`project/import.html` 第 50 行）

---

## 🔍 **调试技巧**

### **在浏览器控制台检查**

```javascript
// 1. 检查 CSRF token 是否存在
document.querySelector('[name=csrfmiddlewaretoken]')
// 应该返回：<input type="hidden" name="csrfmiddlewaretoken" value="xxxxx">

// 2. 检查值是否有效
document.querySelector('[name=csrfmiddlewaretoken]').value
// 应该返回一个长字符串

// 3. 检查批量删除按钮
document.getElementById('batch-delete')
// 应该返回：<button id="batch-delete">...</button>
```

---

## 📞 **需要帮助？**

如果修复后仍然遇到 CSRF 错误，请提供：

1. **具体操作**：点击哪个按钮？
2. **错误信息**：完整的错误提示
3. **浏览器控制台**：F12 → Console 中的错误
4. **网络请求**：F12 → Network 中的 POST 请求详情

我会帮您进一步诊断！🔍

---

**修复完成！现在批量删除功能应该可以正常工作了！** ✅

请立即测试：
1. 强制刷新浏览器（Ctrl + F5）
2. 访问项目列表
3. 勾选多个项目
4. 点击删除按钮
5. 确认删除

应该成功！🎉
