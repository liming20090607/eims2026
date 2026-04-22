@echo off
chcp 65001 >nul
echo ================================================================
echo Monthly Report Data Recovery - Step by Step
echo 月度报告数据恢复 - 分步执行
echo ================================================================
echo.
echo This script will help you recover monthly report data from the cloud server.
echo 此脚本将帮助您从云服务器恢复月度报告数据。
echo.
echo Cloud Server: root@39.106.41.239
echo.
echo ================================================================
echo Step 1: Export data from cloud server
echo 步骤1：从云服务器导出数据
echo ================================================================
echo.
echo Please execute the following command and enter your SSH password when prompted:
echo 请执行以下命令，并在提示时输入SSH密码：
echo.
echo ssh root@39.106.41.239 "cd /var/www/eims ^&^& source venv/bin/activate ^&^& python manage.py dumpdata eims_app.monthlyreport --indent 2 ^> /tmp/monthly_report_export.json ^&^& echo 'Export completed' ^&^& wc -l /tmp/monthly_report_export.json"
echo.
pause
echo.
echo ================================================================
echo Step 2: Download exported file
echo 步骤2：下载导出的文件
echo ================================================================
echo.
echo Please execute the following command and enter your SSH password when prompted:
echo 请执行以下命令，并在提示时输入SSH密码：
echo.
echo scp root@39.106.41.239:/tmp/monthly_report_export.json e:\EIMS2026\monthly_report_export.json
echo.
pause
echo.
echo ================================================================
echo Step 3: Import data to local database
echo 步骤3：导入数据到本地数据库
echo ================================================================
echo.
echo Now running the import script...
echo 现在运行导入脚本...
echo.
python restore_monthly_reports_import_only.py
echo.
pause
