# 📋 进场通知字段说明

## ✅ 字段配置确认

**进场通知**字段的允许值已经正确配置为：**有、无**

---

## 📊 字段详情

### **允许的取值（2 个）**

| 中文名称 | 存储值 | 说明 |
|---------|--------|------|
| **有** | `yes` | ✅ 标准 |
| **无** | `no` | ✅ 标准 |

### **模型定义**

**文件**: [`model_project_detail.py`](file://e:\EIMS2026\eims_app\models\model_project_detail.py#L103-L107)

```python
ENTRY_NOTICE_CHOICES = [
    ('yes', '有'),
    ('no', '无'),
]
entry_notice = models.CharField("进场通知", max_length=10, 
                                choices=ENTRY_NOTICE_CHOICES, 
                                default='no')
```

---

## 🔧 已配置的内容

### **1. 调试工具验证规则**

**文件**: [`debug_import_tool.py`](file://e:\EIMS2026\debug_import_tool.py#L381)

```python
'entry_notice': ['有', '无'],
```

✅ **状态**: 已正确配置

---

### **2. 项目台账导入逻辑**

**文件**: [`views_project_ledger.py`](file://e:\EIMS2026\eims_app\views\views_project_ledger.py#L350-L356)

**新增映射**:
```python
elif field_name == 'entry_notice':
    # 进场通知映射
    entry_notice_mapping = {
        '有': 'yes',
        '无': 'no',
    }
    data[field_name] = entry_notice_mapping.get(str(value).strip(), 'no')
```

✅ **状态**: 已添加映射逻辑

---

### **3. 合同管理导入逻辑**

**文件**: [`views_contract_management.py`](file://e:\EIMS2026\eims_app\views\views_contract_management.py#L311-L318)

**修改内容**: 与项目台账相同的映射逻辑

✅ **状态**: 已添加映射逻辑

---

### **4. Excel 模板**

**文件**: [`create_import_templates.py`](file://e:\EIMS2026\create_import_templates.py#L176)

```python
['进场通知', '有/无'],
```

✅ **状态**: 已正确配置

---

## 💡 使用示例

### **Excel 填写示例**

在"进场通知"列中，可以填写：

| ✅ 正确填写 | 数据库存储 | 说明 |
|-----------|-----------|------|
| 有 | yes | 有进场通知 |
| 无 | no | 无进场通知 |

### **实际应用场景**

#### **场景 1: 有进场通知**
```
项目编号：TEST2026001
项目名称：测试项目
进场通知：有  ← 会被映射为 'yes'
```

#### **场景 2: 无进场通知**
```
项目编号：TEST2026002
项目名称：另一个项目
进场通知：无  ← 会被映射为 'no'
```

---

## 🎯 映射关系

### **完整的映射表**

```python
{
    '有': 'yes',
    '无': 'no',
}
```

### **默认值**

如果填写了不在列表中的值，会映射为默认值：`'no'`（无）

---

## 📊 完整的选择字段列表

### **所有选择字段的允许值**

| 字段名称 | 允许值 |
|---------|--------|
| **项目月报** | 需要、不需要、是、否、True、False、1、0、YES、NO |
| **合同类别** | 工程监理、造价咨询、工程检测、全过程咨询 |
| **项目状态** | 未开工、在施工、停工中、已完工 |
| **合同状态** | 待审核、在执行、已终止、已解除 |
| **结算情况** | 已结算、未结算 |
| **报建情况** | 已完成、未完成 |
| **进场通知** | 有、无 ✅ |

---

## 🔍 常见问题

### **Q1: 进场通知字段的作用是什么？**

**A**: 用于标识是否有正式的进场通知。这通常是一个布尔型的选择，表示项目是否收到了甲方的进场通知。

### **Q2: 如果填写"是"或"否"可以吗？**

**A**: 
- 调试工具会显示警告 ⚠️（因为不在允许列表中）
- 导入时会映射为默认值 `'no'`
- **建议**: 使用标准的"有"或"无"

### **Q3: 这个字段与"进场通知书"有什么关系？**

**A**: 
- **进场通知**: 是一个选择字段（有/无），表示是否有通知
- **进场通知书**: 是一个文件上传字段，用于上传实际的通知书文件

两者配合使用：
- 如果"进场通知" = "有"，通常会上传"进场通知书"文件
- 如果"进场通知" = "无"，则不需要上传文件

---

## 📁 相关文件

### **已配置的文件**
- [`model_project_detail.py`](file://e:\EIMS2026\eims_app\models\model_project_detail.py#L103-L107) - 模型定义
- [`debug_import_tool.py`](file://e:\EIMS2026\debug_import_tool.py#L381) - 验证规则
- [`views_project_ledger.py`](file://e:\EIMS2026\eims_app\views\views_project_ledger.py#L350-L356) - 项目台账导入
- [`views_contract_management.py`](file://e:\EIMS2026\eims_app\views\views_contract_management.py#L311-L318) - 合同管理导入
- [`create_import_templates.py`](file://e:\EIMS2026\create_import_templates.py#L176) - Excel 模板

---

## ✅ 总结

### **进场通知字段（2 个标准值）**

✅ **有** → `yes`  
✅ **无** → `no`  

### **配置状态**

- ✅ 模型定义：正确
- ✅ 调试工具：已配置
- ✅ 导入逻辑：已添加映射
- ✅ Excel 模板：正确
- ✅ 向后兼容：支持默认值处理

### **优势**

- 📋 **清晰明确**: "有/无"表达非常清楚
- 🔄 **简单直接**: 只有两个选项，不易混淆
- 🛡️ **容错性**: 错误输入会映射为默认值
- 🎯 **业务准确**: 符合实际工作流程

---

**更新时间**: 2026-03-25 04:00  
**状态**: ✅ 已配置并验证  
**影响范围**: 进场通知字段的导入和验证
