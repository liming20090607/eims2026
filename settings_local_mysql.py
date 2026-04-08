"""
EIMS Local Development Configuration - MySQL
Use this file by copying its content to settings.py or importing it.
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import base settings module
import settings as base_settings

# Override critical settings BEFORE importing *
ROOT_URLCONF = 'urls'  # Must be set before any import from settings

# Now import base settings
from settings import *

# ==================== Database Configuration ====================
# Use local MySQL database
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

# Override URL configuration for production
ROOT_URLCONF = 'urls'

# ==================== Other Development Config ====================
# Keep DEBUG mode
DEBUG = True

# Allow all hosts (local development)
ALLOWED_HOSTS = ['*']

# ==================== Static Files Configuration ====================
# WhiteNoise storage for production (compresses static files)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Use PyMySQL as MySQL driver
import pymysql
pymysql.install_as_MySQLdb()

print("Local MySQL configuration loaded")
