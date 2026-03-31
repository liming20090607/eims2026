# Employee vs Personnel 模型对比详解

## 📊 核心区别概览

| 对比维度 | Employee（员工） | Personnel（人员） |
|---------|------------------|-------------------|
| **定位** | 员工基本信息库 | 项目人员分配记录 |
| **用途** | 入职登记、人事档案 | 项目分配、岗位管理 |
| **数据性质** | 静态基础信息 | 动态分配信息 |
| **一对一多** | 一人一条记录 | 一人多条记录（可分配多个项目） |
| **关联关系** | 被 Personnel 关联 | 关联到 Employee |
| **使用场景** | 员工入职、离职管理 | 项目人员调配、岗位安排 |

---

## 👤 Employee 模型 - 员工基本信息

### 📝 模型定义
**文件**: `e:\EIMS2026\eims_app\models\model_employee.py`

**中文名**: 员工信息  
**用途**: 存储员工的基本信息、入职登记

### 🔑 核心字段

#### 1. 唯一标识
```python
employee_code = CharField(unique=True)  # 员工编号（唯一）
```

#### 2. 个人基本信息
```python
name = CharField()              # 姓名
gender = SmallIntegerField()    # 性别（男/女/其他）
id_card = CharField()           # 身份证号（18 位）
native_place = CharField()      # 籍贯
ethnic = CharField()            # 民族（汉/回/满/蒙古/藏/维吾尔/其他）
education = CharField()         # 学历（小学/初中/高中/大专/本科/硕士/博士）
```

#### 3. 联系方式
```python
address = CharField()           # 住址
home_phone = CharField()        # 固定电话
mobile = CharField()            # 手机号
emergency_contact = CharField() # 应急联系人
emergency_phone = CharField()   # 应急电话
wechat = CharField()            # 微信号
```

#### 4. 职务信息
```python
admin_position = CharField()        # 行政职务
tech_position = CharField()         # 技术职务
professional_qualification = CharField()  # 执业资格
professional_title = CharField()    # 职称
job_qualification = CharField()     # 任职资格
```

#### 5. 入职信息
```python
entry_time = DateField()    # 入职时间
leave_time = DateField()    # 离职时间
```

### 🎯 使用场景

#### 1. 员工入职登记
**视图**: `views_employee.employee_add()`  
**模板**: `employee/add.html`  
**表单**: `EmployeeForm`

```python
# eims_app\views\views_employee.py
def employee_add(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.operator = request.user.username
            employee.save()
            messages.success(request, "员工信息添加成功！")
            return redirect("eims_app:employee_list")
```

#### 2. 员工信息管理（列表/详情/编辑/删除）
**路由**:
```python
path('employee/', employee_list, name='employee_list'),
path('employee/add/', employee_add, name='employee_add'),
path('employee/<int:pk>/', employee_detail, name='employee_detail'),
path('employee/<int:pk>/edit/', employee_edit, name='employee_edit'),
path('employee/<int:pk>/delete/', employee_delete, name='employee_delete'),
```

**管理页面**: `employee/list.html`

#### 3. 批量删除
**路由**: `path('employee/batch-delete/', employee_batch_delete, name='employee_batch_delete')`

### 📊 数据特点

- **一人一记录**: 每个员工只有一条记录
- **唯一编号**: `employee_code` 字段唯一
- **完整信息**: 包含员工的全面信息
- **相对静态**: 信息变更频率较低
- **人事管理**: 由 HR 部门维护

---

## 📋 Personnel 模型 - 项目人员分配

### 📝 模型定义
**文件**: `e:\EIMS2026\eims_app\models\model_personnel.py`

**中文名**: 项目人员  
**用途**: 存储员工在项目中的分配信息

### 🔑 核心字段

#### 1. 关联员工（可选）
```python
employee = ForeignKey('Employee', on_delete=models.CASCADE, 
                     null=True, blank=True, verbose_name='员工')
```
**说明**: 
- 可选关联到 Employee
- 可以为空（允许非员工的项目人员）
- 级联删除

#### 2. 基本信息（简化）
```python
personnel_code = CharField()  # 人员编号
name = CharField()            # 姓名
gender = SmallIntegerField()  # 性别
```

#### 3. 项目分配（支持一人多项目）
```python
# 主要项目（可选）
project = ForeignKey('ProjectDetail', null=True, blank=True, 
                    verbose_name='主要项目')
project_code = CharField()    # 项目编号

# 额外项目 2-5（支持一人最多 5 个项目）
project2 = ForeignKey('ProjectDetail', null=True, blank=True)
project_code2 = CharField()

project3 = ForeignKey('ProjectDetail', null=True, blank=True)
project_code3 = CharField()

project4 = ForeignKey('ProjectDetail', null=True, blank=True)
project_code4 = CharField()

project5 = ForeignKey('ProjectDetail', null=True, blank=True)
project_code5 = CharField()
```

#### 4. 部门与岗位
```python
department = CharField()   # 部门
position = CharField()     # 岗位
```

#### 5. 项目相关联系方式
```python
phone = CharField()        # 手机号码
email = EmailField()       # 邮箱
```

#### 6. 项目时间
```python
entry_time = DateField()   # 入岗时间
leave_time = DateField()   # 离岗时间
```

### 🎯 使用场景

#### 1. 人员花名册管理
**视图**: `views_personnel.personnel_add()`  
**模板**: `personnel/add.html`  
**表单**: `PersonnelForm`

**路由**:
```python
path('personnel/', views_personnel.personnel_list, name='personnel_list'),
path('personnel/add/', views_personnel.personnel_add, name='personnel_add'),
path('personnel/<int:pk>/', views_personnel.personnel_detail, name='personnel_detail'),
```

#### 2. 项目人员分配（可视化）
**视图**: `views_allocation_visual.allocation_visual()`  
**模板**: `personnel/allocation_visual.html`

**功能**:
- 将人员分配到项目（支持一人多项目）
- 分配到部门
- 召回人员
- 更新分配信息

**AJAX 接口**:
```python
# eims_app\views\views_allocation_visual.py
def allocate_personnel_ajax(request):
    """分配人员到项目"""
    data = json.loads(request.body)
    personnel_ids = data.get('personnel_ids', [])
    
    for pid in personnel_ids:
        personnel = Personnel.objects.get(pk=pid)
        # 更新项目分配
        personnel.project = project
        personnel.position = position
        personnel.save()
```

#### 3. 项目台账 - 添加项目人员
**视图**: `views_project.add_personnel()`  
**模板**: `project_ledger/add_personnel.html`

**特殊用途**: 为项目添加各岗位人员（总监、总代、土建专监等 8 个岗位）

```python
# eims_app\views\views_project.py
def add_personnel(request, pk):
    project = get_object_or_404(ProjectDetail, pk=pk)
    
    # 从 Personnel 表获取所有姓名（人员花名册）
    personnel_names = Personnel.objects.filter(
        is_deleted=False
    ).order_by('name').values_list('name', flat=True).distinct()
    
    # 创建项目人员记录
    for position_key, position_name in positions:
        if has_change and name:
            personnel = Personnel(
                personnel_code=personnel_code,
                project=project,
                name=name,
                position=position_name,
                # ...
            )
            personnel.save()
```

#### 4. 人员分配管理
**模型**: `PersonnelAllocation`  
**文件**: `model_personnel_detail.py`

记录每次分配的详细信息：
```python
class PersonnelAllocation(BaseModel):
    allocation_code = CharField(unique=True)  # 分配编号
    personnel = ForeignKey('Personnel')       # 被分配人员
    from_project = ForeignKey('ProjectDetail', related_name='from_projects')
    to_project = ForeignKey('ProjectDetail', related_name='to_projects')
    allocation_position = CharField()         # 分配岗位
    allocation_department = CharField()       # 分配部门
    allocation_date = DateField()             # 分配日期
    allocation_status = CharField()           # 分配状态（已分配/待分配/已召回/已调动）
```

### 📊 数据特点

- **一人多记录**: 同一个员工可以有多条 Personnel 记录（分配不同项目）
- **非唯一编号**: `personnel_code` 不唯一（不同项目可以有相同人员）
- **简化信息**: 只保留项目相关的必要信息
- **高度动态**: 随项目调配频繁变更
- **项目管理**: 由项目管理部门维护

---

## 🔄 两个模型的关系

### 关系图
```
Employee (员工基本信息)
    ↓ (1 对多，可选关联)
Personnel (项目人员分配)
    ↓ (多 对 多，通过 PersonnelAllocation)
ProjectDetail (项目)
```

### 关联示例

#### 场景：张三的项目分配
```python
# 1. Employee 表 - 张三的基本信息（只有 1 条记录）
employee = Employee.objects.get(employee_code='EMP001')
# employee.name = '张三'
# employee.mobile = '13800138000'
# employee.education = '本科'

# 2. Personnel 表 - 张三的项目分配（可以有多条记录）
personnel1 = Personnel.objects.create(
    employee=employee,
    name='张三',
    project=project_A,  # 项目 A
    position='技术员',
    department='工程部'
)

personnel2 = Personnel.objects.create(
    employee=employee,
    name='张三',
    project=project_B,  # 项目 B（同时参与另一个项目）
    position='施工员',
    department='生产部'
)

# 3. PersonnelAllocation 表 - 分配记录（详细历史）
allocation1 = PersonnelAllocation.objects.create(
    personnel=personnel1,
    from_project=None,
    to_project=project_A,
    allocation_position='技术员',
    allocation_status='allocated'
)
```

### 查询示例

#### 1. 查询某员工的所有项目分配
```python
employee = Employee.objects.get(employee_code='EMP001')
personnel_records = Personnel.objects.filter(employee=employee)
# 返回该员工在所有项目中的分配记录
```

#### 2. 查询某项目的所有人员
```python
project = ProjectDetail.objects.get(project_code='PROJ001')
personnel_list = Personnel.objects.filter(project=project)
# 返回该项目的所有人员
```

#### 3. 查询某项目的所有员工基本信息
```python
project = ProjectDetail.objects.get(project_code='PROJ001')
employees = Employee.objects.filter(
    project_assignments__project=project
).distinct()
# 通过 related_name='project_assignments' 反向查询
```

---

## 🎯 实际应用场景对比

### 场景 1：新员工入职

**步骤**:
1. **创建 Employee 记录**（HR 操作）
   ```python
   employee = Employee.objects.create(
       employee_code='EMP2026001',
       name='李四',
       gender=0,
       mobile='13900139000',
       education='硕士',
       entry_time='2026-03-01'
   )
   ```

2. **分配到项目时创建 Personnel 记录**（项目管理操作）
   ```python
   personnel = Personnel.objects.create(
       employee=employee,
       name='李四',
       project=project_A,
       position='工程师',
       department='技术部',
       entry_time='2026-03-01'
   )
   ```

### 场景 2：员工调动项目

**只更新 Personnel，不修改 Employee**:
```python
# 错误做法 ❌
employee.project = new_project  # Employee 没有 project 字段！

# 正确做法 ✅
personnel = Personnel.objects.get(pk=personnel_id)
personnel.project = new_project
personnel.position = new_position
personnel.save()

# 创建分配记录
PersonnelAllocation.objects.create(
    personnel=personnel,
    from_project=old_project,
    to_project=new_project,
    allocation_status='transferred'
)
```

### 场景 3：一人多项目

**Employee 不变，创建多个 Personnel 记录**:
```python
# 员工基本信息（只有 1 条）
employee = Employee.objects.get(pk=1)

# 项目分配（可以有多条）
Personnel.objects.create(
    employee=employee,
    project=project_A,
    position='项目经理'
)

Personnel.objects.create(
    employee=employee,
    project=project_B,
    position='技术负责人'
)

Personnel.objects.create(
    employee=employee,
    project=project_C,
    position='顾问'
)
```

### 场景 4：项目人员下拉列表

**为什么从 Personnel 获取姓名？**

```python
# 错误做法 ❌（之前的实现）
employees = Employee.objects.all()
employee_names = [emp.name for emp in employees]
# 问题：Employee 表可能为空，或者包含未分配到项目的人员

# 正确做法 ✅（当前实现）
personnel_names = Personnel.objects.filter(
    is_deleted=False
).order_by('name').values_list('name', flat=True).distinct()
# 优势：
# 1. 从人员花名册获取，确保人员已分配到项目
# 2. 只获取未删除的记录
# 3. 自动去重（同一人在多个项目只出现一次）
# 4. 按姓名排序
```

---

## 📊 数据库表结构对比

### Employee 表
```sql
CREATE TABLE eims_app_employee (
    id INTEGER PRIMARY KEY,
    employee_code VARCHAR(50) UNIQUE,    -- 唯一编号
    name VARCHAR(50),                     -- 姓名
    gender SMALLINT,                      -- 性别
    id_card VARCHAR(18),                  -- 身份证号
    native_place VARCHAR(100),            -- 籍贯
    ethnic VARCHAR(20),                   -- 民族
    education VARCHAR(20),                -- 学历
    address VARCHAR(200),                 -- 住址
    home_phone VARCHAR(20),               -- 固定电话
    mobile VARCHAR(20),                   -- 手机号
    emergency_contact VARCHAR(50),        -- 应急联系人
    emergency_phone VARCHAR(20),          -- 应急电话
    wechat VARCHAR(50),                   -- 微信
    admin_position VARCHAR(100),          -- 行政职务
    tech_position VARCHAR(100),           -- 技术职务
    professional_qualification VARCHAR(200), -- 执业资格
    professional_title VARCHAR(100),      -- 职称
    job_qualification VARCHAR(200),       -- 任职资格
    entry_time DATE,                      -- 入职时间
    leave_time DATE,                      -- 离职时间
    is_deleted BOOLEAN,                   -- 删除标记
    -- ... 系统字段
);
```

### Personnel 表
```sql
CREATE TABLE eims_app_personnel (
    id INTEGER PRIMARY KEY,
    employee_id INTEGER,                  -- 关联 Employee（可选）
    personnel_code VARCHAR(50),           -- 人员编号
    name VARCHAR(50),                     -- 姓名
    gender SMALLINT,                      -- 性别
    project_id INTEGER,                   -- 主要项目
    project_code VARCHAR(50),             -- 项目编号
    project2_id INTEGER,                  -- 项目 2
    project_code2 VARCHAR(50),
    project3_id INTEGER,                  -- 项目 3
    project_code3 VARCHAR(50),
    project4_id INTEGER,                  -- 项目 4
    project_code4 VARCHAR(50),
    project5_id INTEGER,                  -- 项目 5
    project_code5 VARCHAR(50),
    department VARCHAR(100),              -- 部门
    position VARCHAR(100),                -- 岗位
    phone VARCHAR(20),                    -- 手机号
    email VARCHAR(254),                   -- 邮箱
    entry_time DATE,                      -- 入岗时间
    leave_time DATE,                      -- 离岗时间
    is_deleted BOOLEAN,                   -- 删除标记
    -- ... 系统字段
);
```

---

## 🔍 常见误区

### 误区 1：用 Employee 做项目人员选择
```python
# ❌ 错误
employees = Employee.objects.all()
# 问题：
# 1. Employee 可能包含未分配到项目的人员
# 2. 已离职员工也会显示
# 3. 信息不完整（缺少项目、岗位等）

# ✅ 正确
personnel_names = Personnel.objects.filter(
    is_deleted=False
).values_list('name', flat=True).distinct()
# 优势：
# 1. 只包含已分配的项目人员
# 2. 排除已删除的记录
# 3. 自动去重
```

### 误区 2：在 Employee 中存储项目信息
```python
# ❌ 错误设计
class Employee(models.Model):
    project = ForeignKey('ProjectDetail')  # 不应该在这里！
    
# ✅ 正确设计
class Personnel(models.Model):
    employee = ForeignKey('Employee', null=True, blank=True)
    project = ForeignKey('ProjectDetail')
```

### 误区 3：混淆入职时间和入岗时间
```python
# ❌ 错误使用
employee.entry_time  # 入职时间（公司层面）
personnel.entry_time  # 入岗时间（项目层面）

# ✅ 正确使用
# 新员工 2026-03-01 入职公司
employee.entry_time = '2026-03-01'

# 2026-03-15 分配到项目 A 上岗
personnel.entry_time = '2026-03-15'
```

---

## 📈 设计优势

### 1. 职责分离
- **Employee**: 人事档案管理（HR 负责）
- **Personnel**: 项目人员调配（项目管理负责）

### 2. 灵活性
- 支持一人多项目（最多 5 个）
- 支持非员工的项目人员（external personnel）
- 支持灵活的岗位调整

### 3. 数据完整性
- Employee 信息完整且稳定
- Personnel 信息动态但可追溯
- PersonnelAllocation 记录完整历史

### 4. 查询优化
- 项目人员查询快速（直接查 Personnel）
- 员工项目统计方便（通过关联查询）
- 历史记录完整（PersonnelAllocation）

---

## 🎓 最佳实践

### 1. 何时使用 Employee
- ✅ 员工入职登记
- ✅ 人事档案管理
- ✅ 员工信息统计
- ✅ 办理社保公积金
- ✅ 发放工资福利

### 2. 何时使用 Personnel
- ✅ 项目人员分配
- ✅ 项目岗位安排
- ✅ 项目考勤管理
- ✅ 项目绩效考核
- ✅ 人员调配统计

### 3. 数据同步
```python
# 当 Employee 的姓名变更时，同步更新 Personnel
def update_employee_name(employee, new_name):
    employee.name = new_name
    employee.save()
    
    # 同步更新所有项目分配记录
    Personnel.objects.filter(employee=employee).update(
        name=new_name
    )
```

### 4. 级联处理
```python
# 员工离职时
def employee_leave(employee):
    employee.leave_time = timezone.now()
    employee.is_deleted = True
    employee.save()
    
    # 从所有项目召回（不删除 Personnel 记录）
    Personnel.objects.filter(employee=employee).update(
        leave_time=timezone.now(),
        is_deleted=True
    )
```

---

## 📊 总结对比表

| 特性 | Employee | Personnel |
|------|----------|-----------|
| **中文名** | 员工信息 | 项目人员 |
| **定位** | 人事档案 | 项目分配 |
| **记录数量** | 一人一条 | 一人多条（多项目） |
| **编号唯一性** | employee_code 唯一 | personnel_code 不唯一 |
| **关联项目** | ❌ 不直接关联 | ✅ 直接关联（最多 5 个） |
| **字段详细度** | 详细（20+ 字段） | 简化（10+ 字段） |
| **变更频率** | 低（相对稳定） | 高（随项目调配） |
| **管理部门** | HR/人事 | 项目管理部 |
| **典型操作** | 入职、离职、转正 | 分配、调动、召回 |
| **数据来源** | 入职登记表 | 人员花名册 |
| **下拉列表** | ❌ 不用于项目选择 | ✅ 用于项目人员选择 |

---

**文档版本**: 1.0  
**更新时间**: 2026-03-28  
**适用系统**: EIMS2026
