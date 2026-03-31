# Git 远程仓库配置助手 (PowerShell 版本)

Write-Host "========================================" -ForegroundColor Green
Write-Host "  Git 远程仓库配置助手" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# 检查 Git
try {
    $gitVersion = & "C:\Program Files\Git\bin\git.exe" --version
    Write-Host "✅ Git 已安装：$gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git 未安装或无法运行" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit
}

# 检查是否在 Git 仓库中
if (-not (Test-Path ".git")) {
    Write-Host "❌ 当前目录不是 Git 仓库" -ForegroundColor Red
    Write-Host "请先运行：git init" -ForegroundColor Yellow
    Read-Host "按回车键退出"
    exit
}

Write-Host "✅ 当前目录是 Git 仓库" -ForegroundColor Green
Write-Host ""

# 检查是否已配置远程
$remote = Get-Content .git\config | Select-String "url ="
if ($remote) {
    Write-Host "⚠️  已存在远程仓库配置：" -ForegroundColor Yellow
    & "C:\Program Files\Git\bin\git.exe" remote -v
    Write-Host ""
    $change = Read-Host "是否要修改远程仓库地址？(Y/N)"
    if ($change -eq 'Y' -or $change -eq 'y') {
        & "C:\Program Files\Git\bin\git.exe" remote remove origin
        Write-Host "✅ 已删除原有远程仓库配置" -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Host "保持原有配置" -ForegroundColor Cyan
        Read-Host "按回车键退出"
        exit
    }
}

Write-Host "请选择远程仓库平台：" -ForegroundColor Yellow
Write-Host "----------------------------------------"
Write-Host "1. GitHub (https://github.com)"
Write-Host "2. Gitee 码云 (https://gitee.com)"
Write-Host "3. GitLab (https://gitlab.com)"
Write-Host "4. 其他/自定义"
Write-Host "5. 跳过配置"
Write-Host ""
$platform = Read-Host "请输入选项 (1-5)"

Write-Host ""

switch ($platform) {
    "1" {
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "  GitHub 仓库创建指南" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "请按以下步骤操作：" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "1. 访问：https://github.com/new"
        Write-Host "2. 输入仓库名：eims2026"
        Write-Host "3. 选择可见性："
        Write-Host "   - Private（私有，仅自己可见）"
        Write-Host "   - Public（公开，所有人可见）"
        Write-Host "4. 不要勾选任何初始化选项"
        Write-Host "5. 点击 'Create repository'"
        Write-Host ""
        Write-Host "创建完成后，复制仓库地址（HTTPS）：" -ForegroundColor Yellow
        Write-Host "格式：https://github.com/你的用户名/eims2026.git" -ForegroundColor Gray
        Write-Host ""
        $repoUrl = Read-Host "请输入仓库地址"
        
        while ([string]::IsNullOrWhiteSpace($repoUrl)) {
            Write-Host "❌ 未输入地址" -ForegroundColor Red
            $repoUrl = Read-Host "请重新输入仓库地址"
        }
    }
    
    "2" {
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "  Gitee 仓库创建指南" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "请按以下步骤操作：" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "1. 访问：https://gitee.com/new"
        Write-Host "2. 输入仓库名：eims2026"
        Write-Host "3. 选择可见性："
        Write-Host "   - 私有（仅自己可见）"
        Write-Host "   - 公开（所有人可见）"
        Write-Host "4. 不要勾选任何初始化选项"
        Write-Host "5. 点击 '创建'"
        Write-Host ""
        Write-Host "创建完成后，复制仓库地址（HTTPS）：" -ForegroundColor Yellow
        Write-Host "格式：https://gitee.com/你的用户名/eims2026.git" -ForegroundColor Gray
        Write-Host ""
        $repoUrl = Read-Host "请输入仓库地址"
        
        while ([string]::IsNullOrWhiteSpace($repoUrl)) {
            Write-Host "❌ 未输入地址" -ForegroundColor Red
            $repoUrl = Read-Host "请重新输入仓库地址"
        }
    }
    
    "3" {
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "  GitLab 仓库创建指南" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "请按以下步骤操作：" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "1. 访问：https://gitlab.com/projects/new"
        Write-Host "2. 输入项目名：eims2026"
        Write-Host "3. 选择可见性："
        Write-Host "   - Private（私有）"
        Write-Host "   - Public（公开）"
        Write-Host "4. 不要勾选 'Initialize repository with README'"
        Write-Host "5. 点击 'Create project'"
        Write-Host ""
        Write-Host "创建完成后，复制仓库地址（HTTPS）：" -ForegroundColor Yellow
        Write-Host "格式：https://gitlab.com/你的用户名/eims2026.git" -ForegroundColor Gray
        Write-Host ""
        $repoUrl = Read-Host "请输入仓库地址"
        
        while ([string]::IsNullOrWhiteSpace($repoUrl)) {
            Write-Host "❌ 未输入地址" -ForegroundColor Red
            $repoUrl = Read-Host "请重新输入仓库地址"
        }
    }
    
    "4" {
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "  自定义远程仓库" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        $repoUrl = Read-Host "请输入远程仓库地址"
        
        while ([string]::IsNullOrWhiteSpace($repoUrl)) {
            Write-Host "❌ 未输入地址" -ForegroundColor Red
            $repoUrl = Read-Host "请重新输入远程仓库地址"
        }
    }
    
    "5" {
        Write-Host "跳过配置" -ForegroundColor Cyan
        Read-Host "按回车键退出"
        exit
    }
    
    default {
        Write-Host "❌ 无效选项" -ForegroundColor Red
        Read-Host "按回车键退出"
        exit
    }
}

# 配置远程仓库
Write-Host ""
Write-Host "正在配置远程仓库..." -ForegroundColor Yellow
Write-Host "地址：$repoUrl" -ForegroundColor Cyan
Write-Host ""

try {
    & "C:\Program Files\Git\bin\git.exe" remote add origin $repoUrl
    Write-Host "✅ 远程仓库配置成功！" -ForegroundColor Green
    Write-Host ""
    
    & "C:\Program Files\Git\bin\git.exe" remote -v
    Write-Host ""
} catch {
    Write-Host "❌ 配置失败" -ForegroundColor Red
    Write-Host "可能的原因：" -ForegroundColor Yellow
    Write-Host "1. 地址格式错误"
    Write-Host "2. 远程仓库已存在"
    Write-Host "3. 网络问题"
    Write-Host ""
    Read-Host "按回车键退出"
    exit
}

# 询问是否立即推送
$pushNow = Read-Host "是否立即推送到远程仓库？(Y/N)"
if ($pushNow -eq 'Y' -or $pushNow -eq 'y') {
    Write-Host ""
    Write-Host "正在推送代码..." -ForegroundColor Yellow
    
    try {
        # 尝试推送到 master
        & "C:\Program Files\Git\bin\git.exe" push -u origin master
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ 推送成功！" -ForegroundColor Green
        } else {
            # 如果失败，尝试推送到 main
            Write-Host "⚠️  推送到 master 失败，尝试推送到 main..." -ForegroundColor Yellow
            
            & "C:\Program Files\Git\bin\git.exe" branch -M main
            & "C:\Program Files\Git\bin\git.exe" push -u origin main
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ 推送成功！" -ForegroundColor Green
            } else {
                Write-Host "❌ 推送失败" -ForegroundColor Red
                Write-Host "可能的原因：" -ForegroundColor Yellow
                Write-Host "1. 远程仓库不为空"
                Write-Host "2. 权限问题"
                Write-Host "3. 网络问题"
                Write-Host ""
                Write-Host "请检查远程仓库是否为空，然后手动执行：" -ForegroundColor Cyan
                Write-Host "git push -u origin master" -ForegroundColor Gray
            }
        }
    } catch {
        Write-Host "❌ 推送失败" -ForegroundColor Red
        Write-Host "请检查网络和权限设置" -ForegroundColor Yellow
    }
    
    Write-Host ""
}

# 显示完成信息
Write-Host "========================================" -ForegroundColor Green
Write-Host "  配置完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "远程仓库信息：" -ForegroundColor Yellow
& "C:\Program Files\Git\bin\git.exe" remote -v
Write-Host ""
Write-Host "当前分支：" -ForegroundColor Yellow
& "C:\Program Files\Git\bin\git.exe" branch
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  下一步操作" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 在本地修改代码后：" -ForegroundColor White
Write-Host "   git add ."
Write-Host "   git commit -m `"修改说明`""
Write-Host "   git push"
Write-Host ""
Write-Host "2. 使用部署工具：" -ForegroundColor White
Write-Host "   .\deploy_tool.bat"
Write-Host ""
Write-Host "3. 查看状态：" -ForegroundColor White
Write-Host "   git status"
Write-Host ""
Write-Host "4. 查看日志：" -ForegroundColor White
Write-Host "   git log --oneline"
Write-Host ""

Write-Host "按回车键退出..." -ForegroundColor Gray
Read-Host
