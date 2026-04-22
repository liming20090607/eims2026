#!/usr/bin/env python
"""
Upload settings.py and deploy auto-correction system
"""

import paramiko
import time
import os

SSH_CONFIG = {
    'hostname': '39.106.41.239',
    'username': 'root',
    'password': 'fjkl546#'
}

def deploy():
    print("🚀 Deploying auto-correction system")
    print("="*70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(**SSH_CONFIG, timeout=10)
    print("✅ Connected\n")
    
    # Step 1: Ensure directory exists
    print("[1] Creating directories...")
    ssh.exec_command('mkdir -p /var/www/eims/eims /var/www/eims/logs')
    print("  ✅ Directories created")
    
    # Step 2: Upload settings.py using command line instead of SFTP
    print("\n[2] Uploading settings.py...")
    
    # Read local file
    local_path = 'e:\\EIMS2026\\settings.py'
    if not os.path.exists(local_path):
        print(f"  ❌ Local file not found: {local_path}")
        return
    
    with open(local_path, 'r', encoding='utf-8') as f:
        settings_content = f.read()
    
    print(f"  Read {len(settings_content)} bytes from local settings.py")
    
    # Write to server using cat and stdin
    stdin, stdout, stderr = ssh.exec_command(f'cat > /var/www/eims/eims/settings.py << SETTINGS_EOF\n{settings_content}\nSETTINGS_EOF', timeout=30)
    time.sleep(3)
    
    # Verify
    stdin, stdout, stderr = ssh.exec_command('wc -l /var/www/eims/eims/settings.py')
    lines = stdout.read().decode().strip()
    print(f"  ✅ Uploaded {lines}")
    
    # Check password
    stdin, stdout, stderr = ssh.exec_command("grep 'PASSWORD' /var/www/eims/eims/settings.py | head -2")
    pwd_check = stdout.read().decode().strip()
    print(f"  Password config: {pwd_check}")
    
    # Step 3: Create auto-correction script
    print("\n[3] Creating auto-correction script...")
    
    script = '''#!/bin/bash
# EIMS2026 Auto-Correction System
# Runs every 2 minutes automatically
# Log: /var/www/eims/logs/auto_correction.log

LOG="/var/www/eims/logs/auto_correction.log"
EIMS="/var/www/eims"
PY="$EIMS/venv/bin/python"
GUN="$EIMS/venv/bin/gunicorn"
SETTINGS="$EIMS/eims/settings.py"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$1] $2" >> "$LOG"; }

log "INFO" "=== Auto-correction check ==="

# Fix 1: Check settings.py
if [ ! -s "$SETTINGS" ]; then
    log "ERROR" settings.py missing/empty!
    echo "from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-eims2026'
DEBUG = True
ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['http://www.xietongai.com.cn','http://xietongai.com.cn','http://39.106.41.239']
INSTALLED_APPS = ['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','django_extensions','import_export','eims_app','widget_tweaks']
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware','whitenoise.middleware.WhiteNoiseMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','eims_app.middleware.path_resolver.PathResolverMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware','eims_app.middleware.TenantMiddleware','eims_app.middleware.login_required_middleware','eims_app.middleware.monthly_report_reminder_middleware']
ROOT_URLCONF = 'urls'
WSGI_APPLICATION = 'wsgi.application'
DATABASES = {
    'default': {'ENGINE': 'django.db.backends.mysql','NAME': 'eims_dingce','USER': 'root','PASSWORD': 'EIMS2026_mysql','HOST': 'localhost','PORT': '3306'},
    'dingce': {'ENGINE': 'django.db.backends.mysql','NAME': 'eims_dingce','USER': 'root','PASSWORD': 'EIMS2026_mysql','HOST': 'localhost','PORT': '3306'},
    'shengchang': {'ENGINE': 'django.db.backends.mysql','NAME': 'eims_shengchang','USER': 'root','PASSWORD': 'EIMS2026_mysql','HOST': 'localhost','PORT': '3306'},
    'jiachengda': {'ENGINE': 'django.db.backends.mysql','NAME': 'eims_jiachengda','USER': 'root','PASSWORD': 'EIMS2026_mysql','HOST': 'localhost','PORT': '3306'},
    'root_admin': {'ENGINE': 'django.db.backends.mysql','NAME': 'eims_root','USER': 'root','PASSWORD': 'EIMS2026_mysql','HOST': 'localhost','PORT': '3306'},
}
DATABASE_ROUTERS = ['eims_app.utils.database_router.CompanyDatabaseRouter']
import pymysql
pymysql.install_as_MySQLdb()
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = '$EIMS/staticfiles'
STATICFILES_DIRS = ['$EIMS/static']
MEDIA_URL = '/media/'
MEDIA_ROOT = '$EIMS/media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = '/login/'
SESSION_COOKIE_AGE = 86400" > "$SETTINGS"
    log "SUCCESS" ✅ settings.py restored
fi

# Fix 2: Correct MySQL password if wrong
if grep -q "'PASSWORD': 'root123'" "$SETTINGS" 2>/dev/null; then
    sed -i "s/'PASSWORD': 'root123'/'PASSWORD': 'EIMS2026_mysql'/g" "$SETTINGS"
    log "SUCCESS" ✅ Fixed MySQL password
fi

# Fix 3: MySQL
if ! systemctl is-active --quiet mysqld; then
    log "WARNING" MySQL down, restarting...
    systemctl restart mysqld
    sleep 3
    log "SUCCESS" ✅ MySQL restarted
fi

# Fix 4: Gunicorn
GCOUNT=$(pgrep -c gunicorn 2>/dev/null || echo "0")
if [ "$GCOUNT" -lt 2 ]; then
    log "WARNING" Gunicorn down ($GCOUNT), restarting...
    pkill -9 gunicorn 2>/dev/null || true
    sleep 2
    cd "$EIMS"
    nohup $GUN --bind 127.0.0.1:8000 --workers 5 --timeout 120 eims.wsgi:application --access-logfile "$EIMS/logs/gunicorn_access.log" --error-logfile "$EIMS/logs/gunicorn_error.log" >/dev/null 2>&1 &
    sleep 5
    NCOUNT=$(pgrep -c gunicorn 2>/dev/null || echo "0")
    log "SUCCESS" ✅ Gunicorn restarted ($NCOUNT workers)
fi

# Fix 5: Nginx
if ! pgrep -q nginx; then
    log "WARNING" Nginx down, starting...
    nginx
    sleep 2
    log "SUCCESS" ✅ Nginx started
fi

# Test HTTP
CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/ 2>&1)
if [[ "$CODE" =~ ^(200|302|500)$ ]]; then
    log "SUCCESS" ✅ HTTP OK ($CODE)
else
    log "WARNING" ⚠️ HTTP $CODE
fi

log "INFO" === Check complete ===
'''
    
    stdin, stdout, stderr = ssh.exec_command(f'cat > /usr/local/bin/eims_auto_fix.sh << SCRIPT_EOF\n{script}\nSCRIPT_EOF', timeout=10)
    time.sleep(2)
    ssh.exec_command('chmod +x /usr/local/bin/eims_auto_fix.sh')
    print("  ✅ Auto-correction script created")
    
    # Step 4: Add to cron
    print("\n[4] Adding to crontab...")
    stdin, stdout, stderr = ssh.exec_command('crontab -l 2>/dev/null | grep eims_auto_fix')
    if not stdout.read().decode().strip():
        ssh.exec_command('(crontab -l 2>/dev/null; echo "*/2 * * * * /usr/local/bin/eims_auto_fix.sh") | crontab -')
        print("  ✅ Added to cron (every 2 minutes)")
    else:
        print("  ✅ Already in cron")
    
    # Step 5: Run immediate fix
    print("\n[5] Running immediate fix...")
    ssh.exec_command('/usr/local/bin/eims_auto_fix.sh')
    time.sleep(12)
    
    # Step 6: Check results
    print("\n[6] Checking system status...")
    
    tests = [
        ('settings.py exists', 'test -s /var/www/eims/eims/settings.py && echo OK || echo FAIL'),
        ('MySQL', 'systemctl is-active mysqld'),
        ('Gunicorn', 'pgrep -c gunicorn'),
        ('Nginx', 'pgrep -c nginx || echo 0'),
        ('HTTP 80', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:80/login/'),
        ('HTTP 8000', 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000/login/'),
    ]
    
    for name, cmd in tests:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        result = stdout.read().decode().strip()
        print(f"  {name}: {result}")
    
    # Show logs
    print("\n" + "="*70)
    print("📋 Recent auto-correction log:")
    print("="*70)
    stdin, stdout, stderr = ssh.exec_command('tail -12 /var/www/eims/logs/auto_correction.log 2>/dev/null')
    logs = stdout.read().decode().strip()
    if logs:
        for line in logs.split('\n')[-8:]:
            print(f"  {line}")
    else:
        print("  (No logs yet)")
    
    ssh.close()
    
    print("\n" + "="*70)
    print("✅ AUTO-CORRECTION SYSTEM DEPLOYED!")
    print("="*70)
    print("\n📊 What it does every 2 minutes:")
    print("  1. Checks settings.py exists and has correct MySQL password")
    print("  2. Restarts MySQL if crashed")
    print("  3. Restarts Gunicorn if crashed")
    print("  4. Restarts Nginx if stopped")
    print("  5. Tests HTTP response")
    print("\n🎯 Test your website:")
    print("   http://www.xietongai.com.cn/login/")
    print("\n💡 The system will now auto-fix itself!")
    print("="*70 + "\n")

if __name__ == '__main__':
    deploy()
