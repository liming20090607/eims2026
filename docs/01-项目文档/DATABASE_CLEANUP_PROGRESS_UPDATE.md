# 数据库清理实施进度更新

## ✅ **阶段 3a 完成：views_project.py 核心功能**

### **已完成的修改**

#### **✅ 类视图（4 个）**
1. ProjectListView - 列表视图 → ProjectDetail ✅
2. ProjectCreateView - 创建视图 → ProjectDetail ✅
3. ProjectUpdateView - 更新视图 → ProjectDetail ✅
4. ProjectDeleteView - 删除视图 → ProjectDetail ✅
5. ProjectDetailView - 详情视图 → ProjectDetail ✅

#### **✅ 函数视图（5 个）**
1. project_batch_delete - 批量删除 → ProjectDetail ✅
2. project_by_contract - AJAX 查询 → ProjectDetail ✅
3. project_export - Excel 导出 → ProjectDetail ✅
4. project_import - 已弃用，重定向 ✅

#### **⏳ 待处理的导入函数（3 个）**
1. import_project_dynamic - 导入项目动态
   - 依赖 ProjectDynamic 模型
   - 外键关联旧的 Project 模型
   - **建议：** 稍后在模型迁移时统一处理

2. import_output_payment - 导入产值回款
   - 依赖 OutputPayment 模型
   - 可能也外键关联旧模型
   - **建议：** 稍后在模型迁移时统一处理

3. import_personnel - 导入人员信息
   - 可能依赖其他模型
   - **建议：** 稍后在模型迁移时统一处理

---

## 🎯 **策略调整**

### **原因**
这些导入函数涉及的模型外键仍然指向旧的 Project 模型：
```python
class ProjectDynamic(BaseModel):
    project = models.ForeignKey('Project', on_delete=models.CASCADE)  # ❌ 旧模型
```

如果现在修改视图，需要先修改模型和外键关系，这会涉及：
1. 修改多个模型文件
2. 创建数据库迁移
3. 迁移现有数据
4. 风险较高

### **新策略：分两阶段**

#### **阶段 A：核心业务优先（当前）**
- ✅ 完成项目台账和合同管理的 CRUD
- ✅ 确保基本的增删改查都使用 ProjectDetail
- ⏸️ 暂时跳过辅助功能的导入函数

#### **阶段 B：辅助功能迁移（后续）**
- 修改 ProjectDynamic 等模型的外键
- 创建并执行数据库迁移
- 修改相关的导入函数
- 测试验证

---

## 🚀 **当前进度：阶段 3b**

### **下一步：修改 views_contract.py**

**目标：** 将合同管理模块的所有视图改为使用 ProjectDetail 模型

**预计工作量：**
- 主要视图函数：约 8-10 个
- 预计时间：2-3 小时

**关键文件：**
- `eims_app/views/views_contract.py`
- `eims_app/forms/form_contract.py`（可能需要调整）

---

### **views_contract.py 需要修改的内容**

基于之前的代码审查，需要修改：

1. **contract_list** - 合同列表
   - 从 Contract.objects 改为 ProjectDetail.objects
   - 调整筛选条件

2. **contract_add** - 新增合同
   - 改用 ProjectDetail 模型
   - 使用 ContractManagementForm

3. **contract_edit** - 编辑合同
   - 改用 ProjectDetail 模型
   - 使用 ContractManagementForm

4. **contract_delete** - 删除合同
   - 改用 ProjectDetail 模型

5. **contract_import** - 合同导入
   - 可能已有完整功能，检查即可

6. **其他辅助函数**
   - contract_export
   - contract_detail
   - 等

---

## 📊 **总体进度**

| 阶段 | 任务 | 状态 | 完成度 |
|------|------|------|--------|
| **阶段 1** | 代码审查 | ✅ COMPLETE | 100% |
| **阶段 2** | 表单准备 | ✅ COMPLETE | 100% |
| **阶段 3a** | views_project.py | ✅ COMPLETE | 95% |
| **阶段 3b** | views_contract.py | 🔄 IN PROGRESS | 0% |
| **阶段 3c** | 关联视图 | ⏳ PENDING | 0% |
| **阶段 4** | 数据迁移 | ⏳ PENDING | 0% |
| **阶段 5** | 删除旧表 | ⏳ PENDING | 0% |
| **阶段 6** | 测试验证 | ⏳ PENDING | 0% |

**总体进度：约 35%**

---

## 💡 **接下来的工作计划**

### **立即执行：修改 views_contract.py**

**步骤：**
1. 修改模型导入
2. 修改所有视图函数
3. 调整表单引用
4. 测试基本功能

**预期结果：**
- ✅ 合同列表显示 ProjectDetail 数据
- ✅ 新增合同保存到 ProjectDetail
- ✅ 编辑合同更新 ProjectDetail
- ✅ 删除合同从 ProjectDetail 删除

---

### **随后执行：修改关联视图**

**文件清单：**
1. views_monthly_report.py
2. views_personnel.py
3. views_allocation_visual.py
4. views_personnel_detail.py
5. forms_monthly_report.py
6. views_index.py

**策略：**
- 只修改查询引用（从 Project 改为 ProjectDetail）
- 不修改模型外键（留到后续阶段）

---

### **最后执行：模型迁移和旧表清理**

**任务：**
1. 修改 ProjectDynamic 等模型的外键
2. 创建数据库迁移文件
3. 执行迁移
4. 迁移旧表数据
5. 删除旧表

**风险提示：**
- ⚠️ 需要停机维护
- ⚠️ 需要完整备份
- ⚠️ 可能需要回滚方案

---

## ⚠️ **注意事项**

### **1. 外键依赖问题**

当前发现的依赖关系：
```
ProjectDynamic.project → ForeignKey('Project') ❌
OutputPayment.project → ForeignKey('Project') ? (待检查)
Personnel.project → ForeignKey('Project') ? (待检查)
```

**解决方案：**
- 短期：保留现状，使用 project_code 字段关联
- 长期：修改外键到 ProjectDetail，执行迁移

---

### **2. URL 路由兼容性**

当前配置：
```python
path('projects/', ProjectListView.as_view(), name='project_list')
path('project_ledger/', views_project_ledger.project_ledger_list, name='project_ledger_list')
```

由于 ProjectListView 现在使用 project_ledger 模板，两个 URL 实际指向同一个页面。

**建议：**
- 保持现状（向后兼容）
- 或移除 /projects/，统一使用 /project_ledger/

---

### **3. 模板字段兼容性**

某些模板可能还在引用旧字段：
```html
{{ project.project_category }}  <!-- ❌ Project 特有 -->
```

**解决：**
- 如果发现错误，调整为 {{ project.contract_category }}
- 或添加条件判断

---

## 📞 **下一步行动**

**立即执行：**
- ✅ 修改 views_contract.py
- ✅ 确保合同管理模块完全迁移

**等待您的确认：**
- 当前策略是否合理？
- 是否同意分阶段实施？

**我的建议：**
继续推进，先完成核心业务（项目 + 合同），再处理辅助功能！

---

**准备开始修改 views_contract.py！** 🚀
