@echo off
chcp 65001 >nul
REM =========================================
REM EIMS2026 - 一键自动化部署 (Windows版)
REM =========================================

set SERVER_IP=39.106.41.239
set SERVER_USER=root
set SERVER_DIR=/var/www/eims
set GITEE_REMOTE=gitee
set BRANCH=master

echo =========================================
echo   EIMS2026 - 一键自动化部署
echo   时间: %date% %time%
echo =========================================

REM 1. 推送到 Gitee
echo.
echo [1/4] 推送代码到 Gitee...
git add -A
git commit -m "auto: deploy %date% %time%"
if errorlevel 1 echo No changes to commit
git push %GITEE_REMOTE% %BRANCH%
echo OK 代码推送完成

REM 2. SSH 到服务器执行部署
echo.
echo [2/4] 连接到云服务器并拉取代码...
ssh %SERVER_USER%@%SERVER_IP% "cd %SERVER_DIR% && git pull %GITEE_REMOTE% %BRANCH% && echo 'OK 代码拉取完成'"
echo OK 代码更新完成

REM 3. 激活虚拟环境并迁移数据库
echo.
echo [3/4] 数据库迁移...
ssh %SERVER_USER%@%SERVER_IP% "cd %SERVER_DIR% && source venv/bin/activate && python manage.py makemigrations && python manage.py migrate && echo 'OK 数据库迁移完成'"
echo OK 数据库迁移完成

REM 4. 收集静态文件并重启服务
echo.
echo [4/4] 收集静态文件并重启服务...
ssh %SERVER_USER%@%SERVER_IP% "cd %SERVER_DIR% && source venv/bin/activate && python manage.py collectstatic --noinput && supervisorctl restart eims && echo 'OK 静态文件收集完成' && echo 'OK 服务重启完成'"
echo OK 服务重启完成

echo.
echo =========================================
echo   OK 部署完成！
echo   时间: %date% %time%
echo =========================================
echo.
echo 验证部署：
echo   1. 查看服务状态: ssh %SERVER_USER%@%SERVER_IP% "supervisorctl status eims"
echo   2. 查看日志: ssh %SERVER_USER%@%SERVER_IP% "tail -f %SERVER_DIR%/logs/gunicorn.log"
echo   3. 浏览器访问: http://%SERVER_IP%
echo.
pause
