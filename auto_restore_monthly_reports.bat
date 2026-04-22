@echo off
chcp 65001 >nul
echo ================================================================
echo Monthly Report Data Recovery - Automated
echo 月度报告数据恢复 - 自动化执行
echo ================================================================
echo.
echo This script will automatically:
echo 此脚本将自动执行：
echo   1. Export data from cloud server
echo      从云服务器导出数据
echo   2. Download the exported file
echo      下载导出的文件
echo   3. Import data to local database
echo      导入数据到本地数据库
echo.
echo You only need to enter SSH password once at the beginning.
echo 您只需在开始时输入一次SSH密码。
echo.
echo Press any key to start...
pause >nul
echo.

echo ================================================================
echo Step 1/3: Exporting data from cloud server...
echo 步骤 1/3：从云服务器导出数据...
echo ================================================================
echo.
echo Please enter your SSH password when prompted below:
echo 请在下方提示时输入SSH密码：
echo.

ssh root@39.106.41.239 "cd /var/www/eims && source venv/bin/activate && python manage.py dumpdata eims_app.monthlyreport --indent 2 --output /tmp/monthly_report_export.json && echo 'EXPORT_SUCCESS' && wc -l /tmp/monthly_report_export.json"

if %errorlevel% neq 0 (
    echo.
    echo ✗ Export failed! Please check the error above.
    echo ✗ 导出失败！请检查上面的错误信息。
    pause
    exit /b 1
)

echo.
echo ✓ Export completed successfully
echo ✓ 导出成功完成
echo.
timeout /t 2 /nobreak >nul

echo ================================================================
echo Step 2/3: Downloading exported file...
echo 步骤 2/3：下载导出的文件...
echo ================================================================
echo.

scp root@39.106.41.239:/tmp/monthly_report_export.json e:\EIMS2026\monthly_report_export.json

if %errorlevel% neq 0 (
    echo.
    echo ✗ Download failed! Please check the error above.
    echo ✗ 下载失败！请检查上面的错误信息。
    pause
    exit /b 1
)

echo.
echo ✓ Download completed successfully
echo ✓ 下载成功完成
echo.

REM Check if file exists and has content
if not exist e:\EIMS2026\monthly_report_export.json (
    echo ✗ File not found after download
    echo ✗ 下载后文件不存在
    pause
    exit /b 1
)

for %%A in (e:\EIMS2026\monthly_report_export.json) do set filesize=%%~zA
if %filesize% lss 100 (
    echo ✗ File is too small (%filesize% bytes), may be empty or corrupted
    echo ✗ 文件太小（%filesize% 字节），可能为空或损坏
    pause
    exit /b 1
)

echo ✓ File size: %filesize% bytes
echo ✓ 文件大小：%filesize% 字节
echo.
timeout /t 2 /nobreak >nul

echo ================================================================
echo Step 3/3: Importing data to local database...
echo 步骤 3/3：导入数据到本地数据库...
echo ================================================================
echo.

python restore_monthly_reports_import_only.py

if %errorlevel% neq 0 (
    echo.
    echo ✗ Import failed! Please check the error above.
    echo ✗ 导入失败！请检查上面的错误信息。
    pause
    exit /b 1
)

echo.
echo ================================================================
echo ✓✓✓ ALL STEPS COMPLETED SUCCESSFULLY! ✓✓✓
echo ✓✓✓ 所有步骤成功完成！ ✓✓✓
echo ================================================================
echo.
echo Next steps:
echo 下一步：
echo   1. Restart your Django development server
echo      重启Django开发服务器
echo   2. Navigate to the monthly report dashboard
echo      访问月度报告仪表板
echo   3. Verify that all reports are displaying correctly
echo      验证所有报告显示正确
echo.
pause
