# Git 配置测试脚本

Write-Host "========================================" -ForegroundColor Green
Write-Host "  Git 安装检测与配置" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# 检测 Git 是否安装
$gitPath = "C:\Program Files\Git\bin\git.exe"
if (Test-Path $gitPath) {
    Write-Host "✅ Git 已安装到：C:\Program Files\Git" -ForegroundColor Green
    Write-Host ""
    
    # 尝试直接使用完整路径运行 Git
    Write-Host "测试 Git 运行..." -ForegroundColor Yellow
    & "C:\Program Files\Git\bin\git.exe" --version
    Write-Host ""
    
    # 检查是否在 PATH 中
    $gitInPath = Get-Command git -ErrorAction SilentlyContinue
    if ($gitInPath) {
        Write-Host "✅ Git 已添加到 PATH" -ForegroundColor Green
        Write-Host ""
        
        # 显示 Git 版本
        $version = git --version
        Write-Host "Git 版本：$version" -ForegroundColor Cyan
        Write-Host ""
        
        # 检查 Git 配置
        Write-Host "检查 Git 配置：" -ForegroundColor Yellow
        $username = git config --global user.name
        $email = git config --global user.email
        
        if ($username) {
            Write-Host "  用户名：$username" -ForegroundColor Green
        } else {
            Write-Host "  用户名：未配置" -ForegroundColor Red
        }
        
        if ($email) {
            Write-Host "  邮箱：$email" -ForegroundColor Green
        } else {
            Write-Host "  邮箱：未配置" -ForegroundColor Red
        }
        Write-Host ""
        
        # 检查是否在 Git 仓库中
        if (Test-Path ".git") {
            Write-Host "✅ 当前目录是 Git 仓库" -ForegroundColor Green
            Write-Host ""
            
            # 显示 Git 状态
            Write-Host "当前状态：" -ForegroundColor Yellow
            git status --short
        } else {
            Write-Host "⚠️  当前目录不是 Git 仓库" -ForegroundColor Yellow
            Write-Host ""
            
            $response = Read-Host "是否要初始化 Git 仓库？(Y/N)"
            if ($response -eq 'Y' -or $response -eq 'y') {
                Write-Host ""
                Write-Host "初始化 Git 仓库..." -ForegroundColor Yellow
                
                # 创建 .gitignore
                if (-not (Test-Path ".gitignore")) {
                    Write-Host "创建 .gitignore 文件..." -ForegroundColor Green
                    @'
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
db.sqlite3
media/
staticfiles/
.env
*.log
.DS_Store
Thumbs.db
'@ | Out-File -FilePath ".gitignore" -Encoding utf8
                    Write-Host "✅ .gitignore 已创建" -ForegroundColor Green
                }
                
                # 初始化 Git
                git init
                Write-Host "✅ Git 仓库已初始化" -ForegroundColor Green
                
                # 添加文件
                Write-Host ""
                Write-Host "添加文件到 Git..." -ForegroundColor Yellow
                git add .
                Write-Host "✅ 文件已添加" -ForegroundColor Green
                
                # 配置用户信息（如果未配置）
                if (-not $username) {
                    Write-Host ""
                    $username = Read-Host "请输入 Git 用户名"
                    git config --global user.name $username
                    Write-Host "✅ 用户名已配置" -ForegroundColor Green
                }
                
                if (-not $email) {
                    Write-Host ""
                    $email = Read-Host "请输入 Git 邮箱"
                    git config --global user.email $email
                    Write-Host "✅ 邮箱已配置" -ForegroundColor Green
                }
                
                # 首次提交
                Write-Host ""
                $commitMsg = Read-Host "请输入提交信息（默认：Initial commit）"
                if (-not $commitMsg) {
                    $commitMsg = "Initial commit"
                }
                
                git commit -m $commitMsg
                Write-Host "✅ 首次提交完成" -ForegroundColor Green
                
                Write-Host ""
                Write-Host "========================================" -ForegroundColor Green
                Write-Host "  Git 仓库初始化完成！" -ForegroundColor Green
                Write-Host "========================================" -ForegroundColor Green
                Write-Host ""
                Write-Host "下一步：" -ForegroundColor Yellow
                Write-Host "1. 在 GitHub 或 Gitee 创建远程仓库" -ForegroundColor White
                Write-Host "2. 运行：git remote add origin 仓库地址" -ForegroundColor White
                Write-Host "3. 运行：git push -u origin main" -ForegroundColor White
            }
        }
    } else {
        Write-Host "❌ Git 未添加到 PATH" -ForegroundColor Red
        Write-Host ""
        Write-Host "解决方案：" -ForegroundColor Yellow
        Write-Host "1. 关闭所有 PowerShell 和 CMD 窗口" -ForegroundColor White
        Write-Host "2. 重新打开新的 PowerShell 窗口" -ForegroundColor White
        Write-Host "3. 重新运行此脚本" -ForegroundColor White
        Write-Host ""
        Write-Host "或者使用完整路径运行 Git：" -ForegroundColor Cyan
        Write-Host "  & 'C:\Program Files\Git\bin\git.exe' --version" -ForegroundColor Gray
    }
} else {
    Write-Host "❌ Git 未安装" -ForegroundColor Red
    Write-Host ""
    Write-Host "请重新安装 Git：" -ForegroundColor Yellow
    Write-Host "1. 访问：https://git-scm.com/download/win" -ForegroundColor White
    Write-Host "2. 下载并运行安装程序" -ForegroundColor White
    Write-Host "3. 安装时选择 'Git from the command line'" -ForegroundColor White
    Write-Host "4. 完成安装后重新运行此脚本" -ForegroundColor White
    Write-Host ""
    Write-Host "查看详细说明：Git 安装指南.md" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
