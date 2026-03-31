# ⚠️ 正确的 URL 格式说明

## 🐛 您遇到的错误

```
Page not found (404)
"E:\EIMS2026\project-ledger\1\detail"不存在
Request URL: http://localhost:8000/project-ledger/1/detail/
```

**原因**: 您正在访问一个**不存在的 URL**

---

## ✅ 正确的 URL 格式

### **错误 vs 正确**

| ❌ 错误（不要使用） | ✅ 正确（使用这个） |
|------------------|------------------|
| `/project-ledger/1/detail/` | `/project_ledger/1/` |
| 横线、包含 detail | 下划线、简洁格式 |

---

## 🎯 完整的项目台账 URL 列表

### **所有可用的 URL**

```python
# 列表页
http://localhost:8000/project_ledger/

# 详情页（主窗体 + 三个子窗体）
http://localhost:8000/project_ledger/1/
http://localhost:8000/project_ledger/2/
http://localhost:8000/project_ledger/5/
...

# 编辑页
http://localhost:8000/project_ledger/1/edit/

# 删除页
http://localhost:8000/project_ledger/1/delete/

# 导入
http://localhost:8000/project_ledger/import/

# 导出
http://localhost:8000/project_ledger/export/
```

---

## 🔍 为什么您的 URL 是错误的？

### **错误分析**

您访问的 URL: `http://localhost:8000/project-ledger/1/detail/`

**包含 3 个错误**:

1. ❌ **使用了横线** `-` 而不是下划线 `_`
   - 错误：`project-ledger`
   - 正确：`project_ledger`

2. ❌ **包含了多余的 `/detail`**
   - 错误：`/1/detail/`
   - 正确：`/1/`

3. ❌ **路径过长**
   - Django 配置的路径是：`project_ledger/<int:pk>/`
   - 不是：`project-ledger/<int:pk>/detail/`

---

## 🚀 如何正确访问项目详情

### **方法 1: 从列表页进入（推荐）**

1. 访问项目列表：
   ```
   http://localhost:8000/projects/
   ```

2. **双击**任意一行
   - ✅ 自动跳转到正确的详情页 URL

---

### **方法 2: 直接输入 URL**

在浏览器地址栏输入：
```
http://localhost:8000/project_ledger/1/
```

**注意**:
- ✅ 使用**下划线** `_` 不是横线 `-`
- ✅ 不需要 `/detail` 后缀
- ✅ 末尾可以有斜杠 `/`

---

### **方法 3: 使用旧 URL 自动重定向**

访问旧的项目管理 URL：
```
http://localhost:8000/projects/1/
```

✅ 会自动重定向到：
```
http://localhost:8000/project_ledger/1/
```

---

## 💡 快速记忆技巧

### **URL 结构公式**

```
项目台账详情 URL = /project_ledger/{项目 ID}/

示例:
项目 ID = 1  →  /project_ledger/1/
项目 ID = 5  →  /project_ledger/5/
项目 ID = 99 →  /project_ledger/99/
```

---

### **关键词拼写检查**

```
✅ project_ledger
   └─┬─┘ └──┬──┘
     项目    台账
   
❌ project-ledger (横线错误)
❌ project ledger (空格错误)
❌ projectLedger (驼峰错误)
```

---

## ⚠️ 常见错误示例

### **错误 1: 使用横线**

```
❌ http://localhost:8000/project-ledger/1/
✅ http://localhost:8000/project_ledger/1/
```

**原因**: Django URL 配置使用下划线

---

### **错误 2: 添加多余路径**

```
❌ http://localhost:8000/project_ledger/1/detail/
✅ http://localhost:8000/project_ledger/1/
```

**原因**: URL 路由定义就是 `project_ledger/<int:pk>/`，没有 `/detail`

---

### **错误 3: 混淆模块名称**

```
❌ http://localhost:8000/projects/1/detail/  (这是旧的项目管理模块)
✅ http://localhost:8000/project_ledger/1/   (这是新的项目台账模块)
```

**说明**: 
- `/projects/` → 旧的项目管理模块（已废弃）
- `/project_ledger/` → 新的项目台账模块（当前使用）

---

## 📊 URL 对比表

### **新旧模块 URL 对比**

| 功能 | 旧模块 URL | 新模块 URL | 状态 |
|------|-----------|-----------|------|
| **列表页** | `/projects/` | `/project_ledger/` | ✅ 两者都可用 |
| **详情页** | `/projects/1/` | `/project_ledger/1/` | ✅ 自动重定向 |
| **编辑页** | `/projects/1/edit/` | `/project_ledger/1/edit/` | ✅ 两者都可用 |
| **删除页** | `/projects/1/delete/` | `/project_ledger/1/delete/` | ✅ 两者都可用 |

---

## 🔧 如果您还是遇到 404

### **步骤 1: 清除浏览器缓存**

```
按 Ctrl + Shift + Delete
选择"缓存的图片和文件"
点击"清除数据"
```

---

### **步骤 2: 硬刷新页面**

```
按 Ctrl + F5 (Windows)
或 Cmd + Shift + R (Mac)
```

---

### **步骤 3: 检查服务器是否运行**

确保 Django 开发服务器正在运行：
```bash
python manage.py runserver
```

应该看到：
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

---

### **步骤 4: 检查 URL 配置**

打开 `eims_app/urls.py`，确认有以下配置：

```python
# 第 248 行左右
path('project_ledger/<int:pk>/', views_project_ledger.project_ledger_detail, name='project_ledger_detail'),
```

如果没有，说明配置被意外删除了。

---

## 📖 相关资源

### **官方文档**

- [Django URL 配置](https://docs.djangoproject.com/en/stable/topics/http/urls/)
- [Django 命名约定](https://docs.djangoproject.com/en/stable/internals/contributing/writing-code/coding-style/)

---

### **项目文档**

- [URL 路径格式修复](file://URL_PATH_FORMAT_FIX.md)
- [重定向配置说明](file://PROJECT_REDIRECT_CONFIG.md)
- [项目详情页结构](file://PROJECT_DETAIL_MAIN_SUB_PANELS.md)

---

## 🎯 总结

### **记住这个正确的 URL**

```
✅ http://localhost:8000/project_ledger/1/
   └─┬─┘        └─┬─┘ └─┬┘
     模块名       ID   斜杠
```

**特点**:
- ✅ 使用下划线 `_`
- ✅ 格式简洁（没有多余的 `/detail`）
- ✅ 符合 Django 规范

---

**更新时间**: 2026-03-25  
**版本**: v1.0  
**目的**: 帮助用户理解和使用正确的 URL 格式
