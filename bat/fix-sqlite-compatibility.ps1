# 修复 django-import-export 兼容性的 PowerShell 脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  修复 SQLite 兼容性问题" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$sshCommand = "ssh root@39.106.41.239 `"cd /var/www/eims; source venv/bin/activate; pip install django-import-export==2.0.2; find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; supervisorctl restart eims`""

Write-Host "正在执行 SSH 命令..." -ForegroundColor Yellow
Write-Host ""
Write-Host "请复制以下命令到 PowerShell 执行:" -ForegroundColor Green
Write-Host ""
Write-Host $sshCommand -ForegroundColor White
Write-Host ""
Write-Host "或者手动输入:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. ssh root@39.106.41.239" -ForegroundColor White
Write-Host "2. 输入密码登录" -ForegroundColor White
Write-Host "3. cd /var/www/eims" -ForegroundColor White
Write-Host "4. source venv/bin/activate" -ForegroundColor White
Write-Host "5. pip install django-import-export==2.0.2" -ForegroundColor White
Write-Host "6. find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null" -ForegroundColor White
Write-Host "7. supervisorctl restart eims" -ForegroundColor White
Write-Host ""

Invoke-Expression $sshCommand

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  完成后请按 Ctrl+F5 刷新浏览器" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
