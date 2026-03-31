# CSRF 验证失败解决方案

## 🐛 **错误描述**

```
禁止访问 (403)
CSRF 验证失败。请求被中断。
Reason: CSRF token missing.
```

---

## ✅ **解决方案**

### **方案 1：强制刷新浏览器（最常用）**

**步骤**：
```
1. 按 Ctrl + Shift + Delete
2. 选择"Cookie 和其他网站数据"
3. 选择"缓存的图片和文件"
4. 点击"清除数据"
5. 关闭浏览器
6. 重新打开浏览器
7. 重新登录系统
8. 再次尝试提交表单
```

**或者更简单的方法**：
```
按 Ctrl + F5 强制刷新页面
```

---

### **方案 2：清除浏览器缓存**

#### **Chrome/Edge**
```
1. 按 F12 打开开发者工具
2. 右键点击刷新按钮
3. 选择"清空缓存并硬性重新加载"
```

#### **Firefox**
```
1. 按 Ctrl + Shift + Delete
2. 选择"缓存"
3. 点击"立即清除"
```

#### **Safari**
```
1. 开发菜单 → 清空缓存
2. 或使用 Command + Option + E
```

---

### **方案 3：检查 Cookie 设置**

**确保浏览器允许 Cookie**：

#### **Chrome/Edge**
```
1. 点击右上角三个点 → 设置
2. 隐私和安全 → Cookie 及其他网站数据
3. 确保未阻止所有 Cookie
4. 添加例外：http://localhost:8000
```

#### **Firefox**
```
1. 右上角菜单 → 选项
2. 隐私与安全 → Cookie 和网站数据
3. 确保未启用"增强型跟踪保护"的严格模式
```

---

### **方案 4：使用无痕模式**

**临时解决方案**：
```
1. Chrome/Edge: Ctrl + Shift + N
2. Firefox: Ctrl + Shift + P
3. Safari: Command + Shift + N
4. 访问 http://localhost:8000/
5. 登录并测试
```

---

### **方案 5：检查 Django 设置**

如果以上方法都无效，检查 `settings.py`：

```python
# settings.py

# 确保有以下设置（通常默认就有）
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# CSRF 相关设置（一般不需要修改）
CSRF_COOKIE_SECURE = False  # HTTP 下为 False
CSRF_COOKIE_HTTPONLY = False  # 需要 JavaScript 访问时设为 False
CSRF_COOKIE_SAMESITE = 'Lax'  # 或 'None'（跨域时）
```

---

## 🔍 **验证步骤**

### **步骤 1：检查表单是否有 csrf_token**

在浏览器中查看页面源代码（右键 → 查看页面源代码），搜索 `csrfmiddlewaretoken`：

```html
<form method="post">
    <input type="hidden" name="csrfmiddlewaretoken" value="xxxxxxxxxxxxx">
    ...
</form>
```

✅ **如果有这个隐藏字段** → CSRF token 存在  
❌ **如果没有** → 模板可能有问题

---

### **步骤 2：检查 Cookie**

**Chrome/Edge 开发者工具**：
```
1. 按 F12 打开开发者工具
2. Application → Cookies → http://localhost:8000
3. 查找 csrftoken cookie
4. 应该能看到一个长字符串值
```

**Firefox 开发者工具**：
```
1. 按 F12
2. Storage → Cookies → http://localhost:8000
3. 查找 csrftoken
```

---

### **步骤 3：网络请求检查**

**查看 POST 请求是否包含 CSRF token**：
```
1. F12 → Network 标签
2. 提交表单
3. 点击 POST 请求
4. Payload 或 Form Data 标签
5. 应该看到 csrfmiddlewaretoken 参数
```

---

## 💡 **常见原因**

### **原因 1：浏览器缓存旧页面**
- ✅ **解决**：强制刷新（Ctrl + F5）

### **原因 2：Cookie 被禁用或清除**
- ✅ **解决**：启用 Cookie 或重新登录

### **原因 3：会话过期**
- ✅ **解决**：重新登录

### **原因 4：多标签页登录冲突**
- ✅ **解决**：关闭其他标签页，只保留一个

### **原因 5：HTTPS/HTTP混用**
- ✅ **解决**：统一使用 HTTP（本地开发）

---

## 🎯 **快速测试流程**

### **测试 1：项目台账新增**

```
1. 访问 http://localhost:8000/project_ledger/add/
2. 填写表单
   - 项目编号：TEST001
   - 合同编号：HT001
   - 项目名称：测试项目
   - （其他必填字段）
3. 点击"保存"按钮
4. ✅ 应该成功跳转，显示"✓ 项目台账添加成功！"
```

### **测试 2：合同管理新增**

```
1. 访问 http://localhost:8000/contract_management/add/
2. 填写表单
   - 合同类别：工程监理
   - 合同编号：CS001
   - 项目名称：测试合同
   - （其他必填字段）
3. 点击"保存"按钮
4. ✅ 应该成功跳转，显示"✓ 合同添加成功！"
```

---

## ⚠️ **如果仍然失败**

### **调试步骤**

**1. 检查视图函数**

确保视图函数正确传递了 `request`：

```python
# ✅ 正确
@login_required
def project_ledger_add(request):
    if request.method == 'POST':
        form = ProjectLedgerForm(request.POST, request.FILES)
        # ...
    else:
        form = ProjectLedgerForm()
    
    return render(request, 'project_ledger/form.html', {'form': form})

# ❌ 错误 - 忘记传递 request
@login_required
def project_ledger_add(request):
    # ...
    return render('project_ledger/form.html', {'form': form})  # 缺少 request
```

**2. 检查模板渲染**

确保使用 `render()` 而不是直接返回 HttpResponse：

```python
# ✅ 正确
return render(request, 'template.html', context)

# ❌ 错误
return HttpResponse(template.render(context))  # 缺少 request
```

**3. 检查中间件**

确保 `MIDDLEWARE` 中有 `CsrfViewMiddleware`：

```python
# settings.py
MIDDLEWARE = [
    # ...
    'django.middleware.csrf.CsrfViewMiddleware',  # 必须有这个
    # ...
]
```

---

## 📝 **推荐操作顺序**

**第一次遇到**：
```
1. 按 Ctrl + F5 强制刷新 ← 最简单
2. 重新登录
3. 再次尝试提交
```

**如果不行**：
```
1. 清除浏览器缓存和 Cookie
2. 重启浏览器
3. 重新登录
4. 再次尝试
```

**还是不行**：
```
1. 使用无痕模式测试
2. 如果无痕模式可以 → 清除主浏览器的缓存/Cookie
3. 如果都不行 → 检查代码和设置
```

---

## 🎉 **成功标志**

如果看到以下提示，说明 CSRF 验证通过：

**项目台账**：
```
✓ 项目台账添加成功！
✓ 项目台账更新成功！
✓ 项目台账已删除！
```

**合同管理**：
```
✓ 合同添加成功！
✓ 合同更新成功！
✓ 合同已删除！
```

---

## 📞 **需要帮助？**

如果按照以上步骤仍然无法解决，请告诉我：

1. **使用的浏览器**：Chrome/Firefox/Edge/Safari
2. **具体操作步骤**：访问哪个页面 → 填写什么表单 → 点击什么按钮
3. **错误截图**：完整的错误信息
4. **是否已登录**：确认当前登录状态
5. **浏览器控制台错误**：F12 → Console 中的错误信息

我会帮您进一步诊断问题！🔍
