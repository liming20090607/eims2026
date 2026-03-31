@echo off
chcp 65001 >nul

echo ================== 设置EIMS自动备份 ==================
echo.

schtasks /query /tn "EIMS_Auto_Backup" >nul 2>&1

if %errorlevel% equ 0 (
    echo 检测到已存在定时任务
    set /p CHOICE="是否重新创建? (Y/N): "
    if /i not "%CHOICE%"=="Y" (
        echo 已取消
        exit /b 0
    )
    schtasks /delete /tn "EIMS_Auto_Backup" /f >nul 2>&1
    echo 已删除旧任务
)

echo.
echo 正在创建定时任务: 每10分钟自动备份数据库
echo.

schtasks /create /tn "EIMS_Auto_Backup" /tr "e:\EIMS2026\backup_auto.BAT" /sc minute /mo 10 /f >nul 2>&1

if %errorlevel% equ 0 (
    echo [SUCCESS] 自动备份任务创建成功
    echo 任务详情:
    echo   - 任务名称: EIMS_Auto_Backup
    echo   - 执行间隔: 每10分钟
    echo   - 备份脚本: e:\EIMS2026\backup_auto.BAT
    echo   - 备份目录: e:\EIMS2026\backup\
    echo.
    echo 现在运行一次备份测试...
    call e:\EIMS2026\backup_auto.BAT
) else (
    echo [ERROR] 创建定时任务失败
    echo 请以管理员身份运行此脚本
    exit /b 1
)

echo.
echo ================================================
echo 备份设置完成!
echo.
echo 可用操作:
echo   1. 立即备份:   双击运行 backup_auto.BAT
echo   2. 恢复数据:   双击运行 restore_db.BAT
echo   3. 停止自动:   schtasks /delete /tn "EIMS_Auto_Backup" /f
echo ================================================
pause
