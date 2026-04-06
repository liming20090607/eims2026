@echo off
chcp 65001 >nul
title Fix Import-Export Templates
echo ========================================
echo   Fix Import-Export Templates
echo ========================================
echo.
echo This will copy the required template files
echo to the server.
echo.

echo Step 1: Finding template files...
if exist "venv\Lib\site-packages\import_export\templates" (
    echo Templates found in local venv.
    echo Copying to server...
    
    :: Create temp directory for templates
    mkdir C:\temp\import_export_templates 2>nul
    
    :: Copy templates
    xcopy /E /I /Y "venv\Lib\site-packages\import_export\templates" C:\temp\import_export_templates\
    
    echo.
    echo Step 2: Uploading templates to server...
    scp -r C:\temp\import_export_templates\* root@39.106.41.239:/var/www/eims/venv/lib/python3.10/site-packages/import_export/templates/
    
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo Templates uploaded successfully!
    ) else (
        echo.
        echo Failed to upload templates!
    )
) else (
    echo Templates not found in local venv.
    echo Trying alternative location...
    
    if exist "%APPDATA%\Python\Python310\site-packages\import_export\templates" (
        echo Found in AppData.
        xcopy /E /I /Y "%APPDATA%\Python\Python310\site-packages\import_export\templates" C:\temp\import_export_templates\
        scp -r C:\temp\import_export_templates\* root@39.106.41.239:/var/www/eims/venv/lib/python3.10/site-packages/import_export/templates/
    ) else (
        echo.
        echo Cannot find templates locally. We need to create them manually.
    )
)

echo.
echo ========================================
echo   Complete!
echo ========================================
echo.
pause
