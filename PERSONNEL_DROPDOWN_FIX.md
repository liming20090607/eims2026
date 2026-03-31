# 人员姓名下拉列表数据源修复

## ✅ 问题描述

在项目台账的"添加项目人员"页面（`add_personnel.html`）中，所有岗位（总监、总代、土建专监等）的姓名下拉列表选项为空。

**原因**：原代码从 `Employee` 表（员工基本信息表）获取姓名，但该表可能没有数据或数据不完整。

**需求**：姓名下拉列表的选项应该来自"人员花名册"（`Personnel` 表）中已录入的人员姓名。

## 🔧 修复内容

### 修改文件
**文件路径**: `e:\EIMS2026\eims_app\views\views_project.py`

**函数**: `add_personnel(request, pk)`

**修改位置**: 第 554-562 行

### 修改前
```python
# GET 请求时，获取人员花名册中的所有姓名（按姓名升序排列）
employees = Employee.objects.order_by('name')  # 按姓名升序排列
employee_names = [emp.name for emp in employees]
```

**问题**：
- 从 `Employee` 表获取数据
- `Employee` 表可能为空或没有相关人员
- 导致下拉列表无选项

### 修改后
```python
# GET 请求时，获取人员花名册中的所有姓名（按姓名升序排列，去重）
# 从 Personnel 表（人员花名册）获取姓名，而不是 Employee 表
personnel_names = Personnel.objects.filter(
    is_deleted=False  # 只获取未删除的记录
).order_by('name').values_list('name', flat=True).distinct()

# 转换为列表（去重后的姓名列表）
employee_names = list(personnel_names)
```

**改进**：
- ✅ 从 `Personnel` 表（人员花名册）获取姓名
- ✅ 只获取未删除的记录（`is_deleted=False`）
- ✅ 按姓名升序排列
- ✅ 使用 `distinct()` 去重，避免重复姓名
- ✅ 直接获取姓名字段，无需遍历对象

## 📊 数据模型说明

### Employee 表（员工基本信息）
- 存储员工的基本信息
- 字段：员工编号、姓名、性别、身份证号等
- **问题**：可能未录入或数据不完整

### Personnel 表（人员花名册）
- 存储已分配到项目的人员信息
- 字段：人员编号、姓名、性别、岗位、部门等
- **优势**：包含所有已在人员花名册中登记的人员
- 关联：通过外键关联到 `Employee`，但也可以独立存在

## 🎯 影响范围

### 影响的页面
**项目台账详情页** → **添加项目人员**

URL: `/project_ledger/<pk>/add-personnel/`

### 影响的岗位下拉列表
所有 8 个岗位的姓名选择框：
1. ✅ 总监 (`name_director`)
2. ✅ 总代 (`name_deputy_director`)
3. ✅ 土建专监 (`name_civil_supervisor`)
4. ✅ 水电专监 (`name_electrical_supervisor`)
5. ✅ 监理员 (`name_supervisor`)
6. ✅ 资料员 (`name_document_controller`)
7. ✅ 见证员 (`name_witness`)
8. ✅ 安全员 (`name_safety_officer`)

### 模板文件
`e:\EIMS2026\eims_app\templates\project_ledger\add_personnel.html`

模板中使用了 8 次 `{% for name in employee_names %}` 循环，现在都能正确显示人员花名册中的姓名。

## 🧪 测试验证

### 测试步骤
1. **访问人员花名册页面**
   - URL: `/personnel/`
   - 确认花名册中已有人员记录
   
2. **访问项目台账详情页**
   - URL: `/project_ledger/<pk>/`
   - 点击"添加项目人员"按钮
   
3. **检查姓名下拉列表**
   - 勾选任意岗位的"有无变化"复选框
   - 点击"姓名"下拉框
   - 应该能看到人员花名册中的所有人员姓名
   
4. **验证姓名来源**
   - 下拉列表中的姓名应该与人员花名册中的姓名一致
   - 按姓名升序排列
   - 重复姓名只显示一次

### 预期结果
- ✅ 下拉列表显示人员花名册中的所有姓名
- ✅ 姓名按拼音/笔画升序排列
- ✅ 重复姓名自动去重
- ✅ 已删除的人员不显示
- ✅ 可以选择姓名并保存

## 📈 修复效果

### 修复前
```
姓名下拉列表：
┌─────────────────────┐
│ 请选择人员          │
└─────────────────────┘
（空列表，无选项）
```

### 修复后
```
姓名下拉列表：
┌─────────────────────┐
│ 请选择人员          │
├─────────────────────┤
│ 张三                │
│ 李四                │
│ 王五                │
│ ...                 │
└─────────────────────┘
（显示人员花名册中的所有姓名）
```

## 🔍 技术细节

### 查询优化
```python
# 优化前（低效）
employees = Employee.objects.order_by('name')
employee_names = [emp.name for emp in employees]
# 问题：获取整个对象，然后提取姓名，效率低

# 优化后（高效）
personnel_names = Personnel.objects.filter(
    is_deleted=False
).order_by('name').values_list('name', flat=True).distinct()
employee_names = list(personnel_names)
# 优势：直接获取姓名字段，使用数据库去重，效率高
```

### SQL 对比
```sql
-- 优化前
SELECT * FROM employee ORDER BY name;
-- 然后在 Python 中提取姓名

-- 优化后
SELECT DISTINCT name FROM personnel 
WHERE is_deleted = FALSE 
ORDER BY name;
-- 直接在数据库层面去重和排序
```

## 📝 注意事项

### 1. 数据一致性
- 确保人员花名册中已录入相关人员
- 如果人员花名册也为空，需要先添加人员

### 2. 姓名去重
- 使用 `distinct()` 自动去重
- 如果花名册中有多个同名人员，只显示一次

### 3. 删除标记
- 使用 `is_deleted=False` 过滤
- 已删除的人员不会出现在下拉列表中

### 4. 性能考虑
- 使用 `values_list('name', flat=True)` 直接获取姓名
- 避免获取不必要的字段
- 数据库层面去重和排序

##  相关知识

### Django ORM 查询方法

#### values_list(flat=True)
```python
# 获取单个字段的列表
Personnel.objects.values_list('name', flat=True)
# 返回：['张三', '李四', '王五']
```

#### distinct()
```python
# 去重查询
Personnel.objects.values_list('name', flat=True).distinct()
# 返回：['张三', '李四', '王五']（无重复）
```

#### filter(is_deleted=False)
```python
# 只获取未删除的记录
Personnel.objects.filter(is_deleted=False)
# 排除已软删除的数据
```

## ✅ 修复完成检查清单

- [x] 修改视图函数 `add_personnel`
- [x] 从 `Personnel` 表获取姓名
- [x] 添加 `is_deleted=False` 过滤
- [x] 使用 `distinct()` 去重
- [x] 使用 `values_list` 优化查询
- [x] 服务器自动重新加载
- [x] 代码无语法错误
- [x] 系统检查无问题

## 🚀 下一步操作

1. **刷新页面**
   - 访问 `/project_ledger/<pk>/add-personnel/`
   - 按 `Ctrl+F5` 强制刷新
   
2. **测试下拉列表**
   - 勾选任意岗位的"有无变化"
   - 点击姓名下拉框
   - 验证是否显示人员花名册中的姓名

3. **验证功能**
   - 选择一个姓名
   - 填写其他信息
   - 提交表单
   - 确认保存成功

---

**修复时间**: 2026-03-28 21:36  
**修复人员**: AI Assistant  
**测试状态**: ⏳ 待用户验证  
**部署状态**: ✅ 已部署（服务器已自动重载）
