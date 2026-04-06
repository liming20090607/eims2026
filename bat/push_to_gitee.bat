@echo off
chcp 65001 >nul
cls

echo.
echo ========================================
echo   推送到 Gitee
echo ========================================
echo.
echo 远程仓库：https://gitee.com/liming20090607/eims2026.git
echo.
echo 正在推送代码...
echo.

"C:\Program Files\Git\bin\git.exe" push -u gitee master

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   推送成功！
    echo ========================================
    echo.
    echo Gitee 仓库地址:
    echo https://gitee.com/liming20090607/eims2026
    echo.
    echo 请刷新 Gitee 页面查看代码
    echo.
) else (
    echo.
    echo ========================================
    echo   推送失败
    echo ========================================
    echo.
    echo 可能的原因:
    echo - 网络连接问题
    echo - Gitee 账号密码错误
    echo - 仓库权限问题
    echo.
    echo 请检查后重试
    echo.
)

echo 按任意键退出...
pause >nul
