# 数据库清理实施进度报告

## ✅ **已完成的工作**

### **阶段 1：代码审查** ✅ COMPLETE

**发现使用旧模型的文件：**

#### Project 旧模型（7 个文件）
1. ✅ `views_project.py` - 已开始修改
2. ⏳ `views_monthly_report.py` - 待修改
3. ⏳ `views_personnel.py` - 待修改
4. ⏳ `views_allocation_visual.py` - 待修改
5. ⏳ `views_personnel_detail.py` - 待修改
6. ⏳ `views_contract.py` - 关联查询，待修改
7. ⏳ `forms_monthly_report.py` - 待修改

#### Contract 旧模型（2 个文件）
1. ⏳ `views_contract.py` - 待修改
2. ⏳ `forms.py` - 待修改

---

### **阶段 2：表单准备** ✅ COMPLETE

**已有表单：**
- ✅ `ProjectLedgerForm` - 项目台账表单（完整）
- ✅ `ContractManagementForm` - 合同管理表单（完整）

**结论：** 不需要创建新表单，现有表单已满足需求！

---

### **阶段 3：视图修改** 🔄 IN PROGRESS

#### ✅ 已完成：`views_project.py` 核心视图类

**修改内容：**

1. **ProjectListView** (列表视图)
   ```python
   # 修改前
   model = Project
   template_name = 'project/list.html'
   
   # 修改后
   model = ProjectDetail
   template_name = 'project_ledger/list.html'
   queryset = ProjectDetail.objects.all()
   ```
   ✅ 状态：已完成

2. **ProjectCreateView** (创建视图)
   ```python
   # 修改前
   model = Project
   form_class = ProjectForm
   template_name = 'project/add.html'
   
   # 修改后
   model = ProjectDetail
   form_class = ProjectLedgerForm
   template_name = 'project_ledger/form.html'
   success_url = reverse_lazy('eims_app:project_ledger_list')
   ```
   ✅ 状态：已完成

3. **ProjectUpdateView** (更新视图)
   ```python
   # 修改前
   model = Project
   form_class = ProjectForm
   
   # 修改后
   model = ProjectDetail
   form_class = ProjectLedgerForm
   ```
   ✅ 状态：已完成

4. **ProjectDeleteView** (删除视图)
   ```python
   # 修改前
   model = Project
   template_name = 'project/delete.html'
   
   # 修改后
   model = ProjectDetail
   template_name = 'project_ledger/delete.html'
   success_url = reverse_lazy('eims_app:project_ledger_list')
   ```
   ✅ 状态：已完成

5. **ProjectDetailView** (详情视图)
   ⏳ 状态：待修改（逻辑复杂，需要保留导航功能）

6. **导入函数和其他辅助函数**
   ⏳ 状态：待检查和修改

---

## 📋 **待完成的工作**

### **阶段 3：视图修改（续）** ⏳

**待修改文件清单：**

1. ⏳ `views_project.py` - 剩余部分
   - ProjectDetailView
   - project_batch_delete
   - import_from_excel
   - export_to_csv
   - export_to_excel
   - 等其他辅助函数

2. ⏳ `views_contract.py` - 完整修改
   - contract_list
   - contract_add
   - contract_edit
   - contract_delete
   - contract_import
   - 等所有合同相关视图

3. ⏳ `views_monthly_report.py`
   - 所有引用 Project 的地方

4. ⏳ `views_personnel.py`
   - 所有引用 Project 的地方

5. ⏳ `views_allocation_visual.py`
   - 所有引用 Project 的地方

6. ⏳ `views_personnel_detail.py`
   - 所有引用 Project 的地方

7. ⏳ `forms_monthly_report.py`
   - 月度报告表单中的 Project 字段

8. ⏳ `views_index.py`
   - 首页统计信息

---

### **阶段 4：数据迁移** ⏳ PENDING

**任务清单：**

1. ⏳ 备份当前数据库
   ```bash
   cp db.sqlite3 db_backup_before_migration.sqlite3
   ```

2. ⏳ 编写迁移脚本
   ```python
   # 迁移 Project 表数据到 ProjectDetail
   for project in Project.objects.all():
       ProjectDetail.objects.update_or_create(
           project_code=project.project_code,
           defaults={...}
       )
   
   # 迁移 Contract 表数据到 ProjectDetail
   for contract in Contract.objects.all():
       ProjectDetail.objects.update_or_create(
           contract_code=contract.contract_code,
           defaults={...}
       )
   ```

3. ⏳ 执行迁移并验证

---

### **阶段 5：删除旧表** ⏳ PENDING

**任务清单：**

1. ⏳ 确认所有代码都已修改完成
2. ⏳ 再次备份数据库
3. ⏳ 删除旧表
   ```sql
   DROP TABLE eims_app_project;
   DROP TABLE eims_app_contract;
   ```
4. ⏳ 从 models/__init__.py 中移除旧模型引用
5. ⏳ 验证系统运行正常

---

### **阶段 6：测试验证** ⏳ PENDING

**测试清单：**

1. ⏳ 测试项目新增功能
2. ⏳ 测试项目编辑功能
3. ⏳ 测试项目删除功能
4. ⏳ 测试项目列表显示
5. ⏳ 测试合同新增功能
6. ⏳ 测试合同编辑功能
7. ⏳ 测试合同删除功能
8. ⏳ 测试合同列表显示
9. ⏳ 测试数据同步（导入、删除联动）
10. ⏳ 测试月度报告模块
11. ⏳ 测试人员管理模块
12. ⏳ 测试可视化分配模块

---

## 📊 **当前进度**

| 阶段 | 任务 | 状态 | 完成度 |
|------|------|------|--------|
| **阶段 1** | 代码审查 | ✅ COMPLETE | 100% |
| **阶段 2** | 表单准备 | ✅ COMPLETE | 100% |
| **阶段 3** | 视图修改 | 🔄 IN PROGRESS | 20% |
| - | views_project.py 核心类 | ✅ DONE | 80% |
| - | views_project.py 其他函数 | ⏳ TODO | 0% |
| - | views_contract.py | ⏳ TODO | 0% |
| - | 其他关联视图 | ⏳ TODO | 0% |
| **阶段 4** | 数据迁移 | ⏳ PENDING | 0% |
| **阶段 5** | 删除旧表 | ⏳ PENDING | 0% |
| **阶段 6** | 测试验证 | ⏳ PENDING | 0% |

**总体进度：约 25%**

---

## 🎯 **下一步行动**

### **立即执行：完成 views_project.py**

**剩余任务：**
1. 修改 ProjectDetailView
2. 检查并修改所有辅助函数
3. 确保所有导入导出功能正常工作

**预计时间：** 2-3 小时

---

### **随后执行：修改 views_contract.py**

**任务量：**
- 约 500+ 行代码
- 多个视图函数
- 导入导出功能

**预计时间：** 3-4 小时

---

### **最后执行：修改关联视图**

**涉及文件：**
- views_monthly_report.py
- views_personnel.py
- views_allocation_visual.py
- views_personnel_detail.py
- forms_monthly_report.py
- views_index.py

**预计时间：** 4-6 小时

---

## ⚠️ **注意事项**

### **1. URL 路由一致性**

修改后需要确保 URL 路由正确：
```python
# urls.py 中可能需要调整
path('projects/', ...) → 重定向到 /project_ledger/
path('project_ledger/', ...) → 保持不变
```

### **2. 模板兼容性**

确保模板能正确处理 ProjectDetail 模型的字段：
- 项目详情页面可能需要调整
- 某些模板可能依赖旧的 Project 模型字段

### **3. 外键关联**

检查是否有其他模型外键引用了 Project 或 Contract：
```python
class MonthlyReport(models.Model):
    project = models.ForeignKey(Project, ...)  # ❌ 需要改为 ProjectDetail
```

### **4. JavaScript 和 AJAX**

前端可能有硬编码的 URL：
```javascript
// 可能需要更新
fetch('/api/projects/') → fetch('/api/project_ledger/')
```

---

## 💡 **建议策略**

### **渐进式修改（推荐）**

**优点：**
- ✅ 风险分散
- ✅ 可以随时停止
- ✅ 便于调试
- ✅ 用户影响小

**步骤：**
1. 先完成 views_project.py（核心业务）
2. 测试通过
3. 再修改 views_contract.py
4. 测试通过
5. 最后修改其他关联视图
6. 一次性迁移数据并删除旧表

---

### **快速完成方案**

如果时间紧迫，可以：
1. 只修改 views_project.py 和 views_contract.py
2. 暂时保留其他视图的旧模型引用
3. 先迁移数据并删除旧表
4. 后续再逐步修复其他视图

**风险：** 某些功能可能暂时不可用

---

## 📞 **需要您的决定**

请告诉我您希望：

**选项 A：稳健推进（推荐）**
- ✅ 逐个文件修改，确保每个都测试通过
- ✅ 预计总时间：1-2 天
- ✅ 风险低，易于控制

**选项 B：快速完成**
- ⚠️ 优先修改核心视图
- ⚠️ 预计总时间：半天
- ⚠️ 部分功能可能暂时异常

**我的建议：选择选项 A**

---

**当前工作暂停，等待您的指示！**

我应该：
1. 继续完成 views_project.py 的剩余部分？
2. 还是先停下来，等您确认后再继续？
3. 或者您有其他想法？

请告诉我下一步如何行动！🚀
