# 在服务器上创建缺失的目录
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "在服务器上创建缺失的目录" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

$SERVER_IP = "39.106.41.239"
$SERVER_USER = "root"

Write-Host "正在 SSH 连接到 $SERVER_USER@$SERVER_IP..." -ForegroundColor Yellow
Write-Host ""
Write-Host "请输入服务器密码（root 用户的密码）：" -ForegroundColor Yellow
Write-Host ""

# 执行 SSH 命令创建目录
ssh root@39.106.41.239 @"
mkdir -p /var/www/eims/eims_app/templates/eims_app
chown -R admin:admin /var/www/eims/eims_app/templates/eims_app
chmod 755 /var/www/eims/eims_app/templates/eims_app
echo "目录创建成功！"
ls -la /var/www/eims/eims_app/templates/
"@

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "完成！" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步：" -ForegroundColor Yellow
Write-Host "1. 在 WinSCP 中刷新右侧窗口（按 F5）" -ForegroundColor White
Write-Host "2. 应该能看到新建的 eims_app 文件夹" -ForegroundColor White
Write-Host "3. 上传 user_management.html 到该文件夹" -ForegroundColor White
Write-Host ""
Write-Host "按任意键继续..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
