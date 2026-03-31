# 动态下拉列表实现方案

## 📋 目标

为系统中所有使用 Choice 字段的下拉列表添加"手动添加"功能，允许超级管理员在表单交互时动态添加新选项。

---

## 🎯 需要实现的模块

### **1. 项目台账模块**

#### **1.1 项目状态 (project_status)**
- **模型**: `ProjectDetail` / `Project`
- **字段**: `project_status`
- **当前选项**:
  ```python
  PROJECT_STATUS_CHOICES = [
      ('not_started', '未开工'),
      ('under_construction', '在施工'),
      ('completed', '已完工'),
  ]
  ```
- **使用场景**: 
  - 新增/编辑项目详情页
  - 导入项目表格

#### **1.2 合同类别 (contract_category)**
- **模型**: `ProjectDetail` / `Project`
- **字段**: `contract_category`
- **当前选项**:
  ```python
  CONTRACT_CATEGORY_CHOICES = [
      ('engineering_supervision', '工程监理'),
      ('cost_consulting', '造价咨询'),
      ('whole_process_consulting', '全过程咨询'),
  ]
  ```
- **使用场景**: 
  - 新增/编辑项目详情页
  - 导入项目表格

#### **1.3 合同状态 (contract_status)**
- **模型**: `ProjectDetail`
- **字段**: `contract_status`
- **当前选项**:
  ```python
  CONTRACT_STATUS_CHOICES = [
      ('pending_review', '待审核'),
      ('executing', '在执行'),
      ('released', '已解除'),
  ]
  ```
- **使用场景**: 
  - 新增/编辑项目详情页

#### **1.4 结算情况 (settlement_status)**
- **模型**: `ProjectDetail`
- **字段**: `settlement_status`
- **当前选项**:
  ```python
  SETTLEMENT_STATUS_CHOICES = [
      ('unsettled', '未结算'),
      ('settled', '已结算'),
  ]
  ```
- **使用场景**: 
  - 新增/编辑项目详情页

#### **1.5 报建情况 (construction_permit_status)**
- **模型**: `ProjectDetail`
- **字段**: `construction_permit_status`
- **当前选项**:
  ```python
  CONSTRUCTION_PERMIT_CHOICES = [
      ('completed', '已完成'),
      ('incomplete', '未完成'),
  ]
  ```
- **使用场景**: 
  - 新增/编辑项目详情页

#### **1.6 进场通知 (entry_notice)**
- **模型**: `ProjectDetail`
- **字段**: `entry_notice`
- **当前选项**:
  ```python
  ENTRY_NOTICE_CHOICES = [
      ('no', '无'),
      ('yes', '有'),
  ]
  ```
- **使用场景**: 
  - 新增/编辑项目详情页

---

### **2. 项目动态模块**

#### **2.1 项目状态 (project_status)**
- **模型**: `ProjectDynamic`
- **字段**: `project_status`
- **当前选项**:
  ```python
  PROJECT_STATUS_CHOICES = [
      ('not_started', '未开工'),
      ('normal_construction', '正常施工'),
      ('stopped', '在停工'),
      ('completed', '已完工'),
  ]
  ```
- **使用场景**: 
  - 新增项目动态页 (`/project_ledger/{pk}/add-dynamic/`)

---

### **3. 人员管理模块**

#### **3.1 性别 (gender)**
- **模型**: `UserProfile` / `Personnel`
- **字段**: `gender`
- **当前选项**:
  ```python
  GENDER_CHOICES = [
      (0, '男'),
      (1, '女'),
  ]
  ```
- **使用场景**: 
  - 员工信息管理
  - 项目人员管理

#### **3.2 证书类型 (certificate_type)**
- **模型**: `EmployeeCertificate`
- **字段**: `certificate_type`
- **当前选项**:
  ```python
  CERTIFICATE_TYPE_CHOICES = [
      ('professional', '职业资格'),
      ('technical', '专业技术'),
      ('training', '岗位培训'),
  ]
  ```
- **使用场景**: 
  - 员工证书管理

#### **3.3 分配状态 (allocation_status)**
- **模型**: `EmployeeAllocation`
- **字段**: `allocation_status`
- **当前选项**:
  ```python
  ALLOCATION_STATUS_CHOICES = [
      ('allocated', '已分配'),
      ('unallocated', '未分配'),
  ]
  ```
- **使用场景**: 
  - 员工分配管理

---

### **4. 审批流程模块**

#### **4.1 审批状态 (status)**
- **模型**: `ContractApproval`
- **字段**: `status`
- **当前选项**:
  ```python
  APPROVAL_STATUS_CHOICES = [
      ('draft', '草稿'),
      ('pending', '待审核'),
      ('approved', '已通过'),
      ('rejected', '已驳回'),
  ]
  ```
- **使用场景**: 
  - 合同审批流程

#### **4.2 审批流程类型 (approval_flow_type)**
- **模型**: `ContractApproval`
- **字段**: `approval_flow_type`
- **当前选项**:
  ```python
  APPROVAL_FLOW_TYPE_CHOICES = [
      ('user_selected', '由我选择审批人'),
      ('system_assigned', '由系统自动指派'),
  ]
  ```
- **使用场景**: 
  - 合同审批流程配置

#### **4.3 审批结果 (approval_result)**
- **模型**: `ContractApproval`
- **字段**: `approval_result`
- **当前选项**:
  ```python
  APPROVAL_RESULT_CHOICES = [
      ('pending', '待签订'),
      ('signed', '已签订'),
  ]
  ```
- **使用场景**: 
  - 合同审批结果

#### **4.4 文件类型 (file_type)**
- **模型**: `ApprovalAttachment`
- **字段**: `file_type`
- **当前选项**:
  ```python
  FILE_TYPE_CHOICES = [
      ('contract', '合同文件'),
      ('attachment', '附件材料'),
  ]
  ```
- **使用场景**: 
  - 审批附件上传

#### **4.5 操作类型 (action)**
- **模型**: `ApprovalRecord`
- **字段**: `action`
- **当前选项**:
  ```python
  ACTION_CHOICES = [
      ('submit', '提交'),
      ('approve', '同意'),
      ('reject', '驳回'),
  ]
  ```
- **使用场景**: 
  - 审批记录

#### **4.6 角色 (role)**
- **模型**: `DepartmentManager`
- **字段**: `role`
- **当前选项**:
  ```python
  ROLE_CHOICES = [
      ('department_manager', '部门主管'),
      ('senior_leader', '上级领导'),
  ]
  ```
- **使用场景**: 
  - 部门主管配置

#### **4.7 流程类型 (flow_type)**
- **模型**: `ApprovalFlowConfig`
- **字段**: `flow_type`
- **当前选项**:
  ```python
  FLOW_TYPE_CHOICES = [
      ('contract_approval', '合同审批'),
      ('project_approval', '项目审批'),
  ]
  ```
- **使用场景**: 
  - 审批流程配置

#### **4.8 审批人角色 (approver_role)**
- **模型**: `ApprovalFlowConfig`
- **字段**: `approver_role`
- **当前选项**: 引用 `DepartmentManager.ROLE_CHOICES`
- **使用场景**: 
  - 审批流程配置

---

### **5. 工作流模块**

#### **5.1 角色名称 (name)**
- **模型**: `WorkflowRole`
- **字段**: `name`
- **当前选项**:
  ```python
  ROLE_CHOICES = [
      ('initiator', '发起人'),
      ('approver', '审批人'),
      ('final_approver', '最终审批人'),
  ]
  ```
- **使用场景**: 
  - 工作流角色配置

#### **5.2 流程状态 (status)**
- **模型**: `ApprovalFlow`
- **字段**: `status`
- **当前选项**:
  ```python
  FLOW_STATUS_CHOICES = [
      ('draft', '草稿'),
      ('in_progress', '进行中'),
      ('completed', '已完成'),
      ('cancelled', '已取消'),
  ]
  ```
- **使用场景**: 
  - 工作流实例

#### **5.3 操作类型 (action)**
- **模型**: `FlowAction`
- **字段**: `action`
- **当前选项**:
  ```python
  ACTION_CHOICES = [
      ('submit', '提交'),
      ('approve', '同意'),
      ('reject', '驳回'),
      ('withdraw', '撤回'),
  ]
  ```
- **使用场景**: 
  - 工作流操作

---

### **6. 用户模块**

#### **6.1 填报周期 (report_period)**
- **模型**: `UserProfile`
- **字段**: `report_period`
- **当前选项**:
  ```python
  REPORT_PERIOD_CHOICES = [
      ('daily', '日报'),
      ('weekly', '周报'),
      ('monthly', '月报'),
  ]
  ```
- **使用场景**: 
  - 用户填报配置

#### **6.2 填报状态 (status)**
- **模型**: `MonthlyReport`
- **字段**: `status`
- **当前选项**:
  ```python
  REPORT_STATUS_CHOICES = [
      ('draft', '草稿'),
      ('submitted', '已提交'),
      ('approved', '已审核'),
  ]
  ```
- **使用场景**: 
  - 月度报告管理

---

## 🛠️ 实现策略

### **方案 A: 通用 API + 通用前端组件**

**优点**:
- ✅ 代码复用性高
- ✅ 维护成本低
- ✅ 一致的用户体验

**缺点**:
- ❌ 初始实现复杂度较高
- ❌ 需要统一的数据库表存储选项

### **方案 B: 针对性实现（推荐）**

**优点**:
- ✅ 实现简单直接
- ✅ 灵活性高
- ✅ 可以按需逐步实现

**缺点**:
- ❌ 代码重复较多
- ❌ 维护成本较高

---

## 📝 推荐实施方案

### **第一阶段：高频使用字段**

优先实现以下模块的动态添加功能：

1. **项目台账模块** (最重要)
   - ✅ 项目状态
   - ✅ 合同类别
   - ✅ 合同状态

2. **项目动态模块** (已完成)
   - ✅ 项目状态

3. **人员管理模块**
   - ✅ 性别（这个可能不需要动态添加）
   - ✅ 证书类型
   - ✅ 分配状态

### **第二阶段：审批相关字段**

4. **审批流程模块**
   - 审批状态
   - 审批流程类型
   - 文件类型

### **第三阶段：其他字段**

5. **工作流模块**
6. **用户模块**

---

## 💡 技术实现细节

### **1. 数据库设计**

创建通用选项表：

```python
class DynamicChoice(models.Model):
    """动态选项表"""
    category = models.CharField(max_length=50, verbose_name='选项类别')
    code = models.CharField(max_length=50, verbose_name='选项代码')
    name = models.CharField(max_length=100, verbose_name='选项名称')
    order = models.IntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    
    class Meta:
        unique_together = ['category', 'code']
        ordering = ['category', 'order']
```

### **2. 视图函数**

```python
@login_required
@user_passes_test(is_superuser)
def add_dynamic_choice(request, category):
    """通用动态选项添加 API"""
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('code', '').lower().strip()
        name = data.get('name', '').strip()
        
        # 验证
        if not code or not name:
            return JsonResponse({
                'success': False,
                'message': '选项代码和名称不能为空'
            })
        
        # 检查是否已存在
        if DynamicChoice.objects.filter(category=category, code=code).exists():
            return JsonResponse({
                'success': False,
                'message': f'选项代码 {code} 已存在'
            })
        
        # 创建
        choice = DynamicChoice.objects.create(
            category=category,
            code=code,
            name=name,
            order=DynamicChoice.objects.filter(category=category).count() + 1
        )
        
        return JsonResponse({
            'success': True,
            'message': '添加成功',
            'data': {
                'code': choice.code,
                'name': choice.name
            }
        })
    
    return JsonResponse({'success': False, 'message': '不支持的请求方法'})
```

### **3. 前端组件**

```javascript
// 通用动态添加函数
function addDynamicChoice(category, choiceCodeElId, choiceNameElId, callback) {
    const modalHtml = `
        <div class="modal fade" id="addChoiceModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <form id="addChoiceForm">
                        <div class="modal-header">
                            <h5 class="modal-title">添加${getCategoryName(category)}</h5>
                        </div>
                        <div class="modal-body">
                            <div class="mb-3">
                                <label class="form-label">选项代码</label>
                                <input type="text" class="form-control" name="code" required 
                                       placeholder="请输入英文代码">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">选项名称</label>
                                <input type="text" class="form-control" name="name" required 
                                       placeholder="请输入中文名称">
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            <button type="submit" class="btn btn-primary">确定</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
    
    // 显示模态框并绑定事件
    // ...
}
```

---

## ✅ 已完成的功能

### **1. 部门角色类型动态添加**
- **文件**: 
  - `views_department.py` - `add_role_type` 视图
  - `role_form.html` - 前端界面
  - `urls.py` - `/api/add-role-type/` 路由

- **功能**: 在添加角色时，可以动态添加新的角色类型

---

## 📊 优先级排序

| 优先级 | 模块 | 字段 | 使用频率 | 建议实现 |
|--------|------|------|----------|----------|
| P0 | 项目台账 | 项目状态、合同类别 | ⭐⭐⭐⭐⭐ | 立即实现 |
| P0 | 项目动态 | 项目状态 | ⭐⭐⭐⭐⭐ | ✅ 已实现 |
| P1 | 项目台账 | 合同状态、结算情况 | ⭐⭐⭐⭐ | 尽快实现 |
| P1 | 人员管理 | 证书类型、分配状态 | ⭐⭐⭐⭐ | 尽快实现 |
| P2 | 审批流程 | 审批状态、文件类型 | ⭐⭐⭐ | 按需实现 |
| P3 | 工作流 | 角色名称、流程状态 | ⭐⭐ | 按需实现 |
| P3 | 用户模块 | 填报周期、填报状态 | ⭐⭐ | 按需实现 |

---

## 🎯 下一步行动

### **立即实施：项目台账模块**

1. **创建通用 API**
   - 创建 `add_dynamic_choice` 视图函数
   - 配置 URL 路由

2. **修改项目台账表单**
   - 在项目详情页的导入表单中添加"+ 新增"按钮
   - 为每个下拉列表添加动态添加功能

3. **测试验证**
   - 测试添加新选项
   - 测试选项是否正确显示在下拉列表中
   - 测试数据保存

---

**文档创建时间**: 2026-03-26  
**最后更新**: 2026-03-26  
**状态**: 规划中
