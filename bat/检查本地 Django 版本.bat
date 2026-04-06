@echo off
chcp 65001 >nul
echo ======================================
echo 检查本地 Django 版本
echo ======================================
echo.
echo 正在检查...
echo.

echo ======================================
echo Django 版本信息
echo ======================================
python -m django --version

echo.
echo ======================================
echo Python 版本
echo ======================================
python --version

echo.
echo ======================================
echo 已安装的 Django 包
echo ======================================
pip list | findstr /i django

echo.
echo ======================================
echo requirements.txt 指定版本
echo ======================================
findstr /i "django==" requirements.txt

echo.
echo ======================================
echo 检查完成
echo ======================================
echo.
echo 提示：
echo - 如果显示 5.2，需要降级到 4.2.7
echo - 运行：降级本地 Django 版本.bat
echo.
pause
