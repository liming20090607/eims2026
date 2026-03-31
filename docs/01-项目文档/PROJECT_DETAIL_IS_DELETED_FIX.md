# ProjectDetail 模型 is_deleted 字段错误修复

## 🐛 问题描述

访问项目详情页时出现 `FieldError`：

```
Cannot resolve keyword 'is_deleted' into field. 
Choices are: actual_extension_status, actual_start_date, ..., created_at, ..., updated_at
```

**错误位置**: `eims_app/views/views_project_ledger.py` 第 167-174 行

---

## 🔍 根本原因

### **问题分析**

在 `project_ledger_detail` 视图中，尝试使用 `is_deleted` 字段过滤项目：

```python
# ❌ 错误的代码
prev_project = ProjectDetail.objects.filter(
    Q(id__lt=pk) | Q(id__gt=pk),
    is_deleted=False  # ← ProjectDetail 模型没有这个字段！
).order_by('-id').first()
```

### **模型检查**

查看 `ProjectDetail` 模型定义（`eims_app/models/model_project_detail.py`）：

```python
class ProjectDetail(models.Model):
    # ... 其他字段 ...
    
    # 时间字段
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)
    
    # ❌ 没有 is_deleted 字段！
```

**对比其他模型**：

- ✅ `Personnel` 模型有 `is_deleted` 字段
- ✅ `MonthlyReport` 模型有 `is_deleted` 字段
- ❌ `ProjectDetail` 模型**没有** `is_deleted` 字段

---

## ✅ 解决方案

### **修复代码**

移除对 `is_deleted` 的引用，因为 `ProjectDetail` 不支持软删除：

**修改前**:
```python
from django.db.models import Q

prev_project = ProjectDetail.objects.filter(
    Q(id__lt=pk) | Q(id__gt=pk),
    is_deleted=False  # ❌ 错误
).order_by('-id').first()

next_project = ProjectDetail.objects.filter(
    Q(id__gt=pk) | Q(id__lt=pk),
    is_deleted=False  # ❌ 错误
).order_by('id').first()
```

**修改后**:
```python
from django.db.models import Q

prev_project = ProjectDetail.objects.filter(
    id__lt=pk  # ✅ 只查找 ID 小于当前 ID 的项目
).order_by('-id').first()

next_project = ProjectDetail.objects.filter(
    id__gt=pk  # ✅ 只查找 ID 大于当前 ID 的项目
).order_by('id').first()
```

---

## 📊 逻辑说明

### **为什么这样修改？**

#### **原逻辑（有问题）**
```python
# 试图查找所有其他项目（排除自己），然后取第一个
Q(id__lt=pk) | Q(id__gt=pk)  # 除了自己之外的所有项目
```

**问题**:
- ❌ 条件 `Q(id__lt=pk) | Q(id__gt=pk)` 会匹配除当前项目外的**所有**项目
- ❌ 对于 `prev_project`，应该只找 ID **小于** 当前 ID 的项目
- ❌ 对于 `next_project`，应该只找 ID **大于** 当前 ID 的项目

#### **新逻辑（正确）**
```python
# prev_project: 查找 ID 小于当前 ID 的项目中，ID 最大的那个
id__lt=pk  # ID < pk
.order_by('-id').first()  # 按 ID 降序排列，取第一个

# next_project: 查找 ID 大于当前 ID 的项目中，ID 最小的那个
id__gt=pk  # ID > pk
.order_by('id').first()  # 按 ID 升序排列，取第一个
```

**效果**:
- ✅ `prev_project`: 当前项目的**上一个**项目（ID 比当前小，但最接近当前）
- ✅ `next_project`: 当前项目的**下一个**项目（ID 比当前大，但最接近当前）

---

## 🎯 示例说明

假设有以下项目 ID：`[1, 3, 5, 8, 10]`

### **访问项目 ID=5**

**prev_project 查询**:
```python
ProjectDetail.objects.filter(id__lt=5).order_by('-id').first()
# 结果：ID=3 （小于 5 的最大 ID）
```

**next_project 查询**:
```python
ProjectDetail.objects.filter(id__gt=5).order_by('id').first()
# 结果：ID=8 （大于 5 的最小 ID）
```

### **访问项目 ID=1（第一个）**

**prev_project 查询**:
```python
ProjectDetail.objects.filter(id__lt=1).order_by('-id').first()
# 结果：None （没有更小的 ID）
```

**next_project 查询**:
```python
ProjectDetail.objects.filter(id__gt=1).order_by('id').first()
# 结果：ID=3
```

### **访问项目 ID=10（最后一个）**

**prev_project 查询**:
```python
ProjectDetail.objects.filter(id__lt=10).order_by('-id').first()
# 结果：ID=8
```

**next_project 查询**:
```python
ProjectDetail.objects.filter(id__gt=10).order_by('id').first()
# 结果：None （没有更大的 ID）
```

---

## 💡 技术要点

### **1. 软删除模式的使用**

不同模型对软删除的支持不同：

```python
# ✅ 支持软删除的模型
class Personnel(models.Model):
    is_deleted = models.BooleanField(default=False)
    
# ❌ 不支持软删除的模型
class ProjectDetail(models.Model):
    # 没有 is_deleted 字段
    pass
```

**最佳实践**:
- 在使用任何字段前，先确认模型是否支持
- 不要假设所有模型都有相同的辅助字段

### **2. 相邻记录查询模式**

获取上一条/下一条记录的通用模式：

```python
# 上一条记录
prev_obj = Model.objects.filter(
    id__lt=current_id
).order_by('-id').first()

# 下一条记录
next_obj = Model.objects.filter(
    id__gt=current_id
).order_by('id').first()
```

**关键点**:
- `id__lt`: 小于当前 ID
- `id__gt`: 大于当前 ID
- `order_by('-id')`: 降序排列（从大到小）
- `order_by('id')`: 升序排列（从小到大）
- `.first()`: 取第一条记录

### **3. Q 对象的正确使用**

当需要复杂条件时使用 `Q` 对象：

```python
from django.db.models import Q

# ✅ 正确：多个条件 OR
Model.objects.filter(Q(field1=value1) | Q(field2=value2))

# ✅ 正确：多个条件 AND
Model.objects.filter(Q(field1=value1) & Q(field2=value2))

# ✅ 更好：简单 AND 可以省略 Q
Model.objects.filter(field1=value1, field2=value2)
```

在本例中，由于我们只需要简单的 `id__lt` 或 `id__gt` 条件，不需要 `Q` 对象的复杂逻辑，所以可以直接使用字段查找。

---

## 🧪 测试验证

### **测试场景 1: 中间项目**

**步骤**:
1. 访问项目 ID=5
2. 查看导航按钮

**预期**:
- ✅ "上一个项目" 指向 ID=3
- ✅ "下一个项目" 指向 ID=8

---

### **测试场景 2: 第一个项目**

**步骤**:
1. 访问项目 ID=1
2. 查看导航按钮

**预期**:
- ✅ "上一个项目" 按钮禁用（显示"没有上一个项目"）
- ✅ "下一个项目" 指向 ID=3

---

### **测试场景 3: 最后一个项目**

**步骤**:
1. 访问项目 ID=10
2. 查看导航按钮

**预期**:
- ✅ "上一个项目" 指向 ID=8
- ✅ "下一个项目" 按钮禁用（显示"没有下一个项目"）

---

### **测试场景 4: 唯一项目**

**步骤**:
1. 系统中只有 ID=1 一个项目
2. 访问该项目

**预期**:
- ✅ "上一个项目" 按钮禁用
- ✅ "下一个项目" 按钮禁用

---

## 📝 相关修改

### **文件清单**

1. **views_project_ledger.py** (已修复)
   - 函数：`project_ledger_detail`
   - 修改：移除 `is_deleted` 条件
   - 优化：简化查询逻辑

2. **detail.html** (无需修改)
   - 模板已经正确处理了 `None` 值
   - 当 `prev_project` 或 `next_project` 为 `None` 时，显示禁用的按钮

---

## ✅ 完成状态

- ✅ 移除了对 `is_deleted` 字段的引用
- ✅ 简化了查询逻辑（更清晰）
- ✅ 保持了原有功能（上一个/下一个导航）
- ✅ 代码更易读和维护

---

## 💡 后续建议

### **1. 统一软删除策略**

考虑为所有主要模型添加一致的软删除支持：

```python
# 方案 A: 为 ProjectDetail 添加 is_deleted
class ProjectDetail(models.Model):
    # ... existing fields ...
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    
    class Meta:
        base_manager_name = 'all_objects'
        default_manager_name = 'objects'
    
    all_objects = models.Manager()  # 包含已删除
    objects = models.Manager()  # 默认管理器（未来可加过滤）
```

**优点**:
- ✅ 统一的删除策略
- ✅ 便于数据恢复
- ✅ 审计追踪

**缺点**:
- ⚠️ 需要数据库迁移
- ⚠️ 所有查询都需要考虑 `is_deleted`

---

### **2. 添加自定义管理器**

如果将来需要软删除功能，可以添加管理器：

```python
class ProjectDetailManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class ProjectDetail(models.Model):
    # ... fields ...
    is_deleted = models.BooleanField(default=False)
    
    objects = ProjectDetailManager()  # 默认过滤已删除
    all_objects = models.Manager()  # 包含已删除
```

---

### **3. 添加排序选项**

当前按 ID 排序，可以考虑添加更多排序选项：

```python
# 按创建时间排序
prev_project = ProjectDetail.objects.filter(
    created_at__lt=project_detail.created_at
).order_by('-created_at').first()

# 按项目编号排序
prev_project = ProjectDetail.objects.filter(
    project_code__lt=project_detail.project_code
).order_by('-project_code').first()
```

---

**修复完成时间**: 2026-03-26 01:14  
**错误类型**: FieldError - is_deleted field not found  
**修复方式**: 移除不存在的字段引用，简化查询逻辑  
**功能状态**: ✅ 已修复并测试
