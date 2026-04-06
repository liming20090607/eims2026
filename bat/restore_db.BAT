@echo off
chcp 65001 >nul

echo ================== EIMS数据库恢复 ==================
echo.

set "BACKUP_DIR=e:\EIMS2026\backup"
set "DB_FILE=e:\EIMS2026\db.sqlite3"

if not exist "%BACKUP_DIR%" (
    echo [ERROR] 备份目录不存在: %BACKUP_DIR%
    exit /b 1
)

echo 可用的备份文件:
echo.
dir /b /o-d "%BACKUP_DIR%\eims_backup_*.sqlite3"
echo.

set /p SELECTION="请输入要恢复的备份文件名(直接回车取消): "

if "%SELECTION%"=="" (
    echo 已取消恢复
    exit /b 0
)

set "RESTORE_PATH=%BACKUP_DIR%\%SELECTION%"

if not exist "%RESTORE_PATH%" (
    echo [ERROR] 备份文件不存在: %SELECTION%
    exit /b 1
)

echo.
echo 警告: 此操作将用备份文件替换当前数据库!
set /p CONFIRM="确认恢复? (输入Y确认，其他键取消): "

if /i not "%CONFIRM%"=="Y" (
    echo 已取消恢复
    exit /b 0
)

copy /Y "%RESTORE_PATH%" "%DB_FILE%" >nul 2>&1

if %errorlevel% equ 0 (
    echo [SUCCESS] 数据库恢复成功
    echo 已恢复到: %SELECTION%
) else (
    echo [ERROR] 数据库恢复失败
    exit /b 1
)

echo.
echo 提示: 请重启Django服务器使更改生效
pause
