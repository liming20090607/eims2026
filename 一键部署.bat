@echo off
chcp 65001 >nul
cls
echo =========================================
echo    EIMS 云服务器自动部署工具
echo =========================================
echo.
echo 正在检查环境...
echo.

REM 检查 Git Bash 是否存在
set "GITBASH=C:\Program Files\Git\bin\bash.exe"
if not exist "%GITBASH%" set "GITBASH=C:\Program Files (x86)\Git\bin\bash.exe"

if not exist "%GITBASH%" (
    echo [错误] 未找到 Git Bash!
    echo.
    echo 请先安装 Git for Windows:
    echo https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

echo [成功] 找到 Git Bash
echo.
echo =========================================
echo 部署步骤:
echo =========================================
echo 1. 设置 MySQL root 密码 (自动)
echo 2. 推送代码到 Gitee (需要确认)
echo 3. 备份服务器数据库 (自动)
echo 4. 拉取代码到服务器 (自动)
echo 5. 导出本地数据 (自动)
echo 6. 同步到服务器 (自动)
echo 7. 重启服务 (自动)
echo =========================================
echo.
echo 注意: 执行过程中需要输入服务器 SSH 密码
echo 请输入后按回车键继续...
echo.
pause

echo.
echo 开始部署...
echo.

REM 切换到项目目录并执行部署脚本
cd /d "%~dp0"
"%GITBASH%" --login -i -c "cd /e/EIMS2026 && bash deploy_all.sh"

echo.
echo =========================================
echo 部署完成!
echo =========================================
echo.
pause
