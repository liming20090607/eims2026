# EIMS 服务器快速修复工具
# 使用方法：双击运行或在 PowerShell 中执行
# .\一键上传并执行修复脚本.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  EIMS 服务器一键修复工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$serverIP = "39.106.41.239"
$username = "admin"
$scriptPath = "E:\EIMS2026\bat\服务器诊断与修复-admin 用.sh"

Write-Host "服务器：$serverIP" -ForegroundColor Yellow
Write-Host "用户名：$username" -ForegroundColor Yellow
Write-Host ""

# Step 1: 测试连接
Write-Host "[1/3] 测试服务器连接..." -ForegroundColor Cyan
try {
    $testConnection = Test-NetConnection $serverIP -Port 22 -InformationLevel Quiet
    if ($testConnection) {
        Write-Host "  ✅ SSH 端口 22 可连接" -ForegroundColor Green
    } else {
        Write-Host "  ❌ 无法连接到服务器，请检查网络或 SSH 服务" -ForegroundColor Red
        Write-Host "  按任意键退出..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 1
    }
} catch {
    Write-Host "  ❌ 连接测试失败：$_" -ForegroundColor Red
    Write-Host "  按任意键退出..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}
Write-Host ""

# Step 2: 上传脚本
Write-Host "[2/3] 上传修复脚本到服务器..." -ForegroundColor Cyan

# 检查 scp 是否可用
try {
    $scpCommand = Get-Command scp -ErrorAction Stop
    Write-Host "  ✅ 找到 scp 命令" -ForegroundColor Green
} catch {
    Write-Host "  ❌ 未找到 scp 命令，请确保已安装 OpenSSH 客户端" -ForegroundColor Red
    Write-Host "  安装方法：设置 -> 应用 -> 可选功能 -> 添加 OpenSSH 客户端" -ForegroundColor Yellow
    Write-Host "  按任意键退出..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# 上传脚本
Write-Host ""
Write-Host "  正在上传脚本..." -ForegroundColor Yellow
Write-Host "  本地：$scriptPath" -ForegroundColor Gray
Write-Host "  远程：/tmp/服务器诊断与修复-admin 用.sh" -ForegroundColor Gray
Write-Host ""

# 执行 scp 上传
$localScriptPath = Join-Path $PSScriptRoot "bat\服务器诊断与修复-admin 用.sh"
scp $localScriptPath "${username}@${serverIP}:/tmp/服务器诊断与修复-admin 用.sh"

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ 脚本上传成功！" -ForegroundColor Green
} else {
    Write-Host "  ❌ 脚本上传失败" -ForegroundColor Red
    Write-Host "  请手动输入密码进行上传..." -ForegroundColor Yellow
    Write-Host ""
    
    # 提供手动命令
    Write-Host "  请在 PowerShell 中执行以下命令：" -ForegroundColor Cyan
    Write-Host "  scp $localScriptPath ${username}@${serverIP}:/tmp/服务器诊断与修复-admin 用.sh" -ForegroundColor White
    Write-Host ""
}

Write-Host ""

# Step 3: 提供 SSH 登录命令
Write-Host "[3/3] 登录服务器并执行修复脚本" -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  下一步操作" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "请在 PowerShell 中执行以下命令登录服务器：" -ForegroundColor Yellow
Write-Host ""
Write-Host "  ssh ${username}@${serverIP}" -ForegroundColor White
Write-Host ""
Write-Host "登录后执行以下命令：" -ForegroundColor Yellow
Write-Host ""
Write-Host "  chmod +x /tmp/服务器诊断与修复-admin 用.sh" -ForegroundColor White
Write-Host "  bash /tmp/服务器诊断与修复-admin 用.sh" -ForegroundColor White
Write-Host ""
Write-Host "然后选择选项 1（启动 Supervisor 和 Gunicorn）" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 询问是否立即登录
Write-Host "是否现在打开 SSH 登录窗口？(Y/N)" -ForegroundColor Yellow
$answer = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

if ($answer.Character -eq 'Y' -or $answer.Character -eq 'y') {
    Write-Host ""
    Write-Host "正在打开 SSH 登录..." -ForegroundColor Cyan
    Start-Process "ssh" -ArgumentList "${username}@${serverIP}"
}

Write-Host ""
Write-Host "提示：修复完成后，别忘了配置阿里云安全组（端口 8000）！" -ForegroundColor Green
Write-Host ""
Write-Host "按任意键退出..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
