# 数据库清理实施记录

## 📋 **阶段 1：代码审查完成** ✅

### **使用旧模型的文件清单**

#### **Project 旧模型（7 个文件）**
1. `views_project.py` - 项目主要视图
2. `views_monthly_report.py` - 月度报告视图  
3. `views_personnel.py` - 人员管理视图
4. `views_allocation_visual.py` - 可视化分配视图
5. `views_personnel_detail.py` - 人员详情视图
6. `views_contract.py` - 合同视图（关联查询）
7. `forms_monthly_report.py` - 月度报告表单

#### **Contract 旧模型（2 个文件）**
1. `views_contract.py` - 合同主要视图
2. `forms.py` - 合同表单

---

## 🎯 **实施策略**

### **关键发现**

当前系统已经在使用 `ProjectDetail` 表作为单表多视图架构：
- ✅ 项目台账模块 - 使用 `ProjectLedgerForm` + `ProjectDetail` 模型
- ✅ 合同管理模块 - 使用 `ContractManagementForm` + `ProjectDetail` 模型
- ✅ 导入功能 - 写入 `ProjectDetail` 表

**但存在的问题：**
- ❌ 项目管理主视图仍在使用旧的 `Project` 模型
- ❌ 合同管理主视图仍在使用旧的 `Contract` 模型
- ❌ 月度报告、人员管理等模块也在引用旧模型

### **解决方案调整**

**不需要创建新表单！** 因为：
1. 已有 `ProjectLedgerForm` - 用于项目台账
2. 已有 `ContractManagementForm` - 用于合同管理
3. 只需修改视图，让它们使用正确的模型和表单

---

## 🚀 **阶段 3：修改视图计划**

### **视图修改优先级**

#### **高优先级（核心业务）**
1. `views_project.py` - 项目管理主视图
2. `views_contract.py` - 合同管理主视图

#### **中优先级（关联模块）**
3. `views_monthly_report.py` - 月度报告
4. `views_personnel.py` - 人员管理
5. `views_allocation_visual.py` - 可视化分配
6. `views_personnel_detail.py` - 人员详情

#### **低优先级（辅助功能）**
7. `forms_monthly_report.py` - 月度报告表单
8. `views_index.py` - 首页统计

---

## 📝 **修改方案**

### **方案 A：渐进式修改（推荐）**

**优点：**
- ✅ 风险分散
- ✅ 易于回滚
- ✅ 可以逐步测试

**步骤：**
1. 先修改 `views_project.py` 和 `views_contract.py`
2. 测试通过
3. 再修改其他关联视图
4. 最后迁移数据并删除旧表

### **方案 B：一次性修改**

**优点：**
- ✅ 快速完成
- ✅ 没有中间状态

**缺点：**
- ❌ 风险集中
- ❌ 调试困难

---

## 💡 **我的决定**

采用**方案 A：渐进式修改**

**理由：**
1. 降低风险
2. 可以随时停止
3. 便于定位问题
4. 用户影响最小

---

## 📊 **下一步行动**

### **立即执行：修改 views_project.py**

**目标：**
将 `ProjectListView` 从使用 `Project` 模型改为使用 `ProjectDetail` 模型

**修改内容：**
```python
# 修改前
class ProjectListView(ListView):
    model = Project
    template_name = 'project/list.html'
    queryset = Project.objects.all()

# 修改后
class ProjectListView(ListView):
    model = ProjectDetail
    template_name = 'project_ledger/list.html'  # 重定向到项目台账页面
    queryset = ProjectDetail.objects.all()
```

**原因：**
- 项目管理的列表功能已经在项目台账中实现
- 避免重复代码
- 确保数据同步

---

**准备开始实施！请稍候...**
