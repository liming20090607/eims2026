# ⚠️ ️ ⚠️ 警告：这是一个手动执行的脚本 ⚠️ ️ ⚠️
#
# 此脚本会从云服务器同步用户数据到本地数据库。
#
# 重要说明：
# 1. 此脚本不会自动执行，需要超级管理员手动运行
# 2. 执行此操作会将云端数据覆盖到本地
# 3. 执行前请确保已备份本地数据
# 4. 仅在需要恢复本地数据时才使用此脚本
#
# 同步方向：云服务器 → 本地（单向）
# 执行权限：仅限超级管理员
#
# 同步用户账号数据从云服务器到本地
# 使用方法: .\sync_users_data.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   同步用户账号数据从云服务器到本地" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "服务器: 39.106.41.239" -ForegroundColor Yellow
Write-Host "功能: 导出用户数据并导入到本地数据库" -ForegroundColor Yellow
Write-Host ""
Write-Host "注意: 执行过程中需要输入服务器 root 密码" -ForegroundColor Magenta
Write-Host ""

$confirm = Read-Host "是否继续？(y/n)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "操作已取消" -ForegroundColor Yellow
    exit 0
}

# 步骤 1: 在服务器上导出用户数据
Write-Host ""
Write-Host "[步骤 1/3] 导出服务器用户数据..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Gray

$sshCmd = 'ssh root@39.106.41.239 "cd /var/www/eims && source venv/bin/activate && python manage.py dumpdata auth.User auth.Group auth.Permission --indent 2 > /tmp/users_export.json"'

Write-Host "正在连接服务器并导出数据..." -ForegroundColor Gray
Write-Host "请输入服务器 root 密码" -ForegroundColor Magenta
Write-Host ""

Invoke-Expression $sshCmd

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "❌ 导出失败！" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "请检查：" -ForegroundColor Yellow
    Write-Host "  1. 网络连接是否正常" -ForegroundColor White
    Write-Host "  2. SSH 密码是否正确" -ForegroundColor White
    Write-Host "  3. 服务器是否可访问" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "✅ 服务器导出成功" -ForegroundColor Green
Write-Host ""

# 步骤 2: 下载导出的数据文件到本地
Write-Host "[步骤 2/3] 下载数据文件到本地..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Gray

# 创建fixtures目录
$fixturesDir = "eims_app\fixtures"
if (-not (Test-Path $fixturesDir)) {
    New-Item -ItemType Directory -Path $fixturesDir -Force | Out-Null
    Write-Host "已创建目录: $fixturesDir" -ForegroundColor Gray
}

$scpCmd = "scp root@39.106.41.239:/tmp/users_export.json $fixturesDir\users_export.json"

Write-Host "正在下载文件..." -ForegroundColor Gray
Write-Host "请输入服务器 root 密码" -ForegroundColor Magenta
Write-Host ""

Invoke-Expression $scpCmd

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "❌ 下载失败！" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "✅ 文件下载成功" -ForegroundColor Green
Write-Host ""

# 步骤 3: 导入数据到本地数据库
Write-Host "[步骤 3/3] 导入数据到本地数据库..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Gray

$fixturePath = "$fixturesDir\users_export.json"

if (-not (Test-Path $fixturePath)) {
    Write-Host "❌ 文件不存在: $fixturePath" -ForegroundColor Red
    exit 1
}

# 检查文件大小
$fileSize = (Get-Item $fixturePath).Length
Write-Host "文件大小: $fileSize bytes" -ForegroundColor Gray

if ($fileSize -lt 100) {
    Write-Host "⚠️  警告：文件可能为空或损坏！" -ForegroundColor Yellow
    $continue = Read-Host "是否继续导入？(y/n)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 0
    }
}

Write-Host ""
Write-Host "正在导入数据..." -ForegroundColor Gray
Write-Host ""

$loadDataCmd = "python manage.py loaddata $fixturePath"
Invoke-Expression $loadDataCmd

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "❌ 导入失败！" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "可能的原因：" -ForegroundColor Yellow
    Write-Host "  1. 数据格式不匹配" -ForegroundColor White
    Write-Host "  2. 存在ID冲突" -ForegroundColor White
    Write-Host "  3. 依赖模型缺失" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "✅ 数据导入成功" -ForegroundColor Green
Write-Host ""

# 验证导入结果
Write-Host "[验证] 检查导入结果..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Gray
Write-Host ""

python manage.py shell -c "from django.contrib.auth.models import User; from eims_app.models import UserProfile; print(f'用户账号数: {User.objects.count()}'); print(f'用户资料数: {UserProfile.objects.count()}'); users = User.objects.order_by('-id')[:5]; print('\n最新5个用户:'); [print(f'  - {u.username} (ID:{u.id})') for u in users]"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   ✅ 用户数据同步完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "现在您可以访问：" -ForegroundColor Cyan
Write-Host "  用户管理页面: http://127.0.0.1:8000/user-management/" -ForegroundColor White
Write-Host "  Django Admin: http://127.0.0.1:8000/admin/" -ForegroundColor White
Write-Host ""

# 清理临时文件
$cleanup = Read-Host "是否删除临时文件 users_export.json？(y/n)"
if ($cleanup -eq "y" -or $cleanup -eq "Y") {
    Remove-Item $fixturePath -Force
    Write-Host "✅ 已删除临时文件" -ForegroundColor Green
}

Write-Host ""
