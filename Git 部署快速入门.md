# 🚀 EIMS Git 部署快速入门

## 📋 为什么使用 Git？

**之前的问题**：
- ❌ 每次修改都要重新上传整个项目
- ❌ 文件替换容易出错
- ❌ 无法追踪修改历史
- ❌ 无法回滚到之前的版本

**使用 Git 后**：
- ✅ 只上传变更的文件
- ✅ 自动追踪所有修改
- ✅ 可以轻松回滚
- ✅ 支持多人协作

---

## 🎯 快速开始（15 分钟）

### 第 1 步：安装 Git（本地）

**Windows**：
1. 下载：https://git-scm.com/download/win
2. 安装（全部使用默认选项）
3. 验证：打开 CMD 运行 `git --version`

### 第 2 步：创建 Git 仓库（本地）

```bash
# 在项目根目录执行
cd e:\EIMS2026

# 初始化 Git 仓库
git init

# 创建 .gitignore 文件（排除不必要的文件）
echo venv/ >> .gitignore
echo __pycache__/ >> .gitignore
echo *.pyc >> .gitignore
echo db.sqlite3 >> .gitignore
echo media/ >> .gitignore
echo staticfiles/ >> .gitignore
echo .env >> .gitignore

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit - EIMS project"
```

### 第 3 步：创建远程仓库

**选择 A：GitHub（推荐）**
1. 访问 https://github.com
2. 点击右上角 "+" → "New repository"
3. 仓库名：`eims2026`
4. 选择 "Private"（私有）
5. 点击 "Create repository"

**选择 B：Gitee（国内速度快）**
1. 访问 https://gitee.com
2. 点击右上角 "+" → "新建仓库"
3. 仓库名：`eims2026`
4. 点击 "创建"

### 第 4 步：关联远程仓库

```bash
# GitHub
git remote add origin https://github.com/你的用户名/eims2026.git

# Gitee
git remote add origin https://gitee.com/你的用户名/eims2026.git

# 推送代码
git push -u origin main
```

### 第 5 步：在服务器上克隆

```bash
# SSH 登录阿里云服务器
ssh root@你的服务器 IP

# 克隆项目
cd /var/www
git clone https://github.com/你的用户名/eims2026.git eims
cd eims

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置数据库和 .env 文件
# （参考部署指南）
```

### 第 6 步：创建部署脚本

**在服务器上创建 `/var/www/eims/deploy.sh`**：
```bash
nano /var/www/eims/deploy.sh
```

粘贴以下内容：
```bash
#!/bin/bash
cd /var/www/eims
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
systemctl restart eims
echo "✅ 部署完成！"
```

赋予执行权限：
```bash
chmod +x /var/www/eims/deploy.sh
```

---

## 📝 日常使用流程

### 在本地修改代码后

**方法 1：使用命令行**
```bash
cd e:\EIMS2026

# 查看变更
git status

# 添加变更
git add .

# 提交（写上修改说明）
git commit -m "修复了部门角色配置的布局问题"

# 推送到远程
git push origin main

# SSH 到服务器执行部署
ssh root@服务器 IP "cd /var/www/eims && ./deploy.sh"
```

**方法 2：使用部署工具（推荐）**
```bash
# 双击运行
deploy_tool.bat

# 按提示选择操作：
# 2. 提交并推送代码
# 3. 远程部署到服务器
```

---

## 🎯 典型工作流

### 场景 1：小修改（修改 1-2 个文件）

```bash
# 本地修改 → 提交 → 推送 → 部署
git add .
git commit -m "修复了按钮颜色问题"
git push
ssh root@服务器 IP "cd /var/www/eims && ./deploy.sh"
```

### 场景 2：大功能（多个文件修改）

```bash
# 创建功能分支
git checkout -b feature/new-feature

# 开发过程中多次提交
git add .
git commit -m "实现功能第一部分"

git add .
git commit -m "实现功能第二部分"

# 完成后推送到远程
git push -u origin feature/new-feature

# 测试无误后合并到主分支
git checkout main
git merge feature/new-feature
git push

# 部署到服务器
ssh root@服务器 IP "cd /var/www/eims && ./deploy.sh"
```

### 场景 3：紧急修复

```bash
# 直接在主分支修复
git checkout main

# 快速修复
git add .
git commit -m "紧急修复：xxx 问题"
git push

# 立即部署
ssh root@服务器 IP "cd /var/www/eims && ./deploy.sh"
```

---

## 🔧 使用部署工具

### 本地部署工具（Windows）

**文件**：`deploy_tool.bat`

**功能**：
1. 初始化 Git 仓库
2. 提交并推送代码
3. 远程部署到服务器
4. 查看 Git 状态
5. 查看 Git 日志

**使用方法**：
1. 双击运行 `deploy_tool.bat`
2. 按提示输入选项（1-6）
3. 根据提示操作

**首次配置**：
编辑 `deploy_tool.bat`，修改：
```batch
set SERVER_IP=你的服务器 IP
set SERVER_USER=root
set SERVER_PATH=/var/www/eims
```

### 服务器部署脚本

**文件**：`server_deploy.sh`（在服务器上）

**功能**：
- 自动拉取最新代码
- 安装依赖
- 数据库迁移
- 收集静态文件
- 重启服务

**使用方法**：
```bash
# SSH 到服务器
ssh root@服务器 IP

# 进入项目目录
cd /var/www/eims

# 运行部署脚本
./deploy.sh
```

---

## 📊 Git 常用命令

### 基础命令
```bash
# 查看状态
git status

# 查看变更
git diff

# 查看提交历史
git log
git log --oneline

# 撤销修改
git checkout -- 文件名
git reset HEAD 文件名
```

### 分支管理
```bash
# 创建分支
git checkout -b 分支名

# 切换分支
git checkout 分支名

# 查看分支
git branch

# 合并分支
git merge 分支名

# 删除分支
git branch -d 分支名
```

### 远程操作
```bash
# 查看远程仓库
git remote -v

# 添加远程仓库
git remote add origin 仓库地址

# 推送代码
git push origin 分支名

# 拉取代码
git pull origin 分支名
```

---

## 🐛 常见问题

### Q1：推送代码失败？
**A**：检查远程仓库地址是否正确
```bash
git remote -v
git remote set-url origin 正确的仓库地址
```

### Q2：合并冲突？
**A**：手动解决冲突文件中的 `<<<<<<<` 和 `>>>>>>>` 标记
```bash
# 查看冲突文件
git status

# 编辑冲突文件，解决冲突
# 然后重新提交
git add .
git commit -m "解决合并冲突"
```

### Q3：部署失败？
**A**：检查服务器日志
```bash
# 查看应用日志
tail -f /var/log/gunicorn/error.log

# 查看服务状态
systemctl status eims

# 手动执行部署步骤
cd /var/www/eims
git pull
source venv/bin/activate
python manage.py migrate
systemctl restart eims
```

### Q4：如何回滚到之前的版本？
**A**：使用 Git 回滚
```bash
# 查看历史提交
git log --oneline

# 回滚到指定版本
git reset --hard 提交 ID

# 强制推送到远程
git push -f

# 重新部署
ssh root@服务器 IP "cd /var/www/eims && ./deploy.sh"
```

---

## 💡 最佳实践

### 提交信息规范
```bash
# 好的提交信息
git commit -m "修复：部门角色配置页面布局问题"
git commit -m "新增：人员花名册导出功能"
git commit -m "优化：数据库查询性能"

# 避免的提交信息
git commit -m "修改"  # 太模糊
git commit -m "修复 bug"  # 不具体
```

### 分支策略
```bash
# 主分支（随时可部署）
main

# 开发分支
develop

# 功能分支
feature/login
feature/report

# 修复分支
fix/bug-123
hotfix/security-issue
```

### 部署频率
- ✅ 小步快跑：频繁部署，每次只部署小改动
- ✅ 测试充分：在开发环境测试后再部署
- ✅ 避开高峰：选择用户少的时候部署

---

## 🎉 总结

**现在的工作流程**：
1. ✅ 在本地修改代码
2. ✅ `git add .` + `git commit`
3. ✅ `git push` 推送到远程
4. ✅ SSH 到服务器运行 `./deploy.sh`

**对比之前**：
- ❌ 之前：上传整个项目 → 手动替换 → 手动迁移 → 手动重启
- ✅ 现在：一行命令自动完成所有步骤

**节省时间**：
- 之前：10-15 分钟
- 现在：1-2 分钟

**立即开始吧！** 🚀
