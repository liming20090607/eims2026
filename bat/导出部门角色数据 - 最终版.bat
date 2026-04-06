@echo off
chcp 65001 >nul
echo ======================================
echo EIMS 数据迁移工具 - 导出部门和角色
echo ======================================
echo.

REM 获取项目根目录
set PROJECT_ROOT=%~dp0..
cd /d "%PROJECT_ROOT%"

echo 📋 正在导出数据...
echo 当前目录：%CD%
echo.

echo [1/4] 导出部门数据...
python manage.py dumpdata eims_app.Department --indent 2 > department_data.json
if %ERRORLEVEL% EQU 0 (
    echo   ✅ 部门数据导出成功
    for %%A in (department_data.json) do echo   📊 文件大小：%%~zA 字节
) else (
    echo   ❌ 部门数据导出失败
    echo.
    echo 错误信息：
    echo   1. 检查 Django 环境是否正确
    echo   2. 检查 eims_app 是否已安装
    echo   3. 查看上方错误详情
    pause
    exit /b 1
)

echo.
echo [2/4] 导出角色数据...
python manage.py dumpdata eims_app.Role --indent 2 > role_data.json
if %ERRORLEVEL% EQU 0 (
    echo   ✅ 角色数据导出成功
    for %%A in (role_data.json) do echo   📊 文件大小：%%~zA 字节
) else (
    echo   ❌ 角色数据导出失败
    echo.
    echo 错误信息：
    echo   1. 检查 Django 环境是否正确
    echo   2. 检查 eims_app 是否已安装
    echo   3. 查看上方错误详情
    pause
    exit /b 1
)

echo.
echo [3/4] 验证导出文件...
if exist department_data.json (
    echo   ✅ department_data.json 已生成
) else (
    echo   ❌ department_data.json 未生成
    pause
    exit /b 1
)

if exist role_data.json (
    echo   ✅ role_data.json 已生成
) else (
    echo   ❌ role_data.json 未生成
    pause
    exit /b 1
)

echo.
echo [4/4] 准备上传到服务器...
echo.
echo 请输入服务器 IP（默认：39.106.41.239）：
set /p SERVER_IP=
if "%SERVER_IP%"=="" set SERVER_IP=39.106.41.239

echo.
echo 正在上传文件到 %SERVER_IP%...
echo.

scp department_data.json root@%SERVER_IP%:/root/
if %ERRORLEVEL% EQU 0 (
    echo   ✅ 部门数据上传成功
) else (
    echo   ❌ 部门数据上传失败，请检查 SSH 连接
    goto :manual
)

scp role_data.json root@%SERVER_IP%:/root/
if %ERRORLEVEL% EQU 0 (
    echo   ✅ 角色数据上传成功
) else (
    echo   ❌ 角色数据上传失败，请检查 SSH 连接
    goto :manual
)

echo.
echo ======================================
echo ✅ 数据导出和上传完成！
echo ======================================
echo.
echo 📊 导出统计：
echo   部门数据：已导出
echo   角色数据：已导出
echo.
echo 📁 文件位置：
echo   本地：%CD%
echo   服务器：root@%SERVER_IP%:/root/
echo.
echo ======================================
echo 下一步操作：
echo ======================================
echo.
echo 方式 1：自动 SSH 登录并导入（推荐）
echo   按任意键继续，将自动 SSH 登录服务器并执行导入
echo.
echo 方式 2：手动导入
echo   SSH 登录服务器后执行：
echo     cd /var/www/eims
echo     source venv/bin/activate
echo     python manage.py loaddata /root/department_data.json
echo     python manage.py loaddata /root/role_data.json
echo.

pause >nul
echo.
echo ======================================
echo 正在 SSH 登录服务器...
echo ======================================
echo.

ssh root@%SERVER_IP% "cd /var/www/eims; source venv/bin/activate; python manage.py loaddata /root/department_data.json; python manage.py loaddata /root/role_data.json; python manage.py shell -c 'from eims_app.models import Department, Role; print(f\"导入完成 - 部门：{Department.objects.count()} 条，角色：{Role.objects.count()} 条\")'"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ======================================
    echo ✅ 迁移完成！
    echo ======================================
) else (
    echo.
    echo ======================================
    echo ⚠️ 自动导入失败，请手动导入
    echo ======================================
    goto :manual
)

echo.
pause
exit /b 0

:manual
echo.
echo ======================================
echo 手动导入说明
echo ======================================
echo.
echo 1. SSH 登录服务器：
echo    ssh root@%SERVER_IP%
echo.
echo 2. 进入项目目录：
echo    cd /var/www/eims
echo.
echo 3. 激活虚拟环境：
echo    source venv/bin/activate
echo.
echo 4. 导入部门数据：
echo    python manage.py loaddata /root/department_data.json
echo.
echo 5. 导入角色数据：
echo    python manage.py loaddata /root/role_data.json
echo.
echo 6. 验证导入：
echo    python manage.py shell -c "from eims_app.models import Department, Role; print(f'部门：{Department.objects.count()}, 角色：{Role.objects.count()}')"
echo.

pause
