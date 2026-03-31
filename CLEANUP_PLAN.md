# EIMS 废弃模块清理方案

## 📋 清理目标

根据项目文档《侧边栏菜单权限管理_使用说明.md》，以下模块已在重构中被标记为"已删除"，但代码中仍有残留：

1. ❌ **信息收集模块** (InfoCollect)
2. ❌ **产值回款模块** (OutputPayment)  
3. ❌ **质安检查/巡检管理模块** (Inspection)

---

## 🗂️ 需要删除的文件清单

### 1. 信息收集模块 (InfoCollect)

#### 模型文件
- `eims_app/models/model_info_collect.py`

#### 视图文件
- `eims_app/views/views_info_collect.py`

#### 表单文件
- `eims_app/forms/form_info_collect.py`

#### 模板文件
- `eims_app/templates/info_collect/` (整个文件夹)
  - info_collect_add.html
  - info_collect_delete.html
  - info_collect_detail.html
  - info_collect_edit.html
  - info_collect_list.html

#### 迁移文件
- `eims_app/migrations/0001_initial.py` (部分代码，需编辑而非删除)

---

### 2. 产值回款模块 (OutputPayment)

#### 模型文件
- `eims_app/models/model_output_payment.py`

#### 视图文件
- `eims_app/views/views_output_payment.py`

#### 表单文件
- `eims_app/forms/form_output_payment.py`

#### 模板文件
- `eims_app/templates/output_payment/` (整个文件夹)

#### 迁移文件
- `eims_app/migrations/0001_initial.py` (部分代码，需编辑而非删除)

---

### 3. 质安检查/巡检管理模块 (Inspection)

#### 模型文件
- `eims_app/models/model_inspection.py`

#### 视图文件
- `eims_app/views/views_inspect.py`

#### 表单文件
- `eims_app/forms/form_inspection.py`

#### 模板文件
- `eims_app/templates/inspect/` (整个文件夹)
  - inspect_add.html
  - inspect_delete.html
  - inspect_detail.html
  - inspect_edit.html
  - inspect_list.html

#### 迁移文件
- `eims_app/migrations/0001_initial.py` (部分代码，需编辑而非删除)

---

## 🔧 需要修改的代码文件

### 1. `eims_app/models/__init__.py`
**删除导入**:
```python
from .model_output_payment import OutputPayment
from .model_inspection import Inspection
from .model_info_collect import InfoCollect
```

**删除导出**:
```python
'OutputPayment',
'Inspection',
'InfoCollect',
```

### 2. `eims_app/forms/__init__.py`
**删除导入**:
```python
from .form_output_payment import OutputPaymentForm
from .form_inspection import InspectionForm
from .form_info_collect import CollectForm
```

### 3. `eims_app/urls.py`
**删除路由导入**:
```python
from .views import views_output_payment
from .views import views_inspect
from .views import views_info_collect
```

**删除路由配置**:
```python
# 产值回款路由
path('output_payment/', views_output_payment.output_list, name='output_payment_list'),
path('output_payment/add/', views_output_payment.output_add, name='output_payment_add'),
# ... 其他 output_payment 路由

# 质安检查路由
path('inspection/', views_inspect.inspect_list, name='inspection_list'),
# ... 其他 inspection 路由

# 信息收集路由
path('info_collect/', views_info_collect.collect_list, name='info_collect_list'),
# ... 其他 info_collect 路由
```

### 4. `eims_app/templatetags/sidebar_tags.py`
**删除菜单项**:
```python
{
    'id': 'output_payment',
    'url': reverse('output_payment_list'),
    'text': '产值回款',
    'icon': 'bi-cash-coin',
    'permission': 'eims_app.view_output_payment'
},
{
    'id': 'inspection',
    'url': reverse('inspection_list'),
    'text': '巡检管理',
    'icon': 'bi-binoculars',
    'permission': 'eims_app.view_inspection'
},
{
    'id': 'info_collect',
    'url': reverse('info_collect_list'),
    'text': '信息收集',
    'icon': 'bi-collection',
    'permission': 'eims_app.view_info_collect'
},
```

### 5. `staticfiles/js/menu_config.js`
**删除菜单配置**:
```javascript
{
  id: 'output_payment',
  path: '/output_payment/',
  text: '产值回款',
  icon: '<i class="bi bi-cash-coin"></i>',
  permission: 'view_output_payment',
  order: 5
},
{
  id: 'inspection',
  path: '/inspection/',
  text: '巡检管理',
  icon: '<i class="bi bi-binoculars"></i>',
  permission: 'view_inspection',
  order: 6
},
{
  id: 'info_collect',
  path: '/info_collect/',
  text: '信息收集',
  icon: '<i class="bi bi-collection"></i>',
  permission: 'view_info_collect',
  order: 7
},
```

### 6. `eims_app/templatetags/permission_tags.py`
**删除权限映射**:
```python
PERMISSION_MAPPING = {
    'output_payment': ['eims_app.view_output_payment'],
    'inspection': ['eims_app.view_inspection'],
    'info_collect': ['eims_app.view_info_collect'],
    # ...
}
```

---

## ⚠️ 重要注意事项

### 1. 数据库迁移
删除模型后，建议创建新的迁移文件：
```bash
python manage.py makemigrations
python manage.py migrate
```

**或者**保留迁移文件但不再使用这些模型。

### 2. 数据备份
在执行删除操作前，建议备份数据库：
```bash
# SQLite
cp db.sqlite3 db_backup_before_cleanup.sqlite3

# MySQL (如果在生产环境)
mysqldump -u eims_user -p eims_db > backup_before_cleanup.sql
```

### 3. 测试验证
清理后需要测试：
- ✅ 服务器正常启动
- ✅ 其他模块功能正常
- ✅ 侧边栏菜单显示正确
- ✅ 没有 ImportError 或 NoReverseMatch 错误

---

## 🚀 执行步骤建议

### 第一阶段：删除物理文件
1. 删除模型、视图、表单文件
2. 删除模板文件夹
3. 清理 `__init__.py` 中的导入

### 第二阶段：清理配置代码
4. 清理 urls.py 路由
5. 清理 sidebar_tags.py 菜单配置
6. 清理 menu_config.js 菜单配置
7. 清理 permission_tags.py 权限映射

### 第三阶段：测试验证
8. 重启 Django 服务器
9. 访问各个模块确认无异常
10. 检查浏览器控制台无 JavaScript 错误

### 第四阶段：数据库清理（可选）
11. 创建并应用迁移（删除数据库表）
12. 或者保留表结构作为历史数据

---

## 📝 风险提示

⚠️ **高风险操作**：
- 直接删除数据库表可能导致数据丢失
- 如果其他代码引用了这些模型，会导致 ImportError

✅ **安全做法**：
- 先注释掉相关代码，观察一段时间
- 确认无影响后再物理删除
- 保留迁移文件以便版本控制

---

## ✅ 清理完成检查清单

- [ ] 所有废弃的物理文件已删除
- [ ] 所有导入语句已清理
- [ ] 路由配置已删除
- [ ] 菜单配置已更新
- [ ] 权限映射已清理
- [ ] 服务器正常启动
- [ ] 其他模块功能正常
- [ ] 侧边栏显示正确
- [ ] 无控制台错误
- [ ] 数据库迁移已处理

---

**生成时间**: 2026-03-26  
**文档版本**: v1.0  
**执行人**: [待填写]  
**复核人**: [待填写]
