# EIMS 云服务器一键部署 - PowerShell 版本
# 使用方法：右键此文件 → 使用 PowerShell 运行

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "   EIMS 云服务器自动部署工具" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 配置变量
$ServerUser = "root"
$ServerIP = "39.106.41.239"
$ServerPath = "/var/www/eims"
$MySqlPassword = "root123"
$ProjectPath = "e:\EIMS2026"

# 切换到项目目录
Set-Location $ProjectPath

Write-Host "部署步骤：" -ForegroundColor Yellow
Write-Host "1. 设置 MySQL root 密码" -ForegroundColor White
Write-Host "2. 推送代码到 Gitee" -ForegroundColor White
Write-Host "3. 同步到服务器" -ForegroundColor White
Write-Host ""
Write-Host "注意：执行过程中需要输入服务器 SSH 密码" -ForegroundColor Yellow
Write-Host ""

$confirm = Read-Host "是否开始部署？(y/n)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "已取消部署" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "=== 第一步：上传 MySQL 密码设置脚本 ===" -ForegroundColor Green
scp setup_mysql_auto.sh "${ServerUser}@${ServerIP}:/root/setup_mysql_auto.sh"

Write-Host ""
Write-Host "=== 第二步：设置 MySQL 密码 ===" -ForegroundColor Green
ssh "${ServerUser}@${ServerIP}" "bash /root/setup_mysql_auto.sh"

Write-Host ""
Write-Host "=== 第三步：推送代码到 Gitee ===" -ForegroundColor Green
$gitConfirm = Read-Host "是否提交并推送代码到 Gitee？(y/n)"
if ($gitConfirm -eq "y" -or $gitConfirm -eq "Y") {
    git add .
    git commit -m "Auto deploy - $(Get-Date -Format 'yyyy-MM-dd-HHmmss')"
    git push origin main
    Write-Host "✓ 代码已推送到 Gitee" -ForegroundColor Green
} else {
    Write-Host "跳过代码推送（假设已推送）" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== 第四步：备份服务器数据库 ===" -ForegroundColor Green
$backupFile = "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql"
ssh "${ServerUser}@${ServerIP}" "cd ${ServerPath} && MYSQL_PWD=${MySqlPassword} mysqldump -u root eims > ${backupFile}"
Write-Host "✓ 服务器数据库已备份: ${backupFile}" -ForegroundColor Green

Write-Host ""
Write-Host "=== 第五步：从 Gitee 拉取代码 ===" -ForegroundColor Green
ssh "${ServerUser}@${ServerIP}" "cd ${ServerPath} && git pull origin main"
Write-Host "✓ 代码已同步" -ForegroundColor Green

Write-Host ""
Write-Host "=== 第六步：导出本地数据 ===" -ForegroundColor Green
python manage.py dumpdata --natural-foreign --natural-primary --indent=2 > local_data.json
Write-Host "✓ 本地数据已导出" -ForegroundColor Green

Write-Host ""
Write-Host "=== 第七步：传输数据到服务器 ===" -ForegroundColor Green
scp local_data.json "${ServerUser}@${ServerIP}:${ServerPath}/local_data.json"
Write-Host "✓ 数据已传输" -ForegroundColor Green

Write-Host ""
Write-Host "=== 第八步：导入数据到 MySQL ===" -ForegroundColor Green
ssh "${ServerUser}@${ServerIP}" "cd ${ServerPath} && source venv/bin/activate && python manage.py loaddata local_data.json"
Write-Host "✓ 数据导入完成" -ForegroundColor Green

Write-Host ""
Write-Host "=== 第九步：同步媒体文件 ===" -ForegroundColor Green
# 注意：PowerShell 的 Copy-Item 通过 SSH 比较复杂，这里使用 scp
scp -r media/* "${ServerUser}@${ServerIP}:${ServerPath}/media/"
Write-Host "✓ 媒体文件同步完成" -ForegroundColor Green

Write-Host ""
Write-Host "=== 第十步：收集静态文件 ===" -ForegroundColor Green
ssh "${ServerUser}@${ServerIP}" "cd ${ServerPath} && source venv/bin/activate && python manage.py collectstatic --noinput"
Write-Host "✓ 静态文件收集完成" -ForegroundColor Green

Write-Host ""
Write-Host "=== 第十一步：数据库迁移 ===" -ForegroundColor Green
ssh "${ServerUser}@${ServerIP}" "cd ${ServerPath} && source venv/bin/activate && python manage.py migrate --noinput"
Write-Host "✓ 数据库迁移完成" -ForegroundColor Green

Write-Host ""
Write-Host "=== 第十二步：重启服务 ===" -ForegroundColor Green
ssh "${ServerUser}@${ServerIP}" "supervisorctl restart eims"
ssh "${ServerUser}@${ServerIP}" "systemctl restart nginx"
Write-Host "✓ 服务已重启" -ForegroundColor Green

Write-Host ""
Write-Host "=== 第十三步：清理临时文件 ===" -ForegroundColor Green
Remove-Item local_data.json -ErrorAction SilentlyContinue
ssh "${ServerUser}@${ServerIP}" "rm -f ${ServerPath}/local_data.json"
Write-Host "✓ 临时文件已清理" -ForegroundColor Green

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "✓ 部署完成！" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 服务器信息：" -ForegroundColor Yellow
Write-Host "  地址: http://${ServerIP}" -ForegroundColor White
Write-Host "  数据库: eims (root/${MySqlPassword})" -ForegroundColor White
Write-Host "  代码路径: ${ServerPath}" -ForegroundColor White
Write-Host ""
Write-Host "📋 验证步骤：" -ForegroundColor Yellow
Write-Host "  1. 浏览器访问: http://${ServerIP}" -ForegroundColor White
Write-Host "  2. 检查服务: ssh ${ServerUser}@${ServerIP}" -ForegroundColor White
Write-Host ""
Write-Host "🔄 备份文件：" -ForegroundColor Yellow
Write-Host "  服务器: ${ServerPath}/${backupFile}" -ForegroundColor White
Write-Host ""

Read-Host "按回车键退出"
