#!/bin/bash
# 检查 django-import-export 版本

echo "========================================"
echo "  检查服务器配置"
echo "========================================"
echo ""

cd /var/www/eims
source venv/bin/activate

echo "1. django-import-export 版本:"
python3 -c "import import_export; print(f'   版本：{import_export.__version__}')"

echo ""
echo "2. Django 版本:"
python3 -c "import django; print(f'   版本：{django.VERSION}')"

echo ""
echo "3. SQLite 版本:"
python3 -c "import sqlite3; print(f'   版本：{sqlite3.sqlite_version}')"

echo ""
echo "4. admin.py 中的配置:"
grep -n "ImportExportModelAdmin" eims_app/admin.py | head -3

echo ""
echo "5. Gunicorn 状态:"
supervisorctl status eims

echo ""
echo "========================================"
echo "  检查完成"
echo "========================================"
