@echo off
chcp 65001 >nul
echo ======================================
echo 手机端优化 - 完整部署流程
echo ======================================
echo.
echo 优化内容：
echo 1. Viewport 调整为 0.7 倍缩放
echo 2. 手机端字体缩小到 12px
echo 3. 卡片、按钮等元素进一步缩小
echo 4. 侧边栏宽度调整到 220px
echo.
echo 请选择部署方式：
echo A. 自动上传并部署（推荐）
echo B. 手动 SSH 登录执行
echo C. 只上传文件，稍后手动部署
echo.
set /p choice=请输入选项 (A/B/C): 

if /i "%choice%"=="A" goto auto_deploy
if /i "%choice%"=="B" goto ssh_manual
if /i "%choice%"=="C" goto upload_only
goto end

:auto_deploy
echo.
echo ======================================
echo 自动上传并部署
echo ======================================
echo.
echo 请输入服务器密码（root 用户的密码）：
echo.

echo [1/2] 上传 base.html...
scp eims_app\templates\base\base.html root@39.106.41.239:/var/www/eims/eims_app/templates/base/
if %ERRORLEVEL% EQU 0 (
    echo   ✅ base.html 上传成功
) else (
    echo   ❌ base.html 上传失败
    goto upload_error
)
echo.

echo [2/2] 上传 style.css...
scp static\css\style.css root@39.106.41.239:/var/www/eims/static/css/
if %ERRORLEVEL% EQU 0 (
    echo   ✅ style.css 上传成功
) else (
    echo   ❌ style.css 上传失败
    goto upload_error
)
echo.

echo ======================================
echo 文件上传完成！正在执行部署命令...
echo ======================================
echo.

ssh root@39.106.41.239 @"
cd /var/www/eims
source venv/bin/activate

echo '步骤 1: 重启服务...'
supervisorctl restart eims

echo '步骤 2: 查看服务状态...'
supervisorctl status eims

echo '======================================'
echo '部署完成！'
echo '======================================'
"@

echo.
echo ======================================
echo 部署成功！
echo ======================================
echo.
echo 请在手机上测试：
echo 1. 访问：http://39.106.41.239:8000/
echo 2. 清除浏览器缓存
echo 3. 查看显示效果
echo.
goto end

:ssh_manual
echo.
echo ======================================
echo 手动 SSH 登录执行部署
echo ======================================
echo.
echo 请按以下步骤操作：
echo.
echo 1. SSH 登录服务器
echo    ssh root@39.106.41.239
echo.
echo 2. 进入项目目录
echo    cd /var/www/eims
echo.
echo 3. 激活虚拟环境
echo    source venv/bin/activate
echo.
echo 4. 重启服务
echo    supervisorctl restart eims
echo.
echo 5. 查看服务状态
echo    supervisorctl status eims
echo.
echo 6. 退出
echo    exit
echo.

echo 是否现在 SSH 登录？(Y/N)
set /p login=
if /i "%login%"=="Y" (
    ssh root@39.106.41.239
)
goto end

:upload_only
echo.
echo ======================================
echo 只上传文件
echo ======================================
echo.
echo 请输入服务器密码（root 用户的密码）：
echo.

echo [1/2] 上传 base.html...
scp eims_app\templates\base\base.html root@39.106.41.239:/var/www/eims/eims_app/templates/base/
if %ERRORLEVEL% EQU 0 (echo   ✅ 成功) else (echo   ❌ 失败)
echo.

echo [2/2] 上传 style.css...
scp static\css\style.css root@39.106.41.239:/var/www/eims/static/css/
if %ERRORLEVEL% EQU 0 (echo   ✅ 成功) else (echo   ❌ 失败)
echo.

echo ======================================
echo 文件上传完成！
echo ======================================
echo.
echo 稍后请 SSH 登录执行：
echo    cd /var/www/eims
echo    source venv/bin/activate
echo    supervisorctl restart eims
echo.
goto end

:upload_error
echo.
echo ======================================
echo 上传失败！
echo ======================================
echo.
echo 请检查：
echo 1. 密码是否正确
echo 2. 网络连接是否正常
echo 3. 服务器是否可访问
echo.

:end
pause
