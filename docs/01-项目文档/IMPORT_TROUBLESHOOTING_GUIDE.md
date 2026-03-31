# 导入问题排查指南

## 🔍 如何诊断导入问题

### 方法一：使用调试工具（推荐）

我已经创建了一个专门的调试工具来帮助你诊断导入问题。

#### 访问步骤：

1. **启动服务器**
   ```bash
   python manage.py runserver
   ```

2. **打开浏览器访问**
   ```
   http://localhost:8000/debug_import/
   ```

3. **上传有问题的 Excel 文件**
   - 选择之前导入失败的 Excel 文件
   - 点击"开始调试"按钮

4. **查看详细分析报告**
   
   调试工具会显示：
   - ✅ Excel 基本信息（文件名、行数、列数等）
   - ✅ 表头字段匹配情况（哪些字段匹配成功，哪些失败）
   - ✅ 数据行预览（前 5 行的数据处理情况）
   - ✅ Model 字段验证（检查数据库表结构）
   - ✅ 智能建议（针对发现的问题给出解决建议）

---

### 方法二：查看错误消息

当导入失败时，系统会显示错误消息。注意查看：

#### 1. **整体错误**
```
导入失败：[具体错误信息]
```

#### 2. **行级错误**
```
第 X 行：[具体错误信息]
```

#### 3. **必填字段缺失**
```
第 X 行：缺少必填字段
```

---

### 方法三：手动检查 Excel 文件

#### 检查清单：

1. **文件格式**
   - ✅ 必须是 `.xlsx` 或 `.xls` 格式
   - ✅ 第一个工作表（Sheet1）
   - ✅ 第一行是表头（字段名）
   - ✅ 从第二行开始是数据

2. **表头名称**（必须完全匹配）
   
   **项目台账必需字段：**
   - 项目编号
   - 合同编号
   - 项目名称
   - 合同类别
   - 项目状态
   - 合同状态
   - 结算情况
   - 合同甲方
   - 合同乙方
   - 签订日期
   - 合同总价
   - ...（共 29 个字段）
   
   **合同管理必需字段：**
   - 合同类别
   - 合同编号
   - 项目名称
   - 合同状态
   - 结算情况
   - 合同甲方
   - 合同乙方
   - 签订日期
   - 合同总价
   - ...（共 20 个字段）

3. **必填字段**
   - 项目编号 ⚠️
   - 合同编号 ⚠️
   - 项目名称 ⚠️
   - 合同甲方 ⚠️
   - 合同乙方 ⚠️
   
   这些字段不能为空！

4. **数据格式**
   - 📅 日期字段：`2024-01-15` 或 Excel 日期格式
   - 💰 金额字段：数字（如 `100000.00`），不要带 `¥` 符号
   - 📝 文本字段：不能有异常字符

---

## 🛠️ 常见错误及解决方案

### 错误 1：字段不匹配

**症状：**
```
❌ 未匹配的表头：项目名、甲方、乙方
```

**原因：**
Excel 表头名称与系统定义不一致

**解决方法：**
- 检查表头是否有错别字
- 确保使用标准字段名（参考上面的字段列表）
- 删除多余的列

---

### 错误 2：缺少必填字段

**症状：**
```
第 3 行：缺少必填字段
```

**原因：**
必填字段为空

**解决方法：**
- 检查该行的必填字段是否有值
- 如果某些字段确实没有值，可以填 `-` 或留空（但必填字段必须有值）

---

### 错误 3：日期格式错误

**症状：**
```
第 5 行：日期格式错误：time data '2024/1/15' does not match format '%Y-%m-%d'
```

**原因：**
日期格式不符合要求

**解决方法：**
- 将日期改为 `YYYY-MM-DD` 格式（如 `2024-01-15`）
- 或在 Excel 中设置为标准日期格式

---

### 错误 4：金额格式错误

**症状：**
```
第 8 行：金额格式错误：could not convert string to float: '¥100,000'
```

**原因：**
金额包含货币符号或千位分隔符

**解决方法：**
- 移除 `¥`、`$` 等货币符号
- 保留小数点（如 `100000.00`）
- 可以使用千位分隔符（系统会自动处理）

---

### 错误 5：数据库字段不存在

**症状：**
```
OperationalError: no such column: eims_app_projectdetail.xxx
```

**原因：**
数据库表结构与代码不匹配

**解决方法：**
1. 检查数据库是否已完成迁移
2. 运行调试工具查看数据库实际列
3. 如有必要，重新执行数据库迁移

---

## 📋 完整的字段映射表

### 项目台账导入字段映射

| Excel 表头 | 数据库字段 | 类型 | 必填 | 说明 |
|-----------|-----------|------|------|------|
| 项目编号 | project_code | VARCHAR(50) | ✅ | 唯一标识 |
| 合同编号 | contract_code | VARCHAR(50) | ✅ | 唯一标识 |
| 项目名称 | project_name | VARCHAR(255) | ✅ | - |
| 合同类别 | contract_category | VARCHAR(20) | - | engineering, procurement, etc. |
| 项目状态 | project_status | VARCHAR(20) | - | planning, in_progress, completed |
| 合同状态 | contract_status | VARCHAR(20) | - | draft, active, archived |
| 结算情况 | settlement_status | VARCHAR(20) | - | unpaid, partial, fully_paid |
| 合同甲方 | contract_party_a | VARCHAR(255) | ✅ | - |
| 合同乙方 | contract_party_b | VARCHAR(255) | ✅ | - |
| 签订日期 | signing_date | DATE | - | YYYY-MM-DD |
| 合同总价 | contract_amount | DECIMAL(12,2) | - | 数字 |
| 付款约定 | payment_agreement | TEXT | - | - |
| 项目规模 | project_scale | VARCHAR(255) | - | - |
| 项目总投资 | project_investment | DECIMAL(12,2) | - | 数字 |
| 项目地址 | project_address | VARCHAR(255) | - | - |
| 服务周期 | service_period | VARCHAR(100) | - | - |
| 服务到期日期 | service_deadline | DATE | - | YYYY-MM-DD |
| 延期约定 | extension_agreement | TEXT | - | - |
| 实际延期情况 | actual_extension_status | TEXT | - | - |
| 施工许可证状态 | construction_permit_status | VARCHAR(50) | - | - |
| 进场通知 | entry_notice | TEXT | - | - |
| 进场时间 | entry_time | DATE | - | YYYY-MM-DD |
| 实际开工日期 | actual_start_date | DATE | - | YYYY-MM-DD |
| 预计竣工日期 | estimated_completion_date | DATE | - | YYYY-MM-DD |
| 项目总监 | project_director | VARCHAR(100) | - | - |
| 现场负责人 | project_manager | VARCHAR(100) | - | - |
| 联系电话 | contact_phone | VARCHAR(50) | - | - |
| 备注 | remark | TEXT | - | - |
| 项目月报 | monthly_report_required | BOOLEAN | - | 是/否 |

---

### 合同管理导入字段映射

| Excel 表头 | 数据库字段 | 类型 | 必填 | 说明 |
|-----------|-----------|------|------|------|
| 合同类别 | contract_category | VARCHAR(20) | ✅ | - |
| 合同编号 | contract_code | VARCHAR(50) | ✅ | 唯一标识 |
| 项目名称 | project_name | VARCHAR(255) | ✅ | - |
| 合同状态 | contract_status | VARCHAR(20) | ✅ | - |
| 结算情况 | settlement_status | VARCHAR(20) | ✅ | - |
| 合同甲方 | contract_party_a | VARCHAR(255) | ✅ | - |
| 合同乙方 | contract_party_b | VARCHAR(255) | ✅ | - |
| 签订日期 | signing_date | DATE | - | YYYY-MM-DD |
| 合同总价 | contract_amount | DECIMAL(12,2) | - | 数字 |
| 付款约定 | payment_agreement | TEXT | - | - |
| 项目规模 | project_scale | VARCHAR(255) | - | - |
| 项目总投资 | project_investment | DECIMAL(12,2) | - | 数字 |
| 项目地址 | project_address | VARCHAR(255) | - | - |
| 约定人员配备 | agreed_staffing | TEXT | - | - |
| 服务周期 | service_period | VARCHAR(100) | - | - |
| 服务到期日期 | service_deadline | DATE | - | YYYY-MM-DD |
| 延期约定 | extension_agreement | TEXT | - | - |
| 计划开工日期 | planned_start_date | DATE | - | YYYY-MM-DD |
| 预计竣工日期 | estimated_completion_date | DATE | - | YYYY-MM-DD |
| 备注 | remark | TEXT | - | - |

---

## 🎯 快速排查流程

```
1. 访问调试工具
   ↓
2. 上传 Excel 文件
   ↓
3. 查看分析报告
   ↓
4. 根据报告修正 Excel
   - 修改表头名称
   - 补充必填字段
   - 修正数据格式
   ↓
5. 重新导入
   ↓
6. 成功！✅
```

---

## 💡 最佳实践

### 1. **使用模板**
- 先导出系统中的数据作为模板
- 在模板基础上修改或添加数据
- 这样可以确保格式完全正确

### 2. **小批量测试**
- 首次导入时，先导入 1-2 条记录测试
- 确认无误后再批量导入

### 3. **数据验证**
- 导入前在 Excel 中使用数据验证功能
- 设置下拉列表、日期范围等限制
- 减少格式错误

### 4. **备份数据**
- 导入前备份数据库
- 防止误操作导致数据丢失

---

## 🆘 需要帮助？

如果使用调试工具后仍然无法解决问题，请提供：

1. **错误截图** - 完整的错误消息
2. **Excel 文件** - 脱敏后的测试文件
3. **操作步骤** - 你是如何操作的

这样可以更快地定位和解决问题。

---

**调试工具位置:** `e:\EIMS2026\debug_import_tool.py`  
**访问地址:** `http://localhost:8000/debug_import/`  
**创建时间:** 2026-03-21
