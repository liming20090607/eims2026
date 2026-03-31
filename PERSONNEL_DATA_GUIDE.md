# 人员花名册数据补充指南

## 🔍 问题诊断

### 当前数据状态
```
总记录数：37
未删除记录：11
实际可用人员：6 人（去除测试数据）
```

### 异常测试数据
```
ID:36 - 姓名:"4" (陆军学院老旧小区改造项目)
ID:35 - 姓名:"J" (无项目)
ID:34 - 姓名:"G" (无项目)
ID:33 - 姓名:"E" (无项目)
ID:32 - 姓名:"C" (无项目)
```

### 真实人员数据
```
唐昌罗、唐鹏、张中立、秦养付、罗龙辉、谢荣明（共 6 人）
```

---

## 📋 解决方案

### 方案一：通过界面添加人员（推荐）

#### 步骤 1：访问人员花名册页面
```
http://127.0.0.1:8000/personnel/
```

#### 步骤 2：点击"添加人员"
- 进入人员添加页面
- 填写完整的人员信息

#### 步骤 3：填写人员信息
**必填字段**：
- ✅ 人员编号（如：RY2026001）
- ✅ 姓名（如：张三）
- ✅ 性别
- ✅ 手机号码
- ✅ 部门（如：工程部）
- ✅ 岗位（如：技术员）

**可选字段**：
- 主要项目（可先不选，后续分配）
- 入岗时间
- 邮箱

#### 步骤 4：批量添加人员
重复步骤 2-3，添加所有需要的人员

---

### 方案二：清理测试数据

#### 清理单字符测试记录

**方法 1：通过 Django Admin（推荐）**

1. 访问 Django Admin：
   ```
   http://127.0.0.1:8000/admin/eims_app/personnel/
   ```

2. 勾选以下异常记录：
   - ID 32 - 姓名 "C"
   - ID 33 - 姓名 "E"
   - ID 34 - 姓名 "G"
   - ID 35 - 姓名 "J"
   - ID 36 - 姓名 "4"

3. 选择"删除选中的项目人员"

**方法 2：通过 Python 脚本清理**

创建清理脚本 `cleanup_test_data.py`：

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Personnel

# 删除单字符姓名的测试数据
test_names = ['C', 'E', 'G', 'J', '4']

print('准备删除以下测试数据:')
for name in test_names:
    count = Personnel.objects.filter(name=name).count()
    print(f'  - 姓名 "{name}": {count} 条记录')
    
    # 删除记录
    deleted, _ = Personnel.objects.filter(name=name).delete()
    print(f'    已删除 {deleted} 条')

print('\n清理完成！')
print(f'剩余记录数：{Personnel.objects.count()}')
print(f'未删除记录数：{Personnel.objects.filter(is_deleted=False).count()}')
```

运行脚本：
```bash
python cleanup_test_data.py
```

---

### 方案三：从 Employee 导入数据（快速补充）

如果 Employee 表中有完整的员工数据，可以快速导入到 Personnel 表。

#### 步骤 1：检查 Employee 表数据

```bash
python manage.py shell -c "from eims_app.models import Employee; print(f'Employee 表有 {Employee.objects.count()} 条记录')"
```

#### 步骤 2：批量导入员工到 Personnel

创建导入脚本 `import_employees_to_personnel.py`：

```python
import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Employee, Personnel
from django.utils import timezone

print('=' * 80)
print('从 Employee 导入数据到 Personnel')
print('=' * 80)

# 获取所有未离职员工
employees = Employee.objects.filter(
    is_deleted=False,
    leave_time__isnull=True  # 未离职
)

print(f'\n找到 {employees.count()} 名在职员工')

created_count = 0
skipped_count = 0

for emp in employees:
    # 检查是否已存在于 Personnel 表
    exists = Personnel.objects.filter(
        employee=emp,
        is_deleted=False
    ).exists()
    
    if exists:
        skipped_count += 1
        print(f'  跳过：{emp.name}（已在 Personnel 表中）')
        continue
    
    # 创建 Personnel 记录
    personnel = Personnel.objects.create(
        employee=emp,
        personnel_code=f'RY{emp.employee_code.replace("EMP", "")}',
        name=emp.name,
        gender=emp.gender,
        department='',  # 后续分配
        position='',    # 后续分配
        phone=emp.mobile,
        email=None,
        entry_time=emp.entry_time,  # 使用入职时间作为入岗时间
        is_deleted=False,
        operator='system_import',
        remark=f'从 Employee 表导入，员工编号：{emp.employee_code}'
    )
    
    created_count += 1
    print(f'  ✓ 导入：{emp.name} -> {personnel.personnel_code}')

print('\n' + '=' * 80)
print(f'导入完成！')
print(f'  新增：{created_count} 人')
print(f'  跳过：{skipped_count} 人')
print(f'\nPersonnel 表现在总记录数：{Personnel.objects.count()}')
print(f'Personnel 表未删除记录数：{Personnel.objects.filter(is_deleted=False).count()}')
```

运行脚本：
```bash
python import_employees_to_personnel.py
```

---

## 🎯 推荐操作流程

### 第一阶段：清理测试数据（5 分钟）
1. ✅ 运行清理脚本删除测试数据
2. ✅ 验证剩余人员数据

### 第二阶段：导入现有员工（5 分钟）
1. ✅ 检查 Employee 表数据
2. ✅ 运行导入脚本
3. ✅ 验证导入结果

### 第三阶段：手动补充人员（10-30 分钟）
1. ✅ 访问人员花名册页面
2. ✅ 添加未包含在 Employee 表中的项目人员
3. ✅ 为每个人分配项目和岗位

### 第四阶段：验证（5 分钟）
1. ✅ 访问项目台账页面
2. ✅ 点击"添加项目人员"
3. ✅ 检查姓名下拉列表是否包含所有人员

---

## 📊 验证脚本

创建验证脚本 `verify_personnel_dropdown.py`：

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Personnel

print('=' * 80)
print('人员下拉列表数据验证')
print('=' * 80)

# 模拟视图中的查询
personnel_names = Personnel.objects.filter(
    is_deleted=False
).order_by('name').values_list('name', flat=True).distinct()

print(f'\n下拉列表将显示 {personnel_names.count()} 人:')
print('-' * 80)

for idx, name in enumerate(personnel_names, 1):
    print(f'{idx:3d}. {name}')

print(f'\n总计：{personnel_names.count()} 人')
print('=' * 80)
```

运行验证：
```bash
python verify_personnel_dropdown.py
```

---

## 🔧 快速命令

### 检查 Personnel 表数据
```bash
python check_personnel_data.py
```

### 清理测试数据
```bash
python cleanup_test_data.py
```

### 从 Employee 导入
```bash
python import_employees_to_personnel.py
```

### 验证下拉列表
```bash
python verify_personnel_dropdown.py
```

---

## 📝 注意事项

### 1. 数据质量
- ✅ 确保姓名至少 2 个字符（中文）
- ✅ 人员编号唯一
- ✅ 手机号码格式正确
- ✅ 排除已离职人员

### 2. 导入顺序
1. 先清理测试数据
2. 再从 Employee 导入
3. 最后手动补充

### 3. 后续维护
- 新员工入职时，先创建 Employee 记录
- 分配到项目时，创建 Personnel 记录
- 离职时，同时标记 Employee 和 Personnel 为已删除

---

## 🎓 最佳实践

### 人员编号规则
```
RY + 年份 + 序号
例：RY2026001, RY2026002
```

### 部门命名规范
```
工程部、技术部、生产部、安全部、质量部、物资部、综合部
```

### 岗位命名规范
```
项目经理、项目总工、技术员、施工员、安全员、质量员、材料员、资料员
```

---

## 📞 需要帮助？

如果在数据补充过程中遇到问题，请检查：
1. Django Admin 后台数据
2. 浏览器控制台错误
3. 服务器日志

---

**文档版本**: 1.0  
**创建时间**: 2026-03-28  
**适用系统**: EIMS2026
