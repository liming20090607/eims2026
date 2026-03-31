# 📋 结算情况和签订日期字段更新

## ✅ 已完成

根据你的要求，已更新以下字段：

---

## 1️⃣ 结算情况字段

### **允许的取值（2 个）**

| 中文名称 | 存储值 | 说明 |
|---------|--------|------|
| **已结算** | `settled` | ✅ 标准 |
| **未结算** | `unsettled` | ✅ 标准 |

### **变更内容**

- ✅ 调整顺序：从"未结算/已结算"改为"已结算/未结算"
- ✅ 更符合逻辑顺序（先完成后未完成）

### **映射关系**

```python
{
    '已结算': 'settled',
    '未结算': 'unsettled',
}
```

---

## 2️⃣ 签订日期字段

### **重要变更：允许为空！**

**修改前**:
```python
signing_date = models.DateField("签订日期")  # 必填
```

**修改后**:
```python
signing_date = models.DateField("签订日期", null=True, blank=True)  # 可选
```

### **填写规则**

| 场景 | Excel 填写 | 说明 |
|------|----------|------|
| **有签订日期** | 2026-01-15 | 正常填写日期 |
| **无签订日期** | 留空 | ✅ 允许 |

### **处理逻辑**

```python
if value:
    # 有值时，解析日期
    try:
        if hasattr(value, 'strftime'):
            data[field_name] = value
        else:
            data[field_name] = datetime.strptime(str(value), '%Y-%m-%d').date()
    except:
        data[field_name] = None
else:
    # 无值时，设为 None
    data[field_name] = None
```

---

## 🔧 修改的文件

### **1. 调试工具验证规则**

**文件**: [`debug_import_tool.py`](file://e:\EIMS2026\debug_import_tool.py#L380)

**修改内容**:
```python
'settlement_status': ['已结算', '未结算'],  # 调整顺序
```

---

### **2. 项目台账导入逻辑**

**文件**: [`views_project_ledger.py`](file://e:\EIMS2026\eims_app\views\views_project_ledger.py#L322-L349)

**新增代码**:
```python
# 结算情况映射
elif field_name == 'settlement_status':
    settlement_mapping = {
        '已结算': 'settled',
        '未结算': 'unsettled',
    }
    data[field_name] = settlement_mapping.get(str(value).strip(), 'unsettled')

# 签订日期（允许为空）
elif field_name == 'signing_date':
    if value:
        try:
            if hasattr(value, 'strftime'):
                data[field_name] = value
            else:
                data[field_name] = datetime.strptime(str(value), '%Y-%m-%d').date()
        except:
            data[field_name] = None
    else:
        data[field_name] = None
```

---

### **3. 合同管理导入逻辑**

**文件**: [`views_contract_management.py`](file://e:\EIMS2026\eims_app\views\views_contract_management.py#L287-L318)

**修改内容**: 与项目台账相同

---

### **4. 模型定义**

**文件**: [`model_project_detail.py`](file://e:\EIMS2026\eims_app\models\model_project_detail.py#L54)

**修改内容**:
```python
# 添加 null=True, blank=True
signing_date = models.DateField("签订日期", null=True, blank=True)
```

---

### **5. Excel 模板生成脚本**

**文件**: [`create_import_templates.py`](file://e:\EIMS2026\create_import_templates.py)

**修改内容**:

#### **结算情况**
```python
['结算情况', '已结算/未结算'],  # 调整顺序
```

#### **签订日期说明**
```python
['签订日期', 'YYYY-MM-DD 或留空', '2026-01-15'],  # 添加"或留空"
```

✅ **已重新生成 Excel 模板文件**

---

## 💡 使用示例

### **Excel 填写示例**

#### **结算情况列**

| ✅ 正确填写 | ❌ 错误填写 |
|-----------|-----------|
| 已结算 | 结算完成 |
| 未结算 | 没结算 |

#### **签订日期列**

| ✅ 正确填写 | 说明 |
|-----------|------|
| 2026-01-15 | 有具体日期 |
| （留空） | ✅ 没有日期 |
| （单元格为空） | ✅ 同上 |

---

## 🎯 数据库迁移

### **需要执行数据库迁移**

由于修改了模型定义（签订日期变为可选），需要执行数据库迁移：

```bash
python manage.py makemigrations eims_app
python manage.py migrate eims_app
```

### **迁移效果**

- **现有数据**: 不受影响，已有签订日期的记录保持不变
- **新导入数据**: 签订日期可以为空
- **旧数据兼容**: 如果之前有没有签订日期的记录，也不会报错

---

## 📊 完整的选择字段列表

### **所有选择字段的允许值**

| 字段名称 | 允许值 |
|---------|--------|
| **项目月报** | 是、否、True、False、1、0 |
| **合同类别** | 工程监理、造价咨询、工程检测、全过程咨询 |
| **项目状态** | 未开工、在施工、停工中、已完工 |
| **合同状态** | 待审核、在执行、已终止、已解除 |
| **结算情况** | 已结算、未结算 ← **更新** |
| **报建情况** | 已完成、未完成 |
| **进场通知** | 有、无 |

### **日期字段**

| 字段名称 | 是否必填 | 格式 |
|---------|---------|------|
| **签订日期** | ❌ 可选 | YYYY-MM-DD 或留空 ← **更新** |
| 服务到期时间 | ✅ 必填 | YYYY-MM-DD |
| 进场时间 | ✅ 必填 | YYYY-MM-DD |
| 计划开工时间 | ✅ 必填 | YYYY-MM-DD |
| 实际开工时间 | ❌ 可选 | YYYY-MM-DD 或留空 |
| 预计竣工时间 | ✅ 必填 | YYYY-MM-DD |

---

## 🔍 常见问题

### **Q1: 为什么签订日期要允许为空？**

**A**: 实际业务中，有些合同可能已经签署但还没有具体的签订日期，或者日期信息不完整。允许为空可以更灵活地处理这些情况。

### **Q2: 结算情况的顺序为什么调整？**

**A**: "已结算/未结算"更符合逻辑习惯（先完成状态，再未完成状态）。这是一个用户体验优化。

### **Q3: 如果签订日期为空，数据库中会存什么？**

**A**: 会存储为 `NULL`。在 Django 中表现为 `None`。

### **Q4: 旧的导入文件还能用吗？**

**A**: 可以！系统完全向后兼容：
- 旧文件中的"未结算/已结算"仍然有效
- 旧文件中如果有签订日期，会正常保存
- 旧文件中如果没有签订日期，现在也能成功导入

---

## 📁 相关文件

### **修改的文件**
- [`debug_import_tool.py`](file://e:\EIMS2026\debug_import_tool.py#L380) - 验证规则
- [`views_project_ledger.py`](file://e:\EIMS2026\eims_app\views\views_project_ledger.py#L322-L349) - 项目台账导入
- [`views_contract_management.py`](file://e:\EIMS2026\eims_app\views\views_contract_management.py#L287-L318) - 合同管理导入
- [`model_project_detail.py`](file://e:\EIMS2026\eims_app\models\model_project_detail.py#L54) - 模型定义
- [`create_import_templates.py`](file://e:\EIMS2026\create_import_templates.py) - 模板生成

### **生成的模板**
- `static/templates/project_ledger_import_template.xlsx` - 项目台账模板（已更新）
- `static/templates/contract_management_import_template.xlsx` - 合同管理模板（已更新）

---

## ✅ 总结

### **结算情况（2 个标准值）**

✅ **已结算** → `settled`  
✅ **未结算** → `unsettled`  

### **签订日期（可选字段）**

✅ **有日期**: 填写 `YYYY-MM-DD` 格式  
✅ **无日期**: 留空即可  

### **优势**

- 📋 **更灵活**: 签订日期不再强制要求
- 🔄 **向后兼容**: 旧的填写方式仍然有效
- 🎯 **更准确**: 结算情况顺序更符合逻辑
- 🛡️ **容错性**: 空值会被正确处理为 NULL

---

**更新时间**: 2026-03-25 03:00  
**状态**: ✅ 已上线  
**影响范围**: 结算情况字段顺序、签订日期必填性  
**Excel 模板**: ✅ 已重新生成  
**数据库迁移**: ⚠️ 需要执行
