"""
WSGI config for EIMS project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/stable/howto/deployment/wsgi/
"""

import os

# Apply Python 3.14 compatibility patch before Django loads
try:
    import python314_patch
except ImportError:
    pass

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_local_mysql')

application = get_wsgi_application()
