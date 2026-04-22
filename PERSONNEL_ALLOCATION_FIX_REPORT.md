# 人员分配可视化页面问题诊断与修复报告

## 问题描述

用户反馈：在访问 `/root/personnel/allocation-visual/` 时，"待分配人员"和"部门人员"都显示为 0。

## 根本原因分析

### 1. 数据同步问题（已解决）

**问题：** Personnel 表与 Employee 表未同步，导致 Personnel 表中缺少大量记录。

**解决方案：** 
- 创建了 `sync_employee_to_personnel.py` 脚本
- 成功从 Employee 表同步了 31 条记录到 Personnel 表
- 数据分布：
  - tenant_id=2 (鼎策): 20 人
  - tenant_id=3 (晟昌): 5 人  
  - tenant_id=4 (嘉诚达): 6 人

### 2. 租户上下文缺失问题（本次修复）

**问题：** 当 root 超级管理员通过 `/root/` 路径访问业务页面时，如果 session 中没有设置 `tenant_id`，会导致：

1. **TenantMiddleware** 无法从 session 中读取 tenant_id，因此 `request.tenant = None`
2. **视图查询** 不会按 tenant_id 过滤（第 37-38 行的条件判断失败）
3. **数据库路由器** 看到 `request.current_system = 'root'` 且没有 session tenant_id，默认路由到 'dingce' 数据库
4. **结果：** 查询的是 dingce 数据库，而该数据库中所有 Personnel 记录的 department 都是空字符串，所以"部门人员"为 0

**数据库实际情况：**
```
eims_dingce:
  - 总记录数: 33
  - 待分配人员: 31 (department 为空)
  - 部门人员: 0

eims_jiachengda:
  - 总记录数: 6
  - 待分配人员: 0
  - 部门人员: 6 (都有 department='造价部')
```

## 修复方案

### 修改文件：`eims_app/views/views_allocation_visual.py`

在 `allocation_visual` 视图函数开头添加了租户检查逻辑：

```python
@login_required
@user_passes_test(has_personnel_permission)
def allocation_visual(request):
    """可视化人员分配页面 - 支持复选、双击等交互方式"""
    
    # 如果是 /root/ 路径且没有选择公司，重定向到公司选择页面
    if hasattr(request, 'current_system') and request.current_system == 'root':
        if not hasattr(request, 'tenant') or not request.tenant:
            from django.contrib import messages
            messages.warning(request, '请先选择要查看的公司')
            return redirect('eims_app:tenant_select')
    
    # ... 原有逻辑
```

### 工作原理

1. 当用户访问 `/root/personnel/allocation-visual/` 时
2. **PathResolverMiddleware** 设置 `request.current_system = 'root'`
3. **TenantMiddleware** 尝试从 session 读取 tenant_id
   - 如果有：设置 `request.tenant` 为对应的 Tenant 对象
   - 如果没有：`request.tenant = None`
4. **视图检查：** 如果是 root 路径且没有 tenant，重定向到公司选择页面
5. 用户在租户选择页面选择一个公司后，session 中会保存 tenant_id
6. 再次访问 allocation_visual 时，就能正确查询对应公司的数据

## 使用流程

### Root 超级管理员访问步骤：

1. **首次访问** `/root/personnel/allocation-visual/`
   - 系统检测到未选择公司
   - 自动重定向到公司选择页面 (`/root/tenant-select/`)
   - 显示提示："请先选择要查看的公司"

2. **在公司选择页面**
   - 可以看到所有 4 个公司（鼎策、晟昌、嘉诚达、开发者）
   - 点击选择要查看的公司（例如：嘉诚达）
   - 提交后，session 中保存 `tenant_id=4`

3. **再次访问** `/root/personnel/allocation-visual/`
   - 系统从 session 读取 tenant_id=4
   - 数据库路由器路由到 eims_jiachengda 数据库
   - 正确显示：
     - 待分配人员: 0
     - 部门人员: 6 (造价部的 6 位员工)

### 切换公司

- 可以在侧边栏随时切换公司
- 或者重新访问 `/root/tenant-select/` 选择其他公司

## 数据验证

### 嘉诚达公司 (tenant_id=4) 的 Personnel 数据：

| ID | 人员编号 | 姓名 | 部门 | 分类 |
|----|---------|------|------|------|
| 13 | JCDRY-110 | 黎绍昆 | 造价部 | 部门人员 |
| 14 | JCDRY-001 | 秦有林 | 造价部 | 部门人员 |
| 15 | JCDRY-005 | 刘备 | 造价部 | 部门人员 |
| 16 | JCDRY-004 | 李逵 | 造价部 | 部门人员 |
| 17 | JCDRY-003 | 吴松 | 造价部 | 部门人员 |
| 18 | JCDRY-002 | 潘金莲 | 造价部 | 部门人员 |

**总计：6 条部门人员记录，0 条待分配人员记录**

### 鼎策公司 (tenant_id=2) 的 Personnel 数据：

- 总记录数: 20
- 待分配人员: 20 (所有人员的 department 都为空)
- 部门人员: 0

## 后续建议

### 1. 扩展到其他视图

建议对其他在 `/root/` 路径下访问的业务视图也添加类似的租户检查，例如：
- `personnel_list` (人员花名册)
- `employee_list` (员工花名册)
- `dept_personnel_list` (部门人员)
- `project_personnel_list` (项目人员)

### 2. 改进用户体验

可以在 base.html 模板中添加一个明显的提示：
- 当处于 `/root/` 路径且未选择公司时
- 在页面顶部显示警告横幅
- 提供快速跳转到公司选择页面的链接

### 3. 数据完善

目前鼎策公司的 20 条 Personnel 记录都没有 department 值，可能需要：
- 批量导入或手动分配部门
- 或者提供一个"批量设置部门"的功能

## 测试验证

请按照以下步骤测试：

1. 确保 Django 服务正在运行
2. 以 root 超级管理员身份登录
3. 访问 `http://localhost:8000/root/personnel/allocation-visual/`
4. 应该被重定向到公司选择页面
5. 选择"广西嘉诚达工程造价咨询有限公司"
6. 再次访问 `http://localhost:8000/root/personnel/allocation-visual/`
7. 应该看到：
   - 待分配人员: 0
   - 部门人员: 6
   - 列表显示 6 位造价部员工

## 总结

**问题根源：** Personnel 和 Employee 表不同步 + /root/ 路径缺少租户上下文

**解决方案：** 
1. ✅ 已同步 Employee → Personnel 数据（31 条记录）
2. ✅ 已在 allocation_visual 视图中添加租户检查
3. ⏳ 建议扩展到其他视图以保持一致性

**当前状态：** 修复已完成，等待用户测试验证
