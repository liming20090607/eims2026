#!/bin/bash
# Auto-Correction Script for Server-side execution
# This script will be run by OpenClaw every 2 minutes

LOG_FILE="/var/www/eims/logs/auto_correction.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$1] $2" | tee -a "$LOG_FILE"
}

log "INFO" "=========================================="
log "INFO" "Starting auto-correction check..."

# Check and fix MySQL
check_mysql() {
    if ! systemctl is-active --quiet mysqld; then
        log "WARNING" "MySQL is not running, attempting to fix..."
        systemctl start mysqld
        sleep 2
        if systemctl is-active --quiet mysqld; then
            log "SUCCESS" "✅ MySQL started successfully"
        else
            log "ERROR" "❌ Failed to start MySQL, trying restart..."
            systemctl restart mysqld
            sleep 3
            if systemctl is-active --quiet mysqld; then
                log "SUCCESS" "✅ MySQL restarted successfully"
            else
                log "ERROR" "❌ MySQL restart failed"
                return 1
            fi
        fi
    fi
    return 0
}

# Check and fix Gunicorn
check_gunicorn() {
    GUNICORN_COUNT=$(pgrep -c gunicorn 2>/dev/null || echo "0")
    if [ "$GUNICORN_COUNT" -lt 2 ]; then
        log "WARNING" "Gunicorn not running ($GUNICORN_COUNT workers), restarting..."
        pkill -9 gunicorn 2>/dev/null || true
        sleep 1
        cd /var/www/eims && /var/www/eims/venv/bin/gunicorn \
            --bind 127.0.0.1:8000 \
            --workers 5 \
            eims.wsgi:application \
            --daemon
        sleep 3
        NEW_COUNT=$(pgrep -c gunicorn 2>/dev/null || echo "0")
        if [ "$NEW_COUNT" -ge 2 ]; then
            log "SUCCESS" "✅ Gunicorn running with $NEW_COUNT workers"
        else
            log "ERROR" "❌ Gunicorn failed to start"
            return 1
        fi
    fi
    return 0
}

# Check and fix Nginx
check_nginx() {
    if ! pgrep -q nginx; then
        log "WARNING" "Nginx not running, restarting..."
        nginx -s stop 2>/dev/null || true
        sleep 1
        nginx
        sleep 2
        if pgrep -q nginx; then
            log "SUCCESS" "✅ Nginx running"
        else
            log "ERROR" "❌ Nginx failed to start"
            return 1
        fi
    fi
    return 0
}

# Fix CSRF configuration
fix_csrf() {
    SETTINGS_FILE="/var/www/eims/eims/settings.py"
    
    if ! grep -q "CSRF_TRUSTED_ORIGINS" "$SETTINGS_FILE"; then
        log "WARNING" "CSRF configuration missing, adding..."
        cat >> "$SETTINGS_FILE" << 'EOF'

# CSRF Configuration - Auto-added by auto-correction system
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_TRUSTED_ORIGINS = [
    'http://www.xietongai.com.cn',
    'http://xietongai.com.cn',
    'http://39.106.41.239',
    'http://localhost',
]
EOF
        log "SUCCESS" "✅ CSRF configuration added"
    fi
    return 0
}

# Check HTTP status
check_http() {
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://127.0.0.1:80/login/ 2>&1)
    if [[ "$HTTP_CODE" =~ ^(200|302|500)$ ]]; then
        log "SUCCESS" "✅ HTTP service responding (status: $HTTP_CODE)"
        return 0
    else
        log "WARNING" "⚠️ HTTP service not responding correctly (status: $HTTP_CODE)"
        return 1
    fi
}

# Run all checks
check_mysql
check_gunicorn
check_nginx
fix_csrf
check_http

log "INFO" "=========================================="
log "INFO" "Auto-correction check completed"
