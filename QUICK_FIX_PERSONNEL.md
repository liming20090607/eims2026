# 快速修复姓名下拉列表数据不全问题

## 🎯 问题原因

**Personnel 表（人员花名册）中只有 11 条记录，其中 5 条是测试数据**

当前数据：
- 总记录：37 条
- 未删除：11 条
- 测试数据：5 条（姓名：4, C, E, G, J）
- 真实人员：6 人（唐昌罗、唐鹏、张中立、秦养付、罗龙辉、谢荣明）

---

## ⚡ 快速修复步骤（3 步完成）

### 步骤 1：清理测试数据（1 分钟）

运行清理脚本：
```bash
python cleanup_test_data.py
```

**操作**：
- 对每个测试数据输入 `y` 确认删除
- 删除 5 条测试记录

**预期输出**：
```
✓ 已删除 5 条记录
剩余人员：6 人
```

---

### 步骤 2：从 Employee 导入（1 分钟）

运行导入脚本：
```bash
python import_employees_to_personnel.py
```

**操作**：
- 自动从 Employee 表导入所有在职员工
- 跳过已在 Personnel 表中的人员

**预期输出**：
```
找到 X 名在职员工
✓ 导入：张三 -> RY001
✓ 导入：李四 -> RY002
...
新增：X 人
```

---

### 步骤 3：验证结果（1 分钟）

运行验证脚本：
```bash
python verify_personnel_dropdown.py
```

**预期输出**：
```
下拉列表将显示 X 人:
  1. 张三     (项目 A, 项目 B)
  2. 李四     (项目 C)
  3. 王五     (未分配项目)
...
总计：X 人
```

---

## 🌐 手动添加人员（可选）

如果还有遗漏的人员，通过界面手动添加：

### 访问人员花名册
```
http://127.0.0.1:8000/personnel/
```

### 添加人员步骤
1. 点击"添加人员"按钮
2. 填写信息：
   - 人员编号：`RY2026XXX`
   - 姓名：完整姓名（至少 2 个汉字）
   - 性别：男/女
   - 手机号：11 位手机号
   - 部门：如"工程部"
   - 岗位：如"技术员"
3. 点击"保存"

---

## ✅ 验证修复效果

### 方法 1：访问项目台账
```
http://127.0.0.1:8000/project_ledger/
```

1. 点击任意项目的"查看详情"
2. 点击"添加项目人员"
3. 点击任意岗位的"姓名"下拉框
4. **应该显示所有人员**

### 方法 2：直接测试
打开浏览器控制台（F12），输入：
```javascript
// 检查下拉列表人数
const options = document.querySelectorAll('.select2-results__option');
console.log(`下拉列表人数：${options.length}`);
```

---

## 📊 数据维护建议

### 日常流程
1. **新员工入职**
   - 先创建 Employee 记录（入职登记）
   - 再创建 Personnel 记录（分配到项目）

2. **员工调动**
   - 更新 Personnel 记录的项目字段
   - 创建 PersonnelAllocation 记录

3. **员工离职**
   - 标记 Employee 为已删除
   - 标记 Personnel 为已删除

### 定期检查
```bash
# 每月运行一次验证
python verify_personnel_dropdown.py
```

---

## 🔧 脚本说明

### cleanup_test_data.py
- **功能**：删除单字符测试数据
- **安全**：需要手动确认
- **影响**：删除 5 条测试记录

### import_employees_to_personnel.py
- **功能**：从 Employee 导入到 Personnel
- **智能**：自动跳过已存在人员
- **安全**：不会重复导入

### verify_personnel_dropdown.py
- **功能**：验证下拉列表数据
- **检查**：数据质量、完整性
- **输出**：详细的人员列表

---

## 📝 完整文档

- 详细指南：[`PERSONNEL_DATA_GUIDE.md`](file://e:\EIMS2026\PERSONNEL_DATA_GUIDE.md)
- 模型对比：[`docs/EMPLOYEE_VS_PERSONNEL_COMPARISON.md`](file://e:\EIMS2026\docs\EMPLOYEE_VS_PERSONNEL_COMPARISON.md)

---

## 🎯 预期结果

修复后：
- ✅ 下拉列表包含所有在职员工
- ✅ 无测试数据干扰
- ✅ 姓名按拼音排序
- ✅ 自动去重（一人多项目只出现一次）

---

**创建时间**: 2026-03-28  
**适用系统**: EIMS2026
