# Git Push Script
Write-Host "========================================" -ForegroundColor Green
Write-Host "  推送代码到 GitHub" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "当前目录：$(Get-Location)" -ForegroundColor Yellow
Write-Host ""

Write-Host "正在推送代码..." -ForegroundColor Yellow
& "C:\Program Files\Git\bin\git.exe" push -u origin master

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ 推送成功！" -ForegroundColor Green
    Write-Host ""
    Write-Host "远程仓库：" -ForegroundColor Cyan
    Write-Host "https://github.com/liming20090607/eims2026" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ 推送失败" -ForegroundColor Red
    Write-Host "请检查网络连接和仓库权限" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "按回车键退出..." -ForegroundColor Gray
Read-Host
