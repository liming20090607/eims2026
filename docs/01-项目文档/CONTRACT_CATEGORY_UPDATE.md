# 📋 合同类别字段映射说明

## ✅ 已完成

### **支持的合同类别取值**

现在系统支持以下**6 种**合同类别的写法（向后兼容）：

| 中文名称 | 存储值 | 说明 |
|---------|--------|------|
| **工程监理** | `engineering_supervision` | 标准写法 ✅ |
| **工程造价** | `cost_consulting` | 新增支持 ✅ |
| **造价咨询** | `cost_consulting` | 原有写法 ✅ |
| **工程检测** | `testing` | 新增支持 ✅ |
| **检测** | `testing` | 原有写法 ✅ |
| **全过程咨询** | `whole_process_consulting` | 标准写法 ✅ |

---

## 🔧 修改内容

### **1. 调试工具 - 验证规则更新**

**文件**: [`debug_import_tool.py`](file://e:\EIMS2026\debug_import_tool.py#L376)

**修改前**:
```python
'contract_category': ['工程监理', '造价咨询', '检测', '全过程咨询'],
```

**修改后**:
```python
'contract_category': ['工程监理', '工程造价', '工程检测', '造价咨询', '检测', '全过程咨询'],
```

**效果**: 调试工具现在接受所有 6 种写法

---

### **2. 项目台账导入 - 字段映射**

**文件**: [`views_project_ledger.py`](file://e:\EIMS2026\eims_app\views\views_project_ledger.py#L310-L321)

**新增代码**:
```python
elif field_name == 'contract_category':
    # 合同类别映射（支持多种写法）
    category_mapping = {
        '工程监理': 'engineering_supervision',
        '工程造价': 'cost_consulting',
        '造价咨询': 'cost_consulting',
        '工程检测': 'testing',
        '检测': 'testing',
        '全过程咨询': 'whole_process_consulting',
    }
    data[field_name] = category_mapping.get(str(value).strip(), 'engineering_supervision')
```

**效果**: 
- 自动将中文转换为数据库存储值
- 支持多种写法映射到同一个值
- 默认值为"工程监理"

---

### **3. 合同管理导入 - 字段映射**

**文件**: [`views_contract_management.py`](file://e:\EIMS2026\eims_app\views\views_contract_management.py#L271-L282)

**修改内容**: 与项目台账相同，添加合同类别映射逻辑

---

### **4. Excel 模板 - 填写说明更新**

**文件**: [`create_import_templates.py`](file://e:\EIMS2026\create_import_templates.py)

**修改前**:
```python
['合同类别', '工程监理/造价咨询/检测/全过程咨询'],
```

**修改后**:
```python
['合同类别', '工程监理/工程造价/工程检测/全过程咨询'],
```

**效果**: 模板中显示最新的允许值列表

---

## 💡 使用示例

### **Excel 中填写**

在"合同类别"列中可以填写：

| ✅ 正确写法 | ❌ 错误写法 |
|-----------|-----------|
| 工程监理 | 监理 |
| 工程造价 | 造价 |
| 造价咨询 | 咨询 |
| 工程检测 | 检测工程 |
| 检测 | test |
| 全过程咨询 | 全咨 |

### **导入后的存储**

无论填写哪种写法，数据库中都会存储为标准英文代码：

| Excel 填写 | 数据库存储 |
|-----------|-----------|
| 工程监理 | `engineering_supervision` |
| 工程造价 | `cost_consulting` |
| 造价咨询 | `cost_consulting` |
| 工程检测 | `testing` |
| 检测 | `testing` |
| 全过程咨询 | `whole_process_consulting` |

---

## 🎯 映射关系详解

### **完整映射表**

```python
{
    '工程监理'           → 'engineering_supervision',
    '工程造价'           → 'cost_consulting',
    '造价咨询'           → 'cost_consulting',      # 同义词
    '工程检测'           → 'testing',
    '检测'               → 'testing',              # 同义词
    '全过程咨询'         → 'whole_process_consulting',
}
```

### **为什么支持多种写法？**

1. **用户习惯不同**：
   - 有些用户习惯说"工程造价"
   - 有些用户习惯说"造价咨询"
   - 实际上指的是同一类业务

2. **向后兼容**：
   - 旧数据可能使用"造价咨询"和"检测"
   - 新数据可以使用更规范的"工程造价"和"工程检测"
   - 系统同时支持两种写法，避免导入失败

3. **容错性强**：
   - 即使用户填写了不同的表述，系统也能正确识别
   - 减少因用词不一致导致的导入错误

---

## 📊 验证规则

### **调试工具中的验证**

```python
choice_validations = {
    'contract_category': [
        '工程监理',        # 标准
        '工程造价',        # 新增
        '工程检测',        # 新增
        '造价咨询',        # 原有
        '检测',            # 原有
        '全过程咨询',      # 标准
    ],
    # ... 其他字段 ...
}
```

### **如果填写了不允许的值**

**示例**: 填写"监理"、"设计"、"施工"等

**结果**: 
- 调试工具会显示警告 ⚠️
- 导入时会映射为默认值"工程监理"
- 建议在调试阶段修正

---

## 🔍 常见问题

### **Q1: 为什么要支持"工程造价"和"工程检测"？**

**A**: 这是用户提出的需求。虽然模型定义中使用的是"造价咨询"和"检测"，但实际业务中用户更习惯说"工程造价"和"工程检测"。为了提高用户体验，系统现在同时支持这两种写法。

### **Q2: 如果我填写"工程造价"，数据库会存什么？**

**A**: 数据库会存储为 `cost_consulting`（与"造价咨询"相同）。系统会自动将中文映射为英文代码。

### **Q3: 旧的导入文件还能用吗？**

**A**: 可以！系统完全向后兼容。旧文件中使用的"造价咨询"和"检测"仍然有效。

### **Q4: 如果填写了不在列表中的值会怎样？**

**A**: 会映射为默认值 `engineering_supervision`（工程监理）。但建议在调试工具中检查并修正。

---

## 📁 相关文件

### **修改的文件**
- [`debug_import_tool.py`](file://e:\EIMS2026\debug_import_tool.py#L376) - 调试工具验证规则
- [`views_project_ledger.py`](file://e:\EIMS2026\eims_app\views\views_project_ledger.py#L310-L321) - 项目台账导入映射
- [`views_contract_management.py`](file://e:\EIMS2026\eims_app\views\views_contract_management.py#L271-L282) - 合同管理导入映射
- [`create_import_templates.py`](file://e:\EIMS2026\create_import_templates.py) - Excel 模板生成

### **生成的模板**
- `static/templates/project_ledger_import_template.xlsx` - 项目台账模板
- `static/templates/contract_management_import_template.xlsx` - 合同管理模板

---

## ✅ 总结

### **支持的合同类别（6 种）**

✅ **工程监理** → `engineering_supervision`  
✅ **工程造价** → `cost_consulting` (新增)  
✅ **造价咨询** → `cost_consulting` (兼容)  
✅ **工程检测** → `testing` (新增)  
✅ **检测** → `testing` (兼容)  
✅ **全过程咨询** → `whole_process_consulting`  

### **优势**

- 🎯 **更灵活**: 支持多种表述方式
- 🔄 **向后兼容**: 旧数据不受影响
- 🛡️ **容错性强**: 减少导入失败
- 📊 **统一存储**: 最终都映射为标准代码

---

**更新时间**: 2026-03-25 02:00  
**状态**: ✅ 已上线  
**影响范围**: 合同类别字段的导入和验证
