# 动态选项使用指南

## 📋 概述

本系统现在支持在所有下拉列表（Choice 字段）中动态添加新选项。超级管理员可以通过两种方式管理选项：

1. **前台交互添加** - 在表单页面直接点击"+ 新增"按钮添加
2. **后台集中管理** - 在 Django Admin 后台统一管理

---

## 🎯 已支持的模块

### **项目台账模块**
- ✅ 项目状态 (`project.project_status`)
- ✅ 合同类别 (`project.contract_category`)
- ✅ 合同状态 (`projectdetail.contract_status`)
- ✅ 结算情况 (`projectdetail.settlement_status`)
- ✅ 报建情况 (`projectdetail.construction_permit_status`)
- ✅ 进场通知 (`projectdetail.entry_notice`)

### **项目动态模块**
- ✅ 项目状态 (`projectdynamic.project_status`)

### **人员管理模块**
- ✅ 性别 (`userprofile.gender`, `personnel.gender`)
- ✅ 证书类型 (`employeecertificate.certificate_type`)
- ✅ 分配状态 (`employeeallocation.allocation_status`)

### **审批流程模块**
- ✅ 审批状态 (`contractapproval.status`)
- ✅ 审批流程类型 (`contractapproval.approval_flow_type`)
- ✅ 审批结果 (`contractapproval.approval_result`)
- ✅ 附件类型 (`approvalattachment.file_type`)
- ✅ 审批操作 (`approvalrecord.action`)
- ✅ 部门角色 (`departmentmanager.role`)
- ✅ 流程类型 (`approvalflowconfig.flow_type`)

### **工作流模块**
- ✅ 工作流角色 (`workflowrole.name`)
- ✅ 工作流状态 (`approvalflow.status`)
- ✅ 工作流操作 (`flowaction.action`)

### **用户模块**
- ✅ 填报周期 (`userprofile.report_period`)
- ✅ 填报状态 (`monthlyreport.status`)

---

## 💻 使用方法

### **方法一：在前端表单中添加（推荐）**

#### **步骤 1: 在模板中引入 JS 文件**

```html+
{% load static %}
<script src="{% static 'js/dynamic_choice.js' %}"></script>
```

#### **步骤 2: 在下拉列表旁添加"+ 新增"按钮**

```html
<div class="mb-3">
    <label class="form-label">项目状态</label>
    <div class="input-group">
        <select class="form-select" name="project_status" id="id_project_status" required>
            <option value="">请选择状态</option>
            <option value="not_started">未开工</option>
            <option value="under_construction">在施工</option>
            <option value="completed">已完工</option>
        </select>
        <button type="button" class="btn btn-outline-primary" 
                onclick="addDynamicChoice('project.project_status', 'id_project_status', '项目状态')">
            <i class="bi bi-plus-circle"></i> 新增
        </button>
    </div>
</div>
```

#### **步骤 3: 自动加载动态选项（可选）**

如果希望页面加载时自动显示所有动态添加的选项：

```javascript
<script>
document.addEventListener('DOMContentLoaded', function() {
    // 加载动态选项
    loadDynamicChoices('project.project_status', 'id_project_status');
});
</script>
```

---

### **方法二：在 Django Admin 后台管理**

#### **访问路径**: `/admin/eims_app/dynamicchoice/`

#### **功能说明**:

1. **查看所有选项**
   - 按类别分组显示
   - 可看到每个选项的代码、名称、排序、启用状态

2. **添加新选项**
   - 点击"+ 添加"按钮
   - 选择类别、填写代码和名称
   - 保存即可

3. **编辑选项**
   - 点击某个选项进入编辑
   - 可修改：代码、名称、排序、启用状态

4. **批量操作**
   - 可批量禁用/启用选项
   - 可批量删除选项

---

## 🔧 技术实现细节

### **1. 数据库模型**

```python
class DynamicChoice(models.Model):
    """动态选项表"""
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    code = models.CharField(max_length=50)  # 如：not_started
    name = models.CharField(max_length=100)  # 如：未开工
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, ...)
    created_at = models.DateTimeField(auto_now_add=True)
```

### **2. API 接口**

#### **添加选项**
```
POST /api/dynamic-choices/add/
Body: {
    "category": "project.project_status",
    "code": "custom_status",
    "name": "自定义状态"
}
```

#### **获取选项列表**
```
GET /api/dynamic-choices/{category}/
返回：[
    {"code": "not_started", "name": "未开工"},
    {"code": "custom_status", "name": "自定义状态"}
]
```

#### **管理单个选项**
```
PUT /api/dynamic-choices/manage/{pk}/
DELETE /api/dynamic-choices/manage/{pk}/
```

---

## 📝 最佳实践

### **1. 命名规范**

**代码命名**:
- ✅ 正确：`not_started`, `under_construction`, `completed`
- ❌ 错误：`NotStarted`, `under-construction`, `123completed`

**规则**:
- 必须以小写字母开头
- 只能包含小写字母、数字和下划线
- 使用下划线分隔单词（snake_case）

**名称命名**:
- ✅ 正确：`未开工`, `在施工`, `已完工`
- ❌ 错误：`未开工 (新)`, `施工中...`, `已完成 1`

**规则**:
- 使用简洁明了的中文
- 不要包含特殊符号
- 保持与其他选项风格一致

### **2. 排序策略**

```python
# 默认选项排前面（order 值小）
order = 0    # not_started - 未开工
order = 1    # under_construction - 在施工
order = 2    # completed - 已完工

# 自定义选项排后面
order = 100  # custom_status - 自定义状态
```

### **3. 启用/禁用策略**

**场景**: 某个选项暂时不需要使用，但历史数据中可能已使用

**做法**:
- ✅ 设置为 `is_active = False`（软删除）
- ❌ 不要直接删除记录

**好处**:
- 不影响历史数据
- 可以随时恢复
- 新表单中不再显示该选项

---

## ⚠️ 注意事项

### **1. 权限控制**

- ✅ 只有超级管理员（`is_superuser=True`）可以添加/管理选项
- ✅ 普通用户只能看到已有的选项
- ✅ 前端会验证 CSRF Token

### **2. 数据一致性**

**问题**: 模型中定义的 Choice 选项与动态选项不一致怎么办？

**解决方案**:
```python
# 在视图中优先使用动态选项
from eims_app.models import DynamicChoice

def get_project_status_choices():
    # 先尝试从动态选项获取
    dynamic_choices = DynamicChoice.get_choices_for_category('project.project_status')
    if dynamic_choices:
        return dynamic_choices
    
    # 回退到模型默认定义
    return Project._meta.get_field('project_status').choices
```

### **3. 缓存问题**

**问题**: 添加选项后，其他用户看不到？

**解决方案**:
- 动态选项是实时从数据库读取的
- 无需手动清除缓存
- 确保浏览器没有缓存旧的页面（强制刷新 Ctrl+F5）

### **4. 迁移现有代码**

**已有表单如何支持动态选项？**

只需三步：
1. 在模板中引入 `dynamic_choice.js`
2. 在下拉列表旁添加"+ 新增"按钮
3. （可选）调用 `loadDynamicChoices()` 加载动态选项

---

## 🎨 UI/UX 优化建议

### **1. 按钮样式**

```html
<!-- 紧凑型 -->
<button type="button" class="btn btn-sm btn-outline-primary">
    <i class="bi bi-plus-circle"></i> 新增
</button>

<!-- 图标型 -->
<button type="button" class="btn btn-icon btn-outline-primary">
    <i class="bi bi-plus-circle"></i>
</button>

<!-- 文字型 -->
<button type="button" class="btn btn-link">
    <i class="bi bi-plus-circle"></i> 新增选项
</button>
```

### **2. 提示消息**

系统会自动显示成功/失败消息，位置在页面右上角：
- ✅ 绿色成功框："添加成功"
- ❌ 红色错误框："选项代码已存在"
- ⚠️ 黄色警告框："无效的类别"

### **3. 模态框样式**

使用 Bootstrap 5 标准模态框：
- 标题带图标
- 必填字段标红
- 底部有取消/确定按钮

---

## 🧪 测试清单

### **功能测试**
- [ ] 可以成功添加新选项
- [ ] 新选项立即显示在下拉列表中
- [ ] 可以选中并保存新选项
- [ ] 刷新页面后新选项仍然存在
- [ ] 其他用户可以看到新选项

### **验证测试**
- [ ] 代码格式不正确时显示错误提示
- [ ] 代码重复时显示错误提示
- [ ] 类别无效时显示错误提示
- [ ] 非超级管理员无法访问 API

### **UI 测试**
- [ ] 按钮样式正确
- [ ] 模态框正常显示
- [ ] 提示消息正常显示和消失
- [ ] 移动端响应式正常

---

## 📊 示例代码

### **完整示例：项目台账导入表单**

```html
{% extends 'base/base.html' %}
{% load static %}

{% block extra_head %}
<script src="{% static 'js/dynamic_choice.js' %}"></script>
{% endblock %}

{% block content %}
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}
    
    <!-- 项目状态 -->
    <div class="mb-3">
        <label class="form-label">项目状态</label>
        <div class="input-group">
            <select class="form-select" name="project_status" id="id_project_status" required>
                <option value="">请选择状态</option>
                <option value="not_started">未开工</option>
                <option value="under_construction">在施工</option>
                <option value="completed">已完工</option>
            </select>
            <button type="button" class="btn btn-outline-primary" 
                    onclick="addDynamicChoice('project.project_status', 'id_project_status', '项目状态')">
                <i class="bi bi-plus-circle"></i> 新增
            </button>
        </div>
    </div>
    
    <!-- 合同类别 -->
    <div class="mb-3">
        <label class="form-label">合同类别</label>
        <div class="input-group">
            <select class="form-select" name="contract_category" id="id_contract_category" required>
                <option value="">请选择类别</option>
                <option value="engineering_supervision">工程监理</option>
                <option value="cost_consulting">造价咨询</option>
                <option value="whole_process_consulting">全过程咨询</option>
            </select>
            <button type="button" class="btn btn-outline-primary" 
                    onclick="addDynamicChoice('project.contract_category', 'id_contract_category', '合同类别')">
                <i class="bi bi-plus-circle"></i> 新增
            </button>
        </div>
    </div>
    
    <button type="submit" class="btn btn-primary">保存</button>
</form>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // 加载动态选项（可选）
    loadDynamicChoices('project.project_status', 'id_project_status');
    loadDynamicChoices('project.contract_category', 'id_contract_category');
});
</script>
{% endblock %}
```

---

## 🚀 下一步计划

### **第一阶段：核心模块** (当前)
- ✅ 创建动态选项模型
- ✅ 实现通用 API
- ✅ 创建前端组件
- ⏳ 应用到项目台账模块

### **第二阶段：扩展模块** (计划中)
- [ ] 应用到人员管理模块
- [ ] 应用到审批流程模块
- [ ] 应用到工作流模块

### **第三阶段：优化提升** (未来)
- [ ] 添加批量导入功能
- [ ] 添加选项使用统计
- [ ] 添加选项合并功能
- [ ] 添加选项历史记录

---

## 📞 技术支持

如遇到问题，请检查：
1. 是否为超级管理员
2. 是否正确引入 JS 文件
3. 浏览器控制台是否有错误
4. Network 面板查看 API 请求状态

---

**文档创建时间**: 2026-03-26  
**最后更新**: 2026-03-26  
**维护者**: EIMS 开发团队
