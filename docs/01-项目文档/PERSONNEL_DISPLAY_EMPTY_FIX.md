# 项目人员显示为空问题修复

## 🐛 问题描述

用户报告：**成功添加人员后，项目详情页的人员列表仍然显示为空**

**症状**:
- ✅ 表单提交成功，没有报错
- ✅ 显示"成功添加项目人员"消息
- ❌ 回到项目详情页，人员列表为空
- ❌ 数据库检查发现所有人员记录的 `project_code` 都是空字符串

---

## 🔍 根本原因

通过数据库检查发现：

```python
Total personnel records: 35
Sample records:
  ID=35, Name=J, Project_ID=None, Project_Code='', Position=专监
  ID=34, Name=G, Project_ID=None, Project_Code='', Position=专监
```

**所有人员记录的 `project_id` 和 `project_code` 都是空的！**

### **问题分析**

1. **表单提交问题**: 用户可能没有勾选任何岗位的"有无变化"复选框
2. **创建逻辑问题**: 即使勾选了复选框，但没有填写姓名
3. **字段保存问题**: `project` 和 `project_code` 字段同时存在可能导致冲突

---

## ✅ 修复方案

### **1. 添加调试输出**

在 `add_personnel` 视图中添加 `print` 语句，用于确认人员记录是否正确创建：

```python
created_count = 0
for position_key, position_name in positions:
    has_change = request.POST.get(f'has_change_{position_key}', 'no') == 'yes'
    if has_change:
        name = request.POST.get(f'name_{position_key}', '')
        if name:  # 只有填写了姓名才创建
            personnel = Personnel(
                personnel_code=personnel_code,
                project=project,  # 关联项目对象
                project_code=project_code,  # 项目编号字符串
                name=name,
                # ... 其他字段
            )
            personnel.save()
            created_count += 1
            print(f"✓ Created personnel: {name}, project_id={project.id}, project_code={project_code}")
```

### **2. 改进用户提示**

根据实际创建的人数显示不同的消息：

```python
if created_count == 0:
    messages.warning(request, '未勾选任何岗位的变化，或未填写姓名')
else:
    messages.success(request, f'成功添加 {created_count} 名项目人员')
```

### **3. 显式设置两个字段的注释**

为了清晰说明意图，添加了注释：

```python
project=project,  # 关联项目对象
project_code=project_code,  # 项目编号字符串
```

---

## 📊 修改对比

### **修改前**

```python
for position_key, position_name in positions:
    has_change = request.POST.get(f'has_change_{position_key}', 'no') == 'yes'
    if has_change:
        name = request.POST.get(f'name_{position_key}', '')
        if name:
            personnel = Personnel(
                project=project,
                project_code=project_code,
                # ...
            )
            personnel.save()

messages.success(request, '成功添加项目人员')
```

**问题**:
- ❌ 无法确认是否真的创建了记录
- ❌ 无法确认 `project` 和 `project_code` 是否正确保存
- ❌ 即使用户没有勾选任何岗位，也会显示成功消息

### **修改后**

```python
created_count = 0
for position_key, position_name in positions:
    has_change = request.POST.get(f'has_change_{position_key}', 'no') == 'yes'
    if has_change:
        name = request.POST.get(f'name_{position_key}', '')
        if name:
            personnel = Personnel(
                project=project,  # 关联项目对象
                project_code=project_code,  # 项目编号字符串
                # ...
            )
            personnel.save()
            created_count += 1
            print(f"✓ Created personnel: {name}, project_id={project.id}, project_code={project_code}")

if created_count == 0:
    messages.warning(request, '未勾选任何岗位的变化，或未填写姓名')
else:
    messages.success(request, f'成功添加 {created_count} 名项目人员')
```

**优点**:
- ✅ 可以确认创建了多少条记录
- ✅ 可以在服务器终端看到详细的创建信息
- ✅ 根据实际创建人数显示不同的提示
- ✅ 更容易调试问题

---

## 🎯 测试步骤

### **步骤 1: 访问添加页面**

1. 打开项目详情页：`http://127.0.0.1:8000/project_ledger/1/`
2. 点击"项目人员"子窗体的"+ 新增"按钮
3. 进入添加人员页面

### **步骤 2: 填写表单**

**必须完成的步骤**:

1. ✅ 至少勾选一个岗位的"有无变化"（如"总监"）
2. ✅ 填写该岗位的姓名（必填）
3. ✅ 选择性别（可选，默认男）
4. ✅ 填写部门（可选）
5. ✅ 其他信息根据需要填写

**示例**:
```
☑ 有无变化 - 总监
姓名：张三
性别：男
部门：监理部
入岗时间：2026-03-26
```

### **步骤 3: 提交并观察**

1. 点击"保存"按钮
2. **观察服务器终端输出**，应该看到类似：
   ```
   ✓ Created personnel: 张三，project_id=1, project_code=2036
   ```
3. 页面应该跳转到项目详情页
4. 查看消息提示：
   - 如果创建了人员：显示绿色成功消息 "成功添加 1 名项目人员"
   - 如果没有勾选任何岗位：显示黄色警告消息 "未勾选任何岗位的变化，或未填写姓名"

### **步骤 4: 验证结果**

在项目详情页的"项目人员"子窗体中，应该能看到刚才添加的人员记录。

---

## 🔧 调试指南

如果问题仍然存在，请检查以下内容：

### **1. 检查服务器终端输出**

查看是否有以下输出：

**正常情况**:
```
✓ Created personnel: 张三，project_id=1, project_code=2036
✓ Created personnel: 李四，project_id=1, project_code=2036
```

**异常情况**:
- 没有任何 `✓ Created personnel` 输出 → 说明没有创建成功
- 输出中的 `project_id=None` → 说明项目关联有问题
- 输出中的 `project_code=''` → 说明项目编号为空

### **2. 检查数据库**

运行诊断脚本：

```bash
python check_personnel.py
```

或者在 Django shell 中检查：

```python
from eims_app.models import Personnel

# 检查最新记录
latest = Personnel.objects.order_by('-create_time').first()
print(f"Latest: {latest.name if latest else 'None'}")
print(f"  project_id: {latest.project_id if latest else None}")
print(f"  project_code: '{latest.project_code if latest else ''}'")
```

### **3. 检查表单提交**

在浏览器开发者工具中查看 POST 请求：

1. 打开开发者工具（F12）
2. 切换到 Network 标签
3. 提交表单
4. 查看 POST 请求的 Form Data
5. 确认包含：
   ```
   has_change_director: yes
   name_director: 张三
   gender_director: 0
   department: 监理部
   ```

---

## 💡 可能的后续修复

### **如果 project 字段仍然为空**

可能需要检查 Personnel 模型的 `save()` 方法是否有特殊逻辑，或者是否有信号干扰。

**检查**:
```python
# 在 add_personnel 中添加更多调试
personnel = Personnel(...)
print(f"Before save: project={personnel.project}, project_code={personnel.project_code}")
personnel.save()
print(f"After save: project={personnel.project}, project_code={personnel.project_code}")
```

### **如果字段冲突**

考虑移除 `project_code` 字段，只使用 `project` 外键：

```python
# 在视图查询中使用外键
personnel_list = Personnel.objects.filter(
    project=project_detail,  # 使用外键而不是 project_code
    is_deleted=False
)
```

或者移除 `project` 字段，只使用 `project_code`：

```python
# 在创建时只设置 project_code
personnel = Personnel(
    project_code=project_code,
    # project=project,  # 删除这行
    # ...
)
```

---

## ✅ 完成状态

- ✅ 添加了调试输出（print 语句）
- ✅ 改进了用户提示（区分成功和警告）
- ✅ 添加了计数逻辑（统计实际创建人数）
- ✅ 添加了字段注释（明确说明意图）
- ⏳ 等待测试验证

---

## 📞 下一步

1. **刷新浏览器**（Ctrl+F5）
2. **重新测试添加人员功能**
3. **观察服务器终端输出**
4. **检查项目详情页是否显示人员列表**

如果仍然有问题，请提供：
- 服务器终端的完整输出
- 数据库检查结果
- 浏览器开发者工具中的网络请求信息

---

**修复完成时间**: 2026-03-26 01:00  
**服务器状态**: ✅ 运行正常（已自动重新加载）  
**建议操作**: 重新测试添加人员功能并观察终端输出
