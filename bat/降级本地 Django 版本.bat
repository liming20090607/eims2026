@echo off
chcp 65001 >nul
echo ======================================
echo 降级本地 Django 版本到 4.2.7
echo ======================================
echo.
echo 当前环境信息：
echo.

echo ======================================
echo 步骤 1: 检查当前版本
echo ======================================
python -m django --version

echo.
echo requirements.txt 指定版本：
findstr /i \"django==\" requirements.txt

echo.
echo ======================================
echo 开始降级...
echo ======================================
echo.

echo [1/4] 卸载当前 Django...
python -m pip uninstall -y django
if %ERRORLEVEL% EQU 0 (
    echo   ✅ Django 已卸载
) else (
    echo   ❌ 卸载失败
    goto error
)

echo.
echo [2/4] 安装 Django 4.2.7...
pip install django==4.2.7
if %ERRORLEVEL% EQU 0 (
    echo   ✅ Django 4.2.7 已安装
) else (
    echo   ❌ 安装失败
    goto error
)

echo.
echo [3/4] 验证安装...
python -m django --version

echo.
echo [4/4] 检查 Django 包...
pip list | findstr /i django

echo.
echo ======================================
echo 降级完成！
echo ======================================
echo.
echo 当前 Django 版本应该是：4.2.7
echo.
echo 下一步：
echo 1. 测试项目：python manage.py runserver
echo 2. 访问 Admin: http://localhost:8000/admin/
echo 3. 检查样式是否正常（应该无黑块）
echo.
echo 如果版本不是 4.2.7，请重新运行此脚本
echo.
pause
exit /b 0

:error
echo.
echo ======================================
echo 错误！
echo ======================================
echo.
echo 降级过程中出现错误
echo 请检查：
echo 1. 网络连接
echo 2. pip 配置
echo 3. Python 环境
echo.
pause
