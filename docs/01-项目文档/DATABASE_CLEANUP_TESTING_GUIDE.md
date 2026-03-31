# 数据库清理 - 阶段 3a 测试指南

## ✅ **已修改完成的功能**

### **测试范围：** `views_project.py` 核心功能

---

## 📋 **测试清单**

### **测试 1：项目列表显示** ⭐⭐⭐

**测试路径：** `/projects/` 或 `/project_ledger/`

**预期结果：**
- ✅ 页面正常显示
- ✅ 所有项目数据可见
- ✅ 搜索功能正常
- ✅ 分页功能正常
- ✅ 筛选功能正常（状态、类别等）

**测试步骤：**
```
1. 访问 http://localhost:8000/projects/
2. 检查页面是否正常加载
3. 查看是否有项目数据显示
4. 尝试搜索项目名称
5. 尝试使用筛选条件
6. 测试分页功能
```

**可能的问题：**
- ❌ 模板找不到 → 应该使用 `project_ledger/list.html`
- ❌ 字段不匹配 → ProjectDetail 没有 `project_category` 字段
- ❌ 筛选器异常 → 需要调整筛选逻辑

---

### **测试 2：新增项目** ⭐⭐⭐

**测试路径：** 点击"新增项目"按钮

**预期结果：**
- ✅ 表单页面正常显示
- ✅ 提交后保存到 `ProjectDetail` 表
- ✅ 重定向到项目台账列表
- ✅ 显示成功消息："✓ 项目创建成功！"

**测试步骤：**
```
1. 在项目列表页面点击"新增项目"
2. 填写表单：
   - 项目编号：TEST001
   - 合同编号：HT-TEST001
   - 项目名称：测试项目
   - 合同类别：选择一项
   - 项目状态：选择一项
   - 其他必填字段...
3. 提交表单
4. 检查是否跳转到项目台账列表
5. 检查是否看到新创建的项目
6. 检查成功提示消息
```

**验证方法：**
```sql
-- 在数据库中验证
sqlite> SELECT project_code, project_name FROM eims_app_projectdetail WHERE project_code='TEST001';
-- 应该返回刚创建的项目
```

**可能的问题：**
- ❌ 表单字段不匹配 → ProjectLedgerForm 可能缺少某些字段
- ❌ 模板渲染错误 → 使用了错误的模板
- ❌ 重定向 URL 错误 → 应该到 project_ledger_list

---

### **测试 3：编辑项目** ⭐⭐⭐

**测试路径：** 在列表中点击某个项目的"编辑"按钮

**预期结果：**
- ✅ 表单页面正常显示，带出原有数据
- ✅ 修改后保存成功
- ✅ 数据更新到 `ProjectDetail` 表
- ✅ 重定向到项目台账列表
- ✅ 显示成功消息："✓ 项目更新成功！"

**测试步骤：**
```
1. 在项目列表中找到一个现有项目
2. 点击"编辑"按钮
3. 检查表单是否正确填充原有数据
4. 修改某些字段（如项目名称）
5. 提交表单
6. 检查是否跳转到项目台账列表
7. 检查修改是否生效
8. 检查成功提示消息
```

**验证方法：**
```sql
-- 在数据库中验证
sqlite> SELECT project_code, project_name FROM eims_app_projectdetail WHERE project_code='TEST001';
-- 项目名称应该是修改后的值
```

**可能的问题：**
- ❌ 表单数据未正确加载 → instance 参数问题
- ❌ 保存失败 → 字段验证错误
- ❌ 更新到错误的表 → 仍在使用 Project 模型

---

### **测试 4：删除项目** ⭐⭐⭐

**测试路径：** 在列表中点击某个项目的"删除"按钮

**预期结果：**
- ✅ 删除确认页面正常显示
- ✅ 确认后从 `ProjectDetail` 表删除
- ✅ 重定向到项目台账列表
- ✅ 显示成功消息："✓ 项目删除成功！"

**测试步骤：**
```
1. 在项目列表中找到一个测试项目
2. 点击"删除"按钮
3. 在删除确认页面点击确认
4. 检查是否跳转到项目台账列表
5. 检查该项目是否消失
6. 检查成功提示消息
```

**验证方法：**
```sql
-- 在数据库中验证
sqlite> SELECT COUNT(*) FROM eims_app_projectdetail WHERE project_code='TEST001';
-- 应该返回 0（已删除）
```

**可能的问题：**
- ❌ 删除失败 → 外键约束
- ❌ 删除了错误的表 → 仍在使用 Project 模型
- ❌ 重定向 URL 错误

---

### **测试 5：批量删除** ⭐⭐

**测试路径：** 在列表中勾选多个项目，点击"批量删除"

**预期结果：**
- ✅ 复选框可以选择多个项目
- ✅ 批量删除操作执行成功
- ✅ 从 `ProjectDetail` 表删除选中项目
- ✅ 显示成功消息："✓ 成功删除 X 个项目！"

**测试步骤：**
```
1. 在项目列表中勾选 2-3 个项目
2. 点击"批量删除"按钮
3. 确认删除
4. 检查这些项目是否都消失了
5. 检查成功提示消息
```

**验证方法：**
```sql
-- 在数据库中验证
sqlite> SELECT COUNT(*) FROM eims_app_projectdetail;
-- 总数应该减少
```

**可能的问题：**
- ❌ JavaScript 错误 → 复选框选择逻辑
- ❌ POST 数据格式错误 → project_ids 获取失败
- ❌ 删除操作未执行

---

### **测试 6：导出 Excel** ⭐⭐

**测试路径：** 在列表中点击"导出"按钮

**预期结果：**
- ✅ 下载 Excel 文件
- ✅ 文件名：`项目台账数据.xlsx`
- ✅ 包含正确的列头
- ✅ 数据来自 `ProjectDetail` 表

**测试步骤：**
```
1. 在项目列表页面点击"导出"按钮
2. 检查是否开始下载
3. 打开下载的 Excel 文件
4. 检查列头是否正确：
   - 项目编号、合同编号、项目名称、合同类别...
5. 检查数据是否完整
6. 检查中文字符是否正常
```

**验证要点：**
```
✅ 文件名：项目台账数据.xlsx
✅ 列数：14 列
✅ 列头：['项目编号', '合同编号', '项目名称', '合同类别', 
         '项目状态', '合同状态', '合同甲方', '合同乙方',
         '签订日期', '合同总价 (元)', '项目地址',
         '现场负责人', '项目总监', '备注']
✅ 数据：与数据库一致
```

**可能的问题：**
- ❌ 文件名错误 → 仍是"项目数据.xlsx"
- ❌ 列头缺失 → headers 定义不完整
- ❌ 数据为空 → queryset 查询失败
- ❌ 中文乱码 → 编码问题

---

### **测试 7：导入功能** ⭐⭐

**测试路径：** 访问 `/projects/import/`

**预期结果：**
- ✅ 自动重定向到项目台账导入页面
- ✅ 显示提示信息："ℹ️ 请使用项目台账导入功能"

**测试步骤：**
```
1. 访问 http://localhost:8000/projects/import/
2. 检查是否自动跳转
3. 检查是否显示提示消息
4. 检查最终 URL 是否为 /project_ledger/import/
```

**验证要点：**
```
✅ 重定向发生
✅ 消息提示正确
✅ 最终到达项目台账导入页面
```

**可能的问题：**
- ❌ 未重定向 → 函数逻辑错误
- ❌ 404 错误 → URL 配置问题
- ❌ 无提示信息 → messages 未正确设置

---

### **测试 8：AJAX 查询（如果有此功能）** ⭐

**测试路径：** `GET /api/project/by_contract/?code=XXX`

**预期结果：**
- ✅ 返回 JSON 格式数据
- ✅ 数据来自 `ProjectDetail` 表
- ✅ 包含正确的字段

**测试步骤：**
```javascript
// 在浏览器控制台测试
fetch('/api/project/by_contract/?code=TEST001')
  .then(r => r.json())
  .then(data => console.log(data))

// 预期返回：
// {id: 1, name: "测试项目"}
```

**可能的问题：**
- ❌ 404 错误 → URL 未配置
- ❌ 500 错误 → 查询逻辑错误
- ❌ 返回空数据 → filter 条件错误

---

## 🔍 **数据库验证脚本**

### **验证 1：检查数据是否在正确的表中**

```sql
-- 检查 ProjectDetail 表
sqlite> SELECT 
    project_code, 
    contract_code, 
    project_name, 
    contract_category,
    created_at
FROM eims_app_projectdetail
ORDER BY created_at DESC
LIMIT 10;

-- 应该有数据
```

### **验证 2：检查旧表是否还有数据**

```sql
-- 检查 Project 表（应该没有新数据）
sqlite> SELECT COUNT(*) FROM eims_app_project;
-- 如果数量增加，说明还在写入旧表 ❌

-- 检查 Contract 表（应该没有新数据）
sqlite> SELECT COUNT(*) FROM eims_app_Contract;
-- 如果数量增加，说明还在写入旧表 ❌
```

### **验证 3：检查数据完整性**

```sql
-- 检查必填字段
sqlite> SELECT 
    COUNT(*) as total,
    COUNT(project_code) as has_project_code,
    COUNT(contract_code) as has_contract_code,
    COUNT(project_name) as has_project_name
FROM eims_app_projectdetail;

-- 所有计数应该接近 total（允许少量 NULL）
```

---

## 🐛 **常见问题诊断**

### **问题 1：模板找不到**

**错误信息：**
```
TemplateDoesNotExist: project/list.html
```

**解决方案：**
```python
# views_project.py 中检查
template_name = 'project_ledger/list.html'  # ✅ 正确
# template_name = 'project/list.html'      # ❌ 错误
```

---

### **问题 2：字段不存在**

**错误信息：**
```
FieldError: Cannot resolve keyword 'project_category' into field.
```

**解决方案：**
```python
# ProjectDetail 没有 project_category 字段
# 应该使用 contract_category

# 检查筛选逻辑
queryset.filter(contract_category=selected_category)  # ✅
# queryset.filter(project_category=selected_category)  # ❌
```

---

### **问题 3：重定向 URL 错误**

**错误信息：**
```
NoReverseMatch: 'project_list' is not a registered url
```

**解决方案：**
```python
# 检查 success_url
success_url = reverse_lazy('eims_app:project_ledger_list')  # ✅
# success_url = reverse_lazy('eims_app:project_list')      # ❌
```

---

### **问题 4：表单验证失败**

**错误信息：**
```
ValidationError: {'project_code': ['This field is required.']}
```

**解决方案：**
```python
# 检查表单字段是否完整
# ProjectLedgerForm 的 Meta.fields 是否包含所有必填字段

# 或者在模板中添加必填字段提示
<input type="text" name="project_code" required>
```

---

## 📊 **测试结果记录表**

| 测试项 | 状态 | 问题描述 | 备注 |
|--------|------|----------|------|
| **测试 1：列表显示** | ⏳ 待测试 | - | - |
| **测试 2：新增项目** | ⏳ 待测试 | - | - |
| **测试 3：编辑项目** | ⏳ 待测试 | - | - |
| **测试 4：删除项目** | ⏳ 待测试 | - | - |
| **测试 5：批量删除** | ⏳ 待测试 | - | - |
| **测试 6：导出 Excel** | ⏳ 待测试 | - | - |
| **测试 7：导入功能** | ⏳ 待测试 | - | - |
| **测试 8：AJAX 查询** | ⏳ 待测试 | - | - |

**总体状态：** ⏳ 等待测试

---

## 🚀 **测试环境准备**

### **1. 启动开发服务器**

```bash
cd e:\EIMS2026
python manage.py runserver
```

**预期输出：**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### **2. 清除浏览器缓存**

```
按 Ctrl + Shift + R（硬刷新）
或
按 Ctrl + F5
```

### **3. 登录系统**

```
访问：http://127.0.0.1:8000/admin/login/
使用管理员账号登录
```

### **4. 开启开发者工具**

```
按 F12 打开浏览器开发者工具
切换到 Console 和 Network 标签
```

---

## 💡 **测试建议**

### **优先级顺序：**

1. ⭐⭐⭐ **必须测试**
   - 测试 1：列表显示
   - 测试 2：新增项目
   - 测试 3：编辑项目
   - 测试 4：删除项目

2. ⭐⭐ **重要测试**
   - 测试 5：批量删除
   - 测试 6：导出 Excel

3. ⭐ **可选测试**
   - 测试 7：导入功能
   - 测试 8：AJAX 查询

### **测试环境：**

- ✅ 开发环境（本地）
- ✅ 测试数据库（可以重置）
- ✅ 有测试数据

### **测试时间：**

- 完整测试：约 30 分钟
- 核心测试：约 15 分钟

---

## 📞 **测试完成后**

### **如果测试通过 ✅**

请告诉我：
```
测试通过！所有功能正常工作。
```

我将继续完成剩余的工作：
1. 完成 views_project.py 剩余部分
2. 修改 views_contract.py
3. 修改其他关联视图
4. 数据迁移
5. 删除旧表

---

### **如果发现问题 ❌**

请提供：
```
测试 X 失败
错误信息：[复制完整的错误信息]
操作步骤：[描述您做了什么]
截图：[如果有的话]
```

我将立即修复问题！

---

## 🎯 **下一步行动**

**您的任务：**
1. 按照上述测试指南进行测试
2. 记录测试结果
3. 告诉我测试结论

**我的任务：**
- ⏳ 等待您的测试结果
- ✅ 如果通过 → 继续完成剩余工作
- 🐛 如果有问题 → 立即修复

---

**准备好了吗？请开始测试吧！** 🚀

如果有任何问题，随时告诉我！
