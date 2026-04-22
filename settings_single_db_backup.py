"""Django settings for AOS (协同 AI 办公系统) project."""
import sys
import os
from pathlib import Path

# 添加venv路径以便导入dotenv
_venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'venv')
if os.path.exists(_venv_path) and _venv_path not in sys.path:
    sys.path.insert(0, _venv_path)

from dotenv import load_dotenv

# 清理重复路径
sys.path = list(dict.fromkeys(sys.path))

# 确保项目根目录在首位
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

print(f"Fixed Python path: {sys.path}")  # Debug

# 加载 .env 文件（如果存在）
load_dotenv()

# -------------------------- 基础路径配置 --------------------------
# 项目根目录：E:\AOS
BASE_DIR = Path(__file__).resolve().parent

# -------------------------- 安全配置 --------------------------
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-aos-development-key-2026')
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() == 'true'

# 允许的主机（开发环境）
#ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
ALLOWED_HOSTS = ['*']  # 开发阶段允许所有主机访问（生产环境请务必修改）

# CSRF 信任来源（生产环境配置）
CSRF_TRUSTED_ORIGINS = [
    'http://39.106.41.239',
    'http://39.106.41.239:8000',
    'http://localhost',
    'http://127.0.0.1',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# -------------------------- 应用配置 --------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',  # 支持 runserver_plus（HTTPS）
    'import_export',  # 数据导入导出
    'eims_app',
    'widget_tweaks',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # 静态文件服务（Gunicorn 生产环境必需）
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'eims_app.middleware.TenantMiddleware',  # 租户中间件 - 多租户数据隔离
    'eims_app.middleware.login_required_middleware',
    'eims_app.middleware.monthly_report_reminder_middleware',
]

ROOT_URLCONF = 'urls'
WSGI_APPLICATION = 'wsgi.application'

# -------------------------- 数据库配置 --------------------------
# 统一使用 MySQL 数据库（本地和服务器）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'eims',
        'USER': 'root',
        'PASSWORD': 'root123',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}

# 使用 PyMySQL 作为 MySQL 驱动
import pymysql
pymysql.install_as_MySQLdb()

# -------------------------- 密码验证 --------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 登出后重定向到登录页面
LOGOUT_REDIRECT_URL = '/login/'
LOGIN_URL = '/login/'

# -------------------------- Session 配置 --------------------------
SESSION_COOKIE_AGE = 1209600  # Session 过期时间：2 周（14 天）
SESSION_SAVE_EVERY_REQUEST = True  # 每次请求都保存 session，延长过期时间
SESSION_COOKIE_HTTPONLY = True  # 防止 XSS 攻击
SESSION_COOKIE_NAME = 'eims_sessionid'  # 自定义 session cookie 名称
SESSION_COOKIE_SAMESITE = 'Lax'  # 防止 CSRF 攻击，允许同站请求
SESSION_COOKIE_PATH = '/'  # Cookie 在整个站点可用

# 生产环境配置（通过 IP 访问时使用）
# 如果使用域名，取消注释并修改为实际域名
# SESSION_COOKIE_DOMAIN = 'xietongai.com.cn'
# SESSION_COOKIE_SECURE = True  # 仅 HTTPS 时启用

# 注意：通过 HTTP 访问时，SESSION_COOKIE_SECURE 必须为 False
# 通过 HTTPS 访问时，SESSION_COOKIE_SECURE 必须为 True
SESSION_COOKIE_SECURE = False  # 当前使用 HTTP，设为 False

# -------------------------- 国际化 --------------------------
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# -------------------------- 静态文件配置 --------------------------
# 必须设置 STATIC_URL，且以 / 开头和结尾
STATIC_URL = '/static/'

# 开发阶段额外的静态文件目录（对应 E:\EIMS\static）
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# 生产环境 collectstatic 收集目录（对应 E:\EIMS\staticfiles）
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# -------------------------- 媒体文件配置 --------------------------
# 用户上传文件的 URL 前缀
MEDIA_URL = '/media/'

# 用户上传文件的根目录
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# -------------------------- 默认主键字段类型 --------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -------------------------- 自定义认证后端 --------------------------
# 支持使用中文用户名、真实姓名或邮箱登录
AUTHENTICATION_BACKENDS = [
    'eims_app.backends.ChineseUsernameAuthenticationBackend',
]

# -------------------------- 模板配置 --------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',  # 添加此行，用于访问 MEDIA_URL
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'eims_app.context_processors.sidebar_context',  # 添加此行
            ],
        },
    },
]

# -------------------------- 日志配置（可选）--------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
    },
}

# EIMS/settings.py -> AOS/settings.py
if DEBUG:
    # 开发环境使用详细错误页面
    handler404 = 'django.views.defaults.page_not_found'
    handler500 = 'django.views.defaults.server_error'
else:
    # 生产环境使用自定义错误页面
    handler404 = 'eims_app.views.views_errors.custom_404'
    handler500 = 'eims_app.views.views_errors.custom_500'

# -------------------------- Django Admin 配置 --------------------------
# 注意：USE_DARK_THEME 仅在 Django 5.2+ 中可用，当前使用 Django 4.2.7
# 如需自定义 Admin 外观，请使用自定义模板
ADMIN_SITE_HEADER = '协同 AI 办公系统'
ADMIN_SITE_TITLE = '协同 AI 办公系统 - 后台管理'

# -------------------------- 微信开放平台配置 --------------------------
# 需要在微信开放平台注册网站应用后获取
# 注册地址：https://open.weixin.qq.com/
WECHAT_OPEN_APP_ID = os.getenv('WECHAT_OPEN_APP_ID', '')  # 微信开放平台AppID
WECHAT_OPEN_APP_SECRET = os.getenv('WECHAT_OPEN_APP_SECRET', '')  # 微信开放平台AppSecret
WECHAT_OPEN_REDIRECT_URI = os.getenv('WECHAT_OPEN_REDIRECT_URI', 'http://127.0.0.1:8000/wechat-login/callback/')  # 授权回调地址

# -------------------------- 阿里云短信配置 --------------------------
ALIYUN_ACCESS_KEY_ID = os.getenv('ALIYUN_ACCESS_KEY_ID', '')  # 阿里云AccessKey ID
ALIYUN_ACCESS_KEY_SECRET = os.getenv('ALIYUN_ACCESS_KEY_SECRET', '')  # 阿里云AccessKey Secret
ALIYUN_SMS_REGION = os.getenv('ALIYUN_SMS_REGION', 'cn-hangzhou')  # 短信服务区域
ALIYUN_SMS_SIGN_NAME = os.getenv('ALIYUN_SMS_SIGN_NAME', '')  # 短信签名
ALIYUN_SMS_TEMPLATE_CODE = os.getenv('ALIYUN_SMS_TEMPLATE_CODE', '')  # 短信模板代码
