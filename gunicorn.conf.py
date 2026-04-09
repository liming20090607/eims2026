"""
Gunicorn configuration file for EIMS production deployment.
Explicitly sets DJANGO_SETTINGS_MODULE to use MySQL configuration.
"""
import os
import sys

# Ensure project root is in path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# CRITICAL: Set Django settings module BEFORE anything else loads
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings_local_mysql'

# Server socket
bind = '0.0.0.0:8000'

# Worker processes
workers = 3
worker_class = 'sync'
timeout = 120

# Logging
accesslog = '/var/www/eims/logs/access.log'
errorlog = '/var/www/eims/logs/error.log'
capture_output = True
loglevel = 'info'

# Process naming
proc_name = 'eims_gunicorn'

# WSGI Application - this will be loaded AFTER DJANGO_SETTINGS_MODULE is set
# Do NOT use os.environ.setdefault here as it won't override if already set
# The wsgi.py will use the already-set environment variable

# Force template reloading on each request
reload = True
