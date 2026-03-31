"""Django settings for EIMS production environment."""
import os
from pathlib import Path

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# -------------------------- 基础路径配置 --------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------- 安全配置（重要！）--------------------------
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY 环境变量未设置！")

DEBUG = False  # 生产环境必须关闭

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
]

# 从环境变量读取允许的主机
allowed_hosts = os.getenv('ALLOWED_HOSTS', '')
if allowed_hosts:
    ALLOWED_HOSTS.extend([h.strip() for h in allowed_hosts.split(',')])

# 安全增强设置
SECURE_SSL_REDIRECT = True  # 强制 HTTPS
SESSION_COOKIE_SECURE = True  # 仅通过 HTTPS 传输 session cookie
CSRF_COOKIE_SECURE = True  # 仅通过 HTTPS 传输 CSRF cookie
SECURE_HSTS_SECONDS = 31536000  # 1 年
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'  # 防止点击劫持
SECURE_CONTENT_TYPE_NOSNIFF = True  # 防止 MIME 类型嗅探

# -------------------------- 应用配置 --------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'eims_app',
    'widget_tweaks',
    # 生产环境优化
    'django_extensions',  # 开发工具
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # 静态文件压缩
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'eims_app.middleware.login_required.login_required_middleware',
]

ROOT_URLCONF = 'EIMS2026.urls'
WSGI_APPLICATION = 'wsgi.application'

# -------------------------- 数据库配置 --------------------------
# 生产环境推荐使用 PostgreSQL 或 MySQL
DB_ENGINE = os.getenv('DB_ENGINE', 'django.db.backends.sqlite3')

if DB_ENGINE == 'django.db.backends.postgresql':
    DATABASES = {
        'default': {
            'ENGINE': DB_ENGINE,
            'NAME': os.getenv('DB_NAME', 'eims_db'),
            'USER': os.getenv('DB_USER', 'eims_user'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
            'CONN_MAX_AGE': 60,  # 连接池
        }
    }
elif DB_ENGINE == 'django.db.backends.mysql':
    DATABASES = {
        'default': {
            'ENGINE': DB_ENGINE,
            'NAME': os.getenv('DB_NAME', 'eims_db'),
            'USER': os.getenv('DB_USER', 'eims_user'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '3306'),
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                'charset': 'utf8mb4',
            },
        }
    }
else:
    # SQLite（不推荐生产环境使用）
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# -------------------------- 密码验证 --------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------------- 国际化 --------------------------
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# -------------------------- 静态文件配置（生产环境）--------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# WhiteNoise 配置（可选，简化静态文件部署）
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# -------------------------- 媒体文件配置 --------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# -------------------------- 文件上传配置 --------------------------
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# -------------------------- 自定义认证后端 --------------------------
AUTHENTICATION_BACKENDS = [
    'eims_app.auth_backends.UsernameOrNameAuthBackend',
]

# -------------------------- 模板配置 --------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'eims_app.context_processors.sidebar_context',
            ],
        },
    },
]

# -------------------------- 日志配置（生产环境）--------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django_error.log',
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'eims_app': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# -------------------------- 错误处理 --------------------------
handler404 = 'eims_app.views.views_errors.custom_404'
handler500 = 'eims_app.views.views_errors.custom_500'

# -------------------------- 性能优化（可选）--------------------------
# Redis 缓存配置
# redis_url = os.getenv('REDIS_URL')
# if redis_url:
#     CACHES = {
#         'default': {
#             'BACKEND': 'django.core.cache.backends.redis.RedisCache',
#             'LOCATION': redis_url,
#         }
#     }

# -------------------------- 邮件配置（可选）--------------------------
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
if EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
    EMAIL_HOST = os.getenv('EMAIL_HOST')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@eims.com')

# -------------------------- CSRF 配置 --------------------------
CSRF_TRUSTED_ORIGINS = []
csrf_origins = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if csrf_origins:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in csrf_origins.split(',')]

# -------------------------- 会话配置 --------------------------
SESSION_COOKIE_AGE = 1209600  # 2 周
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# -------------------------- 其他生产环境设置 --------------------------
# 禁用 Django 调试工具栏
try:
    import debug_toolbar
except ImportError:
    pass

# 默认主键字段类型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
