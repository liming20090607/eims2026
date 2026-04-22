# 多系统架构修正方案

## 问题诊断

当前实现存在**模型命名冲突**问题：
- eims_dingce.Contract
- eims_shengchang.Contract  
- eims_jiachengda.Contract
- eims_root_admin.Contract

Django无法区分这些同名模型，导致反向关系冲突。

## 正确架构设计

### 方案：共享模型 + 独立视图

```
E:/EIMS2026/
├── eims_app/                 # 共享层
│   ├── models/               # ✅ 所有模型放在这里（唯一数据源）
│   ├── forms/                # ✅ 所有表单放在这里
│   ├── middleware/           # ✅ 中间件
│   └── utils/                # ✅ 工具函数
│
├── eims_dingce/              # 鼎策公司应用
│   ├── views/                # ✅ 仅视图（使用eims_app.models）
│   ├── templates/            # ✅ 仅模板
│   ├── urls.py               # ✅ URL配置
│   └── apps.py               # ✅ 应用配置
│
├── eims_shengchang/          # 晟昌公司应用（同上）
├── eims_jiachengda/          # 嘉诚达公司应用（同上）
└── eims_root_admin/          # Root后台（同上）
```

### 关键原则

1. **模型只在eims_app中定义一次**
2. **各公司应用通过数据库路由器访问不同数据库**
3. **视图根据request.current_system自动选择数据库**

## 实施步骤

### 步骤1：删除重复的models目录

```bash
# 删除公司应用中的models目录
Remove-Item -Recurse -Force eims_dingce\models
Remove-Item -Recurse -Force eims_shengchang\models
Remove-Item -Recurse -Force eims_jiachengda\models
Remove-Item -Recurse -Force eims_root_admin\models
```

### 步骤2：修改公司应用的导入

将所有公司应用中的模型导入改为：
```python
from eims_app.models import Contract, ProjectDetail, ...
```

### 步骤3：保持eims_app在INSTALLED_APPS中

```python
INSTALLED_APPS = [
    ...
    'eims_app',              # ← 必须保留！
    'eims_dingce',
    'eims_shengchang',
    'eims_jiachengda',
    'eims_root_admin',
]
```

### 步骤4：数据库路由器保持不变

CompanyDatabaseRouter已经正确配置，会根据request.current_system自动选择数据库。

## 优势

✅ **无模型冲突** - 模型只定义一次  
✅ **代码复用** - 所有应用共享同一套模型和表单  
✅ **易于维护** - 修改模型只需改一处  
✅ **数据隔离** - 通过数据库路由器实现  

## 需要修改的文件

1. 删除4个公司应用的models/目录
2. 修改所有views/*.py中的import语句
3. 确保eims_app在INSTALLED_APPS中
4. 更新settings.py添加eims_app

---

**建议**: 是否需要我执行这个修正方案？这将解决所有模型冲突问题。
