@echo off
echo ========================================
echo   推送代码到 GitHub
echo ========================================
echo.

echo 正在推送代码...
"C:\Program Files\Git\bin\git.exe" push -u origin master

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   推送成功!
    echo ========================================
    echo.
    echo 远程仓库地址:
    echo https://github.com/liming20090607/eims2026
    echo.
    echo 请刷新 GitHub 页面查看代码
) else (
    echo.
    echo ========================================
    echo   推送失败
    echo ========================================
    echo.
    echo 可能的原因:
    echo - 网络连接问题
    echo - GitHub 服务器问题
    echo - 权限问题
    echo.
    echo 请检查后重试
)

echo.
echo 按任意键退出...
pause >nul
