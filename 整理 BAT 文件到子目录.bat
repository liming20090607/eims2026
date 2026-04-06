@echo off
chcp 65001 >nul
echo ======================================
echo EIMS2026 BAT 文件整理工具
echo ======================================
echo.
echo 正在将所有 BAT 文件移动到 bat\ 目录...
echo.

:: 创建目标目录
if not exist "bat" mkdir "bat"

:: 计数器
set /a total=0
set /a moved=0

:: 移动所有 BAT 文件（除了这个脚本本身）
for %%f in (*.bat *.BAT) do (
    if not "%%f"=="整理 BAT 文件到子目录.bat" (
        set /a total+=1
        echo [!total!] 移动：%%f
        move "%%f" "bat\" >nul
        if !ERRORLEVEL! EQU 0 (
            echo     ✅ 成功
            set /a moved+=1
        ) else (
            echo     ❌ 失败
        )
    )
)

echo.
echo ======================================
echo 移动完成统计
echo ======================================
echo 处理文件总数：%total%
echo 成功移动文件数：%moved%
echo.
echo 新位置：E:\EIMS2026\bat\
echo ======================================
echo.

:: 询问是否创建启动器
set /p create_launcher=是否在根目录保留快捷启动方式？(Y/N): 
if /i "%create_launcher%"=="Y" (
    echo.
    echo 正在创建快捷启动脚本...
    
    :: 创建常用脚本的快捷方式
    (
        echo @echo off
        echo chcp 65001 ^>nul
        echo title EIMS2026 服务器
        echo cls
        echo echo ========================================
        echo echo   EIMS2026 服务器启动
        echo echo ========================================
        echo echo.
        echo call bat\run.bat
        echo pause
    ) > "run_server.bat"
    
    echo   ✅ 已创建 run_server.bat^（根目录启动服务器）
    
    (
        echo @echo off
        echo chcp 65001 ^>nul
        echo echo ======================================
        echo echo   Git 推送代码到 GitHub/Gitee
        echo echo ======================================
        echo echo.
        echo call bat\push_to_github.bat
        echo pause
    ) > "push_code.bat"
    
    echo   ✅ 已创建 push_code.bat^（根目录推送代码）
)

echo.
echo ======================================
echo 整理完成！
echo ======================================
echo.
echo 📁 新的 BAT 文件位置：bat\
echo 📝 说明：
echo   - 大部分脚本使用相对路径，可直接运行
echo   - 部分部署脚本需要切换到项目根目录执行
echo   - 建议在 bat\ 目录中查看各脚本说明
echo.

pause
