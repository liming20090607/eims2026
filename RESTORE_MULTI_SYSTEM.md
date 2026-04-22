# 多系统架构恢复指南

## 📋 当前状态分析

### ✅ 已存在的核心组件
1. **路径解析中间件**: `eims_app/middleware/path_resolver.py` ✓
2. **数据库路由器**: `eims_app/utils/database_router.py` ✓
3. **智能路由选择器**: `eims_app/views/views_router.py` ✓
4. **用户管理优化**: `eims_app/views/views_user_management.py` ✓
5. **相关模板和表单**: 已存在 ✓

### ❌ 需要恢复的配置
1. **settings.py** - 需要配置4个独立数据库
2. **urls.py** - 需要添加多系统URL路由
3. **MIDDLEWARE** - 需要添加PathResolverMiddleware
4. **DATABASE_ROUTERS** - 需要注册数据库路由器

---

## 🔧 恢复步骤

### 第1步：备份当前配置
```bash
copy settings.py settings_single_db_backup.py
copy urls.py urls_single_db_backup.py
```

### 第2步：创建多系统数据库
执行SQL脚本创建4个独立数据库：
```bash
mysql -u root -p < create_multi_system_databases.sql
```

或手动执行：
```sql
CREATE DATABASE IF NOT EXISTS eims_dingce CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS eims_shengchang CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS eims_jiachengda CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS eims_root CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 第3步：更新 settings.py

#### A. 修改数据库配置（第81-94行）
将当前的单数据库配置替换为：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'eims_dingce',
        'USER': 'root',
        'PASSWORD': 'root123',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    },
    'dingce': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'eims_dingce',
        'USER': 'root',
        'PASSWORD': 'root123',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    },
    'shengchang': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'eims_shengchang',
        'USER': 'root',
        'PASSWORD': 'root123',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    },
    'jiachengda': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'eims_jiachengda',
        'USER': 'root',
        'PASSWORD': 'root123',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    },
    'root_admin': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'eims_root',
        'USER': 'root',
        'PASSWORD': 'root123',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    },
}

# 注册数据库路由器
DATABASE_ROUTERS = ['eims_app.utils.database_router.CompanyDatabaseRouter']
```

#### B. 添加中间件（在 MIDDLEWARE 列表中）
找到 `MIDDLEWARE` 配置，在适当位置添加：

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'eims_app.middleware.path_resolver.PathResolverMiddleware',  # ← 添加这一行
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### 第4步：更新 urls.py

将当前的 urls.py 替换为多系统路由配置：

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseRedirect
from eims_app.views.views_custom_login import custom_login
from eims_app.views.views_router import route_selector

def profile_redirect(request):
    return HttpResponseRedirect('/')

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return HttpResponseRedirect('/login/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout/', logout_view, name='logout'),
    path('login/', custom_login, name='user_login'),
    path('accounts/login/', custom_login, name='login'),
    path('accounts/profile/', profile_redirect, name='user_profile'),
    
    # ===== 多系统路由 =====
    # 智能路由入口（推荐）
    path('', route_selector, name='route_selector'),
    
    # 各公司系统
    path('dingce/', include('eims_app.urls')),
    path('shengchang/', include('eims_app.urls')),
    path('jiachengda/', include('eims_app.urls')),
    
    # Root超级管理员后台
    path('root/', include('eims_app.urls')),
]

# 媒体文件配置（开发环境）
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 第5步：执行数据库迁移

为每个数据库执行迁移：

```bash
python manage.py migrate --database=dingce
python manage.py migrate --database=shengchang
python manage.py migrate --database=jiachengda
python manage.py migrate --database=root_admin
```

或使用批量脚本：
```bash
python run_multi_system_migrations.py
```

### 第6步：创建Root超级管理员

```bash
python manage.py createsuperuser --database=root_admin
```

### 第7步：初始化租户数据

运行租户初始化脚本：
```bash
python add_three_tenants.py
python init_tenant_modules.py
```

### 第8步：测试验证

启动服务器：
```bash
python manage.py runserver
```

访问以下地址测试：
- 智能路由入口: http://127.0.0.1:8000/
- 鼎策系统: http://127.0.0.1:8000/dingce/
- 晟昌系统: http://127.0.0.1:8000/shengchang/
- 嘉诚达系统: http://127.0.0.1:8000/jiachengda/
- Root后台: http://127.0.0.1:8000/root/

---

## 🎯 预期效果

### 1. 数据完全隔离
- 每个公司有独立的数据库
- 鼎策的数据不会出现在晟昌系统中
- Root后台可以跨库管理所有数据

### 2. 智能路由
- Superuser登录 → 自动跳转到 /root/
- 单公司员工 → 自动跳转到所属公司系统
- 多公司员工 → 显示公司选择页面

### 3. 用户管理优化
- 支持批量创建用户
- 支持从员工信息同步创建用户账号
- 完善的权限控制

---

## ⚠️ 注意事项

### URL Namespace警告
Django可能会提示：
```
WARNINGS:
?: (urls.W005) URL namespace 'eims_app' isn't unique.
```
这是正常的，因为多个路径include了同一个urls.py，不影响功能。

### 现有数据处理
如果当前数据库中有重要数据，需要先备份：
```bash
mysqldump -u root -p eims > backup_before_multisystem.sql
```

然后在新数据库中重新导入或迁移数据。

---

## 📞 需要帮助？

如果在恢复过程中遇到问题，请检查：
1. 数据库是否正确创建
2. settings.py 配置是否正确
3. urls.py 路由是否正确
4. 中间件是否已注册
5. 数据库路由器是否生效

查看错误日志获取详细信息。
