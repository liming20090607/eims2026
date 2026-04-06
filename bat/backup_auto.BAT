@echo off
chcp 65001 >nul

set BACKUP_DIR=e:\EIMS2026\backup
set DB_FILE=e:\EIMS2026\db.sqlite3

if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

set TIMESTAMP=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set BACKUP_FILENAME=eims_backup_%TIMESTAMP%.sqlite3
set BACKUP_PATH=%BACKUP_DIR%\%BACKUP_FILENAME%

copy /Y "%DB_FILE%" "%BACKUP_PATH%"

if %errorlevel% equ 0 (
    echo [SUCCESS] 数据库备份成功: %BACKUP_FILENAME%
) else (
    echo [ERROR] 数据库备份失败
)

exit /b 0
