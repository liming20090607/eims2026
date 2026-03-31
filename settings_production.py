"""
生产环境 Django 配置示例
使用方法：复制此文件为 settings_production.py 并根据实际情况修改
"""

from .settings import *  # 导入基础配置

# -------------------------- 安全配置（必须修改）--------------------------
DEBUG = False

# 生成强密钥（运行 python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"）
SECRET_KEY = '你的超长随机密钥-至少 50 字符'

# 允许的主机（必须修改为实际域名和 IP）
ALLOWED_HOSTS = [
    '你的域名.com',
    'www.你的域名.com',
    '服务器公网 IP',
    'localhost',
    '127.0.0.1',
]

# CSRF 信任的源
CSRF_TRUSTED_ORIGINS = [
    'http://你的域名.com',
    'https://你的域名.com',
]

# -------------------------- 数据库配置（MySQL）--------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'eims'),
        'USER': os.getenv('DB_USER', 'eims_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', '你的强密码'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}

# -------------------------- 静态文件和媒体文件--------------------------
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 使用 WhiteNoise 压缩静态文件
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# -------------------------- 日志配置--------------------------
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
            'filename': '/var/log/django/error.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# -------------------------- 安全增强--------------------------
# 使用 HTTPS 时启用
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

# 防止点击劫持
X_FRAME_OPTIONS = 'DENY'

# 内容安全策略
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# HSTS（仅 HTTPS）
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# -------------------------- 会话和 Cookie--------------------------
SESSION_COOKIE_AGE = 1209600  # 2 周
SESSION_SAVE_EVERY_REQUEST = True
CSRF_COOKIE_AGE = 1209600

# -------------------------- 文件上传--------------------------
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# -------------------------- 缓存配置（可选，使用 Redis）--------------------------
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.redis.RedisCache',
#         'LOCATION': 'redis://127.0.0.1:6379/1',
#     }
# }

# -------------------------- 邮件配置（可选）--------------------------
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.qq.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@qq.com'
# EMAIL_HOST_PASSWORD = 'your-email-password'
# DEFAULT_FROM_EMAIL = 'your-email@qq.com'

# -------------------------- 其他生产环境配置--------------------------
# 限制管理员权限
ADMINS = [
    ('Admin', 'admin@example.com'),
]

# 分页
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 时区
TIME_ZONE = 'Asia/Shanghai'
USE_TZ = False  # 生产环境建议使用 False，避免时区转换问题
