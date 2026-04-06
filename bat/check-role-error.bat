@echo off
chcp 65001 >nul
title Check Role Restore Error
echo ========================================
echo   Check Role Restore Error
echo ========================================
echo.

ssh root@39.106.41.239 "echo '=== 当前数据库中角色 ==='; cd /var/www/eims; source venv/bin/activate; python3 -c 'import sys; sys.path.append(\"/var/www/eims\"); import os; os.environ.setdefault(\"DJANGO_SETTINGS_MODULE\", \"settings\"); import django; django.setup(); from eims_app.models import Role; print(f\"角色数量: {Role.objects.count()}\"); [print(f\"  - {r.id}: {r.name} - {r.description}\") for r in Role.objects.all()]'; echo ''; echo '=== 角色模型字段 ==='; python3 -c 'import sys; sys.path.append(\"/var/www/eims\"); import os; os.environ.setdefault(\"DJANGO_SETTINGS_MODULE\", \"settings\"); import django; django.setup(); from eims_app.models import Role; print([f.name for f in Role._meta.fields])'"

pause
