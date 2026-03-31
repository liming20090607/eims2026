# 导入字段映射问题修复报告

## 📋 问题描述

用户在导入数据时提示"格式有误"，无法成功导入 Excel 文件。

## 🔍 问题原因

经过检查，发现字段映射存在以下问题：

### **1. 字段映射错误（已修复）**

| Excel 字段 | 原映射 | 正确映射 | 说明 |
|-----------|--------|----------|------|
| 施工许可证 | `construction_permit_status` ❌ | `construction_permit` ✅ | 应为文件上传字段 |
| 进场通知书 | `entry_notice` ❌ | `entry_notice_document` ✅ | 应为文件上传字段 |

### **2. 数据库字段说明**

数据库中存在两个易混淆的字段：

#### **进场通知相关**
- `entry_notice` (CharField) - "进场通知" - 选择字段（有/无）
- `entry_notice_document` (FileField) - "进场通知书" - 文件上传字段

#### **施工许可证相关**
- `construction_permit_status` (CharField) - "报建情况" - 选择字段（已完成/未完成）
- `construction_permit` (FileField) - "施工许可证" - 文件上传字段

## ✅ 解决方案

### **修改的文件**

1. **eims_app/views/views_project_ledger.py**
   - 修正"施工许可证"映射：`construction_permit_status` → `construction_permit`
   - 修正"进场通知书"映射：`entry_notice` → `entry_notice_document`

2. **eims_app/views/views_contract_management.py**
   - 同步修正上述两个字段的映射

### **完整的 36 字段映射**

```python
field_mapping = {
    '项目月报': 'monthly_report_required',
    '合同类别': 'contract_category',
    '项目编号': 'project_code',
    '合同编号': 'contract_code',
    '项目名称': 'project_name',
    '项目状态': 'project_status',
    '合同状态': 'contract_status',
    '结算情况': 'settlement_status',
    '合同甲方': 'contract_party_a',
    '合同乙方': 'contract_party_b',
    '签订日期': 'signing_date',
    '合同文本': 'contract_text',
    '合同总价（元）': 'contract_amount',
    '付款约定': 'payment_agreement',
    '累计回款': 'cumulative_payment',
    '合同余款': 'contract_balance',
    '项目规模': 'project_scale',
    '项目总投资（万元）': 'project_investment',
    '项目地址': 'project_address',
    '约定人员配备': 'agreed_staffing',
    '服务周期': 'service_period',
    '服务到期时间': 'service_deadline',
    '延期约定': 'extension_agreement',
    '实际延期情况': 'actual_extension_status',
    '报建情况': 'construction_permit_status',
    '施工许可证': 'construction_permit',          # ✅ 已修正
    '进场通知': 'entry_notice',
    '进场通知书': 'entry_notice_document',       # ✅ 已修正
    '进场时间': 'entry_time',
    '计划开工时间': 'planned_start_date',
    '实际开工时间': 'actual_start_date',
    '预计竣工时间': 'estimated_completion_date',
    '项目总监': 'project_director',
    '现场负责人': 'project_manager',
    '联系电话': 'contact_phone',
    '备注': 'remark',
}
```

## 🧪 验证结果

运行测试脚本验证：

```bash
$ python test_import_mapping.py

=== 字段映射验证 ===
✅ 所有 36 个字段都已正确映射！

=== 数据库字段验证 ===
✅ 所有映射的数据库字段都有效！
```

## 📝 使用方法

### **方法 1：直接使用调试工具**

1. 访问调试工具：http://localhost:8000/debug_import/
2. 上传你的 Excel 文件
3. 查看详细错误信息

### **方法 2：直接导入**

1. 访问项目台账导入页面：http://localhost:8000/project_ledger/import/
2. 上传 Excel 文件
3. 系统会自动处理并显示导入结果

### **方法 3：使用测试文件**

我已创建了一个测试 Excel 文件：
- 文件位置：`E:\EIMS2026\test_import.xlsx`
- 包含完整的 36 个字段和测试数据
- 可以用此文件验证导入功能是否正常

## ⚠️ 注意事项

### **必填字段**

以下字段为必填，不能为空：
- 项目编号 (`project_code`)
- 合同编号 (`contract_code`)
- 项目名称 (`project_name`)
- 合同甲方 (`contract_party_a`)
- 合同乙方 (`contract_party_b`)

### **字段格式要求**

1. **日期字段**（支持自动识别）
   - 签订日期、服务到期时间、进场时间
   - 计划开工时间、实际开工时间、预计竣工时间
   - 格式：Excel 日期格式或 `YYYY-MM-DD` 文本

2. **金额字段**（支持自动转换）
   - 合同总价（元）、累计回款、合同余款、项目总投资（万元）
   - 可以是数字或带千分位的文本（如 `1,000,000.00`）

3. **布尔字段**
   - 项目月报：支持 `是/否`、`True/False`、`1/0`、`YES/NO`

4. **选择字段**
   - 合同类别：工程监理、造价咨询、检测、全过程咨询
   - 项目状态：未开工、在施工、已完工、在停工
   - 合同状态：待审核、在执行、已终止、已解除
   - 结算情况：未结算、已结算
   - 报建情况：已完成、未完成
   - 进场通知：有、无

## 🎯 后续建议

如果导入仍然失败，请：

1. **使用调试工具检查**
   - 访问 http://localhost:8000/debug_import/
   - 上传 Excel 文件查看具体错误

2. **检查 Excel 格式**
   - 确保第一行是表头（中文列名）
   - 从第二行开始是数据
   - 不要有合并单元格

3. **查看错误提示**
   - 导入页面会显示具体的错误行数和原因
   - 根据错误提示修改 Excel 文件

## 📊 相关文件

- 调试工具：`debug_import_tool.py`
- 测试脚本：`test_import_mapping.py`
- 测试数据：`test_import.xlsx`
- 详细指南：`IMPORT_TROUBLESHOOTING_GUIDE.md`
- 快速帮助：`import_quick_help.html`

---

**修复完成时间**: 2026-03-21  
**状态**: ✅ 已修复并验证
