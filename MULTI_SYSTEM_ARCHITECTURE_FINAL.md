# 多系统架构 - 最终实施方案

## 架构概述

采用**单应用 + 数据库路由 + URL前缀识别**的架构模式：

```
E:/EIMS2026/
├── eims_app/                 # 唯一Django应用
│   ├── models/               # 所有数据模型
│   ├── views/                # 所有视图函数
│   ├── forms/                # 所有表单
│   ├── middleware/           # 中间件（含路径解析器）
│   ├── utils/                # 工具函数（含数据库路由器）
│   └── templates/            # 所有模板
│
├── settings.py               # 配置4个独立数据库
├── urls.py                   # URL路由分发
└── manage.py
```

## 工作原理

### 1. URL路由
```python
# urls.py
path('dingce/', include('eims_app.urls')),      # 鼎策系统
path('shengchang/', include('eims_app.urls')),  # 晟昌系统
path('jiachengda/', include('eims_app.urls')),  # 嘉诚达系统
path('root/', include('eims_app.urls')),        # Root后台
path('', route_selector),                        # 智能路由入口
```

### 2. 路径解析中间件
`eims_app/middleware/path_resolver.py` 自动识别URL前缀并设置：
- `request.current_system` = 'dingce' | 'shengchang' | 'jiachengda' | 'root'
- `request.company_name` = 对应公司名称

### 3. 数据库路由器
`eims_app/utils/database_router.py` 根据 `request.current_system` 自动选择数据库：
- 'dingce' → eims_dingce 数据库
- 'shengchang' → eims_shengchang 数据库
- 'jiachengda' → eims_jiachengda 数据库
- 'root' → eims_root 数据库

### 4. 智能路由选择器
`eims_app/views/views_router.py` 的 `route_selector()` 函数：
- Superuser → /root/
- 单公司用户 → 自动跳转到该公司系统
- 多公司用户 → 显示公司选择页面
- 无权限用户 → 提示页面

## 数据库配置

在 `settings.py` 中配置4个独立数据库：

```python
DATABASES = {
    'default': {...},      # eims_dingce
    'dingce': {...},       # 鼎策数据库
    'shengchang': {...},   # 晟昌数据库
    'jiachengda': {...},   # 嘉诚达数据库
    'root_admin': {...},   # Root后台数据库
}

DATABASE_ROUTERS = ['eims_app.utils.database_router.CompanyDatabaseRouter']
```

## 优势

✅ **简洁可靠** - 只有一个Django应用，无命名冲突  
✅ **完全隔离** - 每个公司独立数据库  
✅ **易于维护** - 代码只需维护一份  
✅ **灵活扩展** - 添加新公司只需添加URL路由和数据库配置  
✅ **自动路由** - 中间件和路由器自动处理，视图无需修改  

## 部署步骤

### 1. 创建数据库
```bash
mysql -u root -p < create_multi_system_databases.sql
```

### 2. 执行迁移
```bash
# 为每个数据库执行迁移
python manage.py migrate --database=dingce
python manage.py migrate --database=shengchang
python manage.py migrate --database=jiachengda
python manage.py migrate --database=root_admin
```

### 3. 创建超级管理员
```bash
python manage.py createsuperuser --database=root_admin
```

### 4. 启动服务器
```bash
python manage.py runserver
```

## 访问地址

- 鼎策系统：http://127.0.0.1:8000/dingce/
- 晟昌系统：http://127.0.0.1:8000/shengchang/
- 嘉诚达系统：http://127.0.0.1:8000/jiachengda/
- Root后台：http://127.0.0.1:8000/root/
- 智能路由：http://127.0.0.1:8000/ （推荐入口）

## 关键文件

### 已创建的核心组件
1. ✅ `eims_app/middleware/path_resolver.py` - 路径解析中间件
2. ✅ `eims_app/utils/database_router.py` - 数据库路由器
3. ✅ `eims_app/views/views_router.py` - 智能路由选择器
4. ✅ `eims_app/templates/eims_app/tenant_select.html` - 公司选择页面
5. ✅ `eims_app/templates/eims_app/no_permission.html` - 权限不足页面

### 配置文件
1. ✅ `settings.py` - 多数据库配置
2. ✅ `urls.py` - URL路由分发

### 辅助脚本
1. ✅ `create_multi_system_databases.sql` - 数据库创建脚本
2. ✅ `run_multi_system_migrations.py` - 批量迁移脚本
3. ✅ `test_multi_system.py` - 测试脚本
4. ✅ `start_multi_system.bat` - Windows快速启动脚本

## 注意事项

⚠️ **URL Namespace警告**  
Django会提示 "URL namespace 'eims_app' isn't unique"，这是因为多个路径include了同一个urls.py。这不影响功能，可以忽略。

⚠️ **视图中的反向URL引用**  
确保所有视图中使用 `reverse('eims_app:view_name')` 时能正确解析。如果需要区分不同公司的URL，可以在视图中根据 `request.current_system` 动态构建URL。

⚠️ **静态文件和媒体文件**  
所有公司共享同一套静态文件和媒体文件目录。如需隔离，可在视图中根据 `request.current_system` 设置不同的MEDIA_ROOT。

## 后续优化建议

1. **模板定制** - 可为不同公司创建不同的base模板
2. **静态文件隔离** - 为每个公司设置独立的static/media目录
3. **缓存策略** - 为每个公司设置独立的缓存key前缀
4. **日志分离** - 为每个公司记录独立的日志文件

---

**架构版本**: v2.0 (单应用多租户)  
**更新日期**: 2026年3月21日  
**状态**: ✅ 已完成基础架构，待数据库初始化和测试
