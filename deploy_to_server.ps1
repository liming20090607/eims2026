# 用户账号管理功能部署脚本
# 在 PowerShell 中运行：.\deploy_to_server.ps1

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "用户账号管理功能部署" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

$SERVER_IP = "39.106.41.239"
$SERVER_USER = "root"
$PROJECT_PATH = "/var/www/eims"

Write-Host "📤 开始上传文件到 $SERVER_USER@$SERVER_IP" -ForegroundColor Green
Write-Host ""

# 文件列表
$files = @(
    @{Source="eims_app\forms\form_user_management.py"; Dest="$PROJECT_PATH/eims_app/forms/"},
    @{Source="eims_app\views\views_user_management.py"; Dest="$PROJECT_PATH/eims_app/views/"},
    @{Source="eims_app\templates\eims_app\user_management.html"; Dest="$PROJECT_PATH/eims_app/templates/eims_app/"},
    @{Source="eims_app\templatetags\custom_filters.py"; Dest="$PROJECT_PATH/eims_app/templatetags/"},
    @{Source="eims_app\urls.py"; Dest="$PROJECT_PATH/eims_app/"},
    @{Source="eims_app\templates\base\base.html"; Dest="$PROJECT_PATH/eims_app/templates/base/"}
)

$successCount = 0
$failCount = 0

# 上传文件
for ($i = 0; $i -lt $files.Count; $i++) {
    $file = $files[$i]
    $num = $i + 1
    
    Write-Host "[$num/6] 上传 $($file.Source)..." -ForegroundColor Yellow
    
    $cmd = "scp `"$($file.Source)`" $SERVER_USER@$SERVER_IP`:$($file.Dest)"
    Write-Host "执行：$cmd" -ForegroundColor Gray
    
    # 执行 scp 命令
    & cmd /c "scp `"$($file.Source)`" $SERVER_USER@$SERVER_IP`:$($file.Dest)"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ 成功" -ForegroundColor Green
        $successCount++
    } else {
        Write-Host "  ✗ 失败" -ForegroundColor Red
        $failCount++
    }
    
    Write-Host ""
}

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "上传完成！" -ForegroundColor Cyan
Write-Host "成功：$successCount 个文件" -ForegroundColor Green
Write-Host "失败：$failCount 个文件" -ForegroundColor $(if ($failCount -eq 0) {"Green"} else {"Red"})
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

if ($failCount -eq 0) {
    Write-Host "✅ 所有文件上传成功！" -ForegroundColor Green
    Write-Host ""
    Write-Host "下一步操作：" -ForegroundColor Yellow
    Write-Host "1. SSH 登录服务器：ssh $SERVER_USER@$SERVER_IP" -ForegroundColor White
    Write-Host "2. 执行以下命令：" -ForegroundColor White
    Write-Host ""
    Write-Host "   cd $PROJECT_PATH" -ForegroundColor Cyan
    Write-Host "   source venv/bin/activate" -ForegroundColor Cyan
    Write-Host "   python manage.py collectstatic --noinput" -ForegroundColor Cyan
    Write-Host "   python manage.py check" -ForegroundColor Cyan
    Write-Host "   sudo supervisorctl restart eims" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host "❌ 部分文件上传失败，请检查网络连接或密码是否正确" -ForegroundColor Red
    Write-Host ""
    Write-Host "建议：" -ForegroundColor Yellow
    Write-Host "1. 确认服务器密码正确" -ForegroundColor White
    Write-Host "2. 确认服务器目录存在：/var/www/eims/eims_app/templates/eims_app/" -ForegroundColor White
    Write-Host "3. 使用 SSH 手动创建目录后再试" -ForegroundColor White
}

Write-Host ""
Write-Host "按任意键继续..." -ForegroundColor Gray
# $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
