# 🔧 项目详情功能问题排查

## ⚠️ 可能的问题

### **1. 浏览器缓存**

**症状**: 
- 页面没有高亮效果
- 点击行没有反应
- 布局仍然是旧的

**原因**: 浏览器缓存了旧版本的 CSS 和 HTML 文件

---

## ✅ 解决方案

### **方法 1: 硬刷新（推荐）**

在浏览器中打开页面后，按以下快捷键：

#### **Chrome / Edge**
```
Ctrl + Shift + R
或
Ctrl + F5
```

#### **Firefox**
```
Ctrl + Shift + R
或
Ctrl + F5
```

#### **Safari (Mac)**
```
Cmd + Shift + R
```

---

### **方法 2: 清除缓存并硬性重新加载**

1. 按 `F12` 打开开发者工具
2. 右键点击浏览器的刷新按钮
3. 选择"清空缓存并硬性重新加载"

---

### **方法 3: 手动清除缓存**

#### **Chrome / Edge**
1. 按 `Ctrl + Shift + Delete`
2. 选择"缓存的图片和文件"
3. 时间范围："全部"
4. 点击"清除数据"

#### **Firefox**
1. 按 `Ctrl + Shift + Delete`
2. 勾选"缓存"
3. 点击"立即清除"

---

### **方法 4: 使用无痕模式**

1. 按 `Ctrl + Shift + N` (Chrome/Edge)
2. 或 `Ctrl + Shift + P` (Firefox)
3. 在新窗口中访问页面

---

## 🎨 预期效果

### **正常状态**

访问 http://localhost:8000/projects/ 后应该看到：

```
┌─────────────────────────────────────────────────────┐
│              项目台账管理系统                        │
├─────────────────────────────────────────────────────┤
│ [搜索筛选区域]                                      │
├───────────────────────────┬─────────────────────────┤
│   项目列表 (9 列 - 更宽)    │   项目详情 (3 列)        │
│                           │                         │
│ ┌───┬────┬────┬────┐     │  ┌───────────────────┐  │
│ │☐ │项目 A│状态│操作│     │  │ 📋 项目详情       │  │
│ │☑ │项目 B│状态│操作│ ←  │  ├───────────────────┤  │
│ │☐ │项目 C│状态│操作│     │  │ 基本信息          │  │
│ └───┴────┴────┴────┘     │  │ - 项目编号：XXX   │  │
│   ↑ 第一行默认高亮        │  │ - 项目名称：XXX   │  │
│   → 蓝色背景 + 左边框      │  │ - 合同金额：XXX   │  │
│                           │  └───────────────────┘  │
└───────────────────────────┴─────────────────────────┘
```

---

## 🔍 检查清单

### **1. 视觉检查**

- [ ] 第一行是否有蓝色背景？
- [ ] 第一行左侧是否有蓝色边框？
- [ ] 右侧是否有详情面板？
- [ ] 列表是否占据大部分宽度（约 75%）？

### **2. 交互检查**

- [ ] 鼠标悬停时，行背景是否变浅蓝色？
- [ ] 点击某一行，该行是否高亮？
- [ ] 点击后，右侧详情是否更新？
- [ ] URL 是否添加了 `current_id` 参数？

### **3. 复选框检查**

- [ ] 点击复选框，是否只选中复选框？
- [ ] 复选框是否不会触发行选择？

---

## 🐛 常见问题

### **Q1: 列表仍然很窄**

**原因**: 浏览器仍在使用旧的 CSS

**解决**:
1. 硬刷新：`Ctrl + Shift + R`
2. 如果不行，清除缓存
3. 或者使用无痕模式测试

---

### **Q2: 没有高亮效果**

**可能原因**:
1. CSS 未加载（缓存问题）
2. JavaScript 错误
3. Django 模板渲染问题

**检查步骤**:

1. **打开开发者工具** (`F12`)
2. **查看 Console** - 是否有 JavaScript 错误？
3. **查看 Network** - CSS 文件是否加载成功？
4. **查看 Elements** - 检查 `<tr>` 元素是否有正确的类名？

**期望的 HTML 结构**:
```html
<tr class="clickable-row active" onclick="selectProject(1)">
    <td class="text-center">
        <input type="checkbox" ...>
    </td>
    <!-- 其他单元格 -->
</tr>
```

**检查 CSS 是否应用**:
```javascript
// 在 Console 中执行
document.querySelector('.clickable-row.active')
// 应该返回第一个高亮的行

// 检查样式
window.getComputedStyle(document.querySelector('.clickable-row.active'))
// backgroundColor 应该是 "rgba(0, 123, 255, 0.1)"
```

---

### **Q3: 点击行没有反应**

**可能原因**:
1. JavaScript 未加载
2. `selectProject` 函数未定义
3. 事件绑定失败

**检查步骤**:

1. **打开 Console** (`F12`)
2. **输入测试代码**:
```javascript
typeof selectProject
// 应该返回 "function"
```

3. **如果返回 "undefined"**，说明 JS 未加载
   - 硬刷新页面
   - 检查网络请求中的 JS 文件

---

### **Q4: 详情面板不显示**

**可能原因**:
1. `current_project` 为 `None`
2. 后端视图未正确传递数据
3. 模板条件判断失败

**检查步骤**:

1. **查看页面源码** (`Ctrl + U`)
2. **搜索** `detail-panel`
3. **检查** `{% if current_project %}` 内的内容是否存在

**如果不存在**，说明后端问题：
- 检查数据库是否有项目记录
- 检查视图函数的 `current_project` 逻辑

---

## 🛠️ 调试技巧

### **1. 添加调试信息**

在模板中添加：

```html
<!-- 调试信息 -->
<div style="background: yellow; padding: 10px; margin: 10px;">
    <strong>调试:</strong>
    <br>current_project: {{ current_project }}
    <br>page_obj count: {{ page_obj|length }}
</div>
```

---

### **2. 测试 JavaScript**

在 Console 中手动执行：

```javascript
// 测试选择功能
selectProject(1);

// 测试高亮
document.querySelector('tr:nth-child(2)').classList.add('active');
```

---

### **3. 检查 CSS**

在 Console 中：

```javascript
// 检查 clickable-row 样式
const style = document.createElement('style');
style.textContent = `
    .clickable-row { cursor: pointer; }
    .clickable-row:hover { background-color: rgba(0, 123, 255, 0.05); }
    .clickable-row.active { background-color: rgba(0, 123, 255, 0.1); border-left: 3px solid #007bff; }
`;
document.head.appendChild(style);
```

---

## 📊 性能优化

### **如果页面加载慢**

1. **检查 Network** - 哪些文件加载慢？
2. **压缩静态文件** - CSS、JS
3. **启用 gzip** - Django 配置
4. **使用 CDN** - Bootstrap、jQuery 等

---

## ✅ 验证成功的标准

完成以下步骤，全部通过即为成功：

1. ✅ **视觉检查**
   - 第一行有蓝色高亮
   - 右侧有详情面板
   - 列表宽度占约 75%

2. ✅ **交互检查**
   - 鼠标悬停有浅色背景
   - 点击行切换高亮
   - 详情实时更新

3. ✅ **功能检查**
   - 复选框独立工作
   - URL 同步更新
   - 刷新保持状态

---

## 🚀 快速测试命令

### **1. 重启 Django 服务器**

```bash
# 停止服务器 (Ctrl + C)
# 重新启动
python manage.py runserver
```

### **2. 访问页面**

```
http://localhost:8000/projects/
```

### **3. 硬刷新**

```
Ctrl + Shift + R
```

---

## 📝 修改记录

### **Version 2.0 改进**

1. **布局优化**
   - 列表从 8 列改为 9 列（更宽）
   - 详情从 4 列改为 3 列
   - 添加粘性定位

2. **样式增强**
   - 移除列表底部间距
   - 详情面板固定在顶部
   - 高亮效果更明显

3. **版本标记**
   - 添加注释便于识别
   - 强制浏览器刷新

---

## 💡 联系支持

如果以上方法都无效，请提供：

1. **浏览器类型和版本**
2. **Console 中的错误信息**
3. **Network 中的失败请求**
4. **页面截图**

这样可以更快定位问题！

---

**更新时间**: 2026-03-25 08:30  
**版本**: 2.0  
**状态**: 已部署，待刷新
