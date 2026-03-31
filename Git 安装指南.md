# 🛠️ Git 安装与配置完整指南

## 📋 检测结果

**当前状态**：❌ Git 未安装或未添加到 PATH

---

## 🚀 方法 1：从官网安装（推荐⭐⭐⭐⭐⭐）

### 第 1 步：下载 Git

**下载地址**：https://git-scm.com/download/win

访问后会自动检测您的系统，点击下载按钮。

### 第 2 步：运行安装程序

1. 双击下载的 `.exe` 文件
2. 点击 "Next" 开始安装

### 第 3 步：安装选项（重要！）

**推荐选择**（按顺序）：

1. **选择目标位置**
   - 默认：`C:\Program Files\Git`
   - 点击 "Next"

2. **选择组件** ✅
   - ✅ Git Bash Here
   - ✅ Git GUI Here
   - ✅ Associate .git* files with default editor
   - ✅ Associate .sh files to run with bash
   - ✅ Add a Git Bash Profile to Windows Terminal
   - ✅ Daily Check

3. **选择开始菜单文件夹**
   - 默认：Git
   - 点击 "Next"

4. **选择默认编辑器** ⭐重要
   - 选择：**Use Visual Studio Code**（或其他您熟悉的编辑器）
   - 或者选择：**Use Notepad**（简单）

5. **调整 PATH 环境** ⭐⭐⭐非常重要
   - 选择第三项：**Git from the command line and also from 3rd-party software**
   - 这样 Git 才能在 PowerShell 和 CMD 中使用

6. **选择 HTTPS 传输后端**
   - 选择：**Use the OpenSSL library**

7. **配置行尾转换** ⭐重要
   - 选择第二项：**Checkout as is, commit Unix-style line endings**
   - 或者第一项：**Checkout Windows-style, commit Unix-style line endings**

8. **配置终端模拟器**
   - 选择：**Use MinTTY**（推荐）

9. **配置默认分支名**
   - 选择：**Default branch name for new repositories**
   - 输入：`main`

10. **配置额外选项**
    - ✅ Enable file system cache
    - ✅ Enable symbolic links

11. **启用实验性选项**
    - ❌ 不勾选任何选项（稳定为主）

### 第 4 步：完成安装

1. 点击 "Install" 开始安装
2. 等待安装完成
3. 点击 "Finish" 完成

### 第 5 步：验证安装

**重要**：关闭所有已打开的 PowerShell 和 CMD 窗口，重新打开新的窗口！

```bash
# 在 PowerShell 中运行
git --version
```

如果显示版本号，说明安装成功！

---

## 🖥️ 方法 2：使用 GitHub Desktop（新手友好⭐⭐⭐⭐）

### 优势
- ✅ 图形化界面，易于使用
- ✅ 自动安装 Git
- ✅ 集成 GitHub 功能

### 安装步骤

1. **下载 GitHub Desktop**
   - 访问：https://desktop.github.com
   - 点击下载

2. **安装**
   - 运行安装程序
   - 登录 GitHub 账号（没有可以注册）

3. **使用**
   - 添加本地项目
   - 提交代码
   - 推送到远程

---

## ⚡ 方法 3：使用包管理器（高级用户⭐⭐⭐）

### 使用 Scoop 安装

```bash
# 如果已安装 Scoop
scoop install git

# 验证安装
git --version
```

### 使用 Chocolatey 安装

```bash
# 以管理员身份运行 PowerShell
choco install git -y

# 验证安装
git --version
```

---

## ⚙️ Git 安装后配置

### 配置用户信息（必须！）

```bash
# 设置用户名
git config --global user.name "Your Name"

# 设置邮箱
git config --global user.email "your.email@example.com"

# 验证配置
git config --global --list
```

### 配置默认编辑器

```bash
# 使用 VS Code
git config --global core.editor "code --wait"

# 使用 Notepad++
git config --global core.editor "'C:/Program Files/Notepad++/notepad++.exe' -multiInst"

# 使用 Vim
git config --global core.editor vim
```

### 配置行尾符

```bash
# Windows 用户推荐
git config --global core.autocrlf true

# 或者统一使用 Unix 风格
git config --global core.autocrlf input
```

---

## 🎯 验证 Git 安装

### 运行检测脚本

```bash
# 在项目目录运行
.\check_git.bat
```

如果显示 ✅ Git 已安装，说明配置成功！

### 手动验证

```bash
# 检查版本
git --version

# 检查配置
git config --global --list

# 创建测试仓库
mkdir test-git
cd test-git
git init
echo "Hello" > test.txt
git add .
git commit -m "Test commit"
```

---

## 🐛 常见问题

### Q1：安装后 git 命令还是不能用？

**A**：需要重启终端或重新登录 Windows

```bash
# 关闭所有 PowerShell 和 CMD 窗口
# 重新打开新的 PowerShell

# 如果还不行，检查 PATH
echo $env:Path -split ';' | Select-String Git
```

### Q2：PATH 配置错误怎么办？

**A**：手动添加 Git 到 PATH

1. 右键"此电脑" → 属性
2. 高级系统设置 → 环境变量
3. 系统变量 → Path → 编辑
4. 添加：`C:\Program Files\Git\bin`
5. 确定保存
6. 重启终端

### Q3：中文乱码问题？

**A**：配置 Git 支持中文

```bash
git config --global core.quotepath false
git config --global gui.encoding utf-8
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8
```

### Q4：权限问题？

**A**：以管理员身份运行终端

```bash
# 右键 PowerShell → 以管理员身份运行
# 然后重新运行 git 命令
```

---

## 📝 下一步操作

Git 安装完成后，继续以下步骤：

### 1. 初始化本地仓库

```bash
cd e:\EIMS2026
git init
git add .
git commit -m "Initial commit"
```

### 2. 创建远程仓库

访问 https://github.com 或 https://gitee.com
创建新仓库 `eims2026`

### 3. 关联远程仓库

```bash
git remote add origin https://github.com/你的用户名/eims2026.git
git push -u origin main
```

### 4. 使用部署工具

```bash
# 运行部署工具
.\deploy_tool.bat

# 或使用检测脚本
.\check_git.bat
```

---

## 📚 学习资源

### 官方文档
- Git 官网：https://git-scm.com
- Git 文档：https://git-scm.com/doc

### 互动教程
- **Learn Git Branching**（可视化学习）：https://learngitbranching.js.org
- **Codecademy Git**：https://www.codecademy.com/learn/learn-git

### 中文教程
- **廖雪峰 Git 教程**：https://www.liaoxuefeng.com/wiki/896043488029600
- **菜鸟教程 Git**：https://www.runoob.com/git/git-tutorial.html

### 视频课程
- **B 站 Git 教程**：搜索 "Git 教程"
- **YouTube Git 教程**：搜索 "Git tutorial for beginners"

---

## 🎉 总结

**安装 Git 的推荐步骤**：

1. ✅ 访问官网下载：https://git-scm.com/download/win
2. ✅ 运行安装程序
3. ✅ 选择正确的选项（特别是 PATH 配置）
4. ✅ 重启终端
5. ✅ 验证安装：`git --version`
6. ✅ 配置用户信息
7. ✅ 开始使用 Git

**预计时间**：10-15 分钟

**立即开始吧！** 🚀

---

*如果遇到问题，请查看常见问题部分或搜索相关错误信息*
