# Git 远程仓库配置 - 3 步完成

## 🎯 最简单的配置方法

### 第 1 步：创建远程仓库 ⭐⭐⭐⭐⭐

**选择平台**（推荐其中一个）：

#### GitHub（国际领先，功能强大）
1. 访问：https://github.com/new
2. Repository name: `eims2026`
3. 选择 Public 或 Private
4. ❌ 不要勾选任何初始化选项
5. 点击 "Create repository"

#### Gitee（国内速度快）
1. 访问：https://gitee.com/new
2. 仓库名称：`eims2026`
3. 选择公开或私有
4. ❌ 不要勾选任何初始化选项
5. 点击 "创建"

---

### 第 2 步：复制仓库地址 ⭐⭐⭐⭐⭐

创建成功后，复制 HTTPS 地址：

**GitHub 格式**:
```
https://github.com/你的用户名/eims2026.git
```

**Gitee 格式**:
```
https://gitee.com/你的用户名/eims2026.git
```

---

### 第 3 步：本地配置并推送 ⭐⭐⭐⭐⭐

**在 PowerShell 中执行以下命令**（一行一行复制）：

```powershell
# 命令 1：配置远程仓库（替换为你的实际地址）
& "C:\Program Files\Git\bin\git.exe" remote add origin https://github.com/你的用户名/eims2026.git

# 命令 2：验证配置
& "C:\Program Files\Git\bin\git.exe" remote -v

# 命令 3：推送代码
& "C:\Program Files\Git\bin\git.exe" push -u origin master
```

**如果推送失败**，尝试推送到 main 分支：
```powershell
& "C:\Program Files\Git\bin\git.exe" branch -M main
& "C:\Program Files\Git\bin\git.exe" push -u origin main
```

---

## ✅ 验证成功

推送成功后：

1. **刷新 GitHub/Gitee 页面**
   - 应该能看到提交记录
   - 文件名和代码都已上传

2. **本地查看**
   ```powershell
   # 查看远程仓库
   & "C:\Program Files\Git\bin\git.exe" remote -v
   
   # 查看远程分支
   & "C:\Program Files\Git\bin\git.exe" branch -r
   ```

---

## 📝 示例（以 GitHub 为例）

假设你的 GitHub 用户名是 `zhangsan`：

**步骤 1**: 访问 https://github.com/new 创建仓库 `eims2026`

**步骤 2**: 复制地址：`https://github.com/zhangsan/eims2026.git`

**步骤 3**: 在 PowerShell 执行：
```powershell
& "C:\Program Files\Git\bin\git.exe" remote add origin https://github.com/zhangsan/eims2026.git
& "C:\Program Files\Git\bin\git.exe" push -u origin master
```

**完成！** 🎉

---

## 💡 常见问题

### Q1: 提示 "remote already exists"？
```powershell
# 删除原有配置
& "C:\Program Files\Git\bin\git.exe" remote remove origin

# 重新配置
& "C:\Program Files\Git\bin\git.exe" remote add origin 新地址

# 推送
& "C:\Program Files\Git\bin\git.exe" push -u origin master
```

### Q2: 推送失败 "permission denied"？
- 检查是否登录了正确的账号
- 检查是否有仓库访问权限
- 私有仓库需要配置 SSH 密钥

### Q3: 如何查看当前状态？
```powershell
# 查看状态
& "C:\Program Files\Git\bin\git.exe" status

# 查看远程仓库
& "C:\Program Files\Git\bin\git.exe" remote -v

# 查看分支
& "C:\Program Files\Git\bin\git.exe" branch
```

---

## 🚀 日常使用

**修改代码后**:
```powershell
# 添加变更
git add .

# 提交
git commit -m "修改说明"

# 推送
git push
```

**或使用工具**:
```bash
# 快速推送工具
push.bat

# 部署工具
deploy_tool.bat
```

---

## 📚 相关文档

| 文档 | 链接 |
|------|------|
| 完整配置指南 | [`Git 远程仓库配置指南.md`](file://e:\EIMS2026\Git 远程仓库配置指南.md) |
| 快速指南 | [`配置远程仓库_快速指南.md`](file://e:\EIMS2026\配置远程仓库_快速指南.md) |
| Git 教程 | [`Git 部署快速入门.md`](file://e:\EIMS2026\Git 部署快速入门.md) |
| 总结 | [`🎉Git 配置完成！开始使用.md`](file://e:\EIMS2026\🎉Git 配置完成！开始使用.md) |

---

## 🎉 立即开始

**现在就去创建仓库吧!**

1. 打开浏览器 → https://github.com/new 或 https://gitee.com/new
2. 创建仓库 `eims2026`
3. 复制地址
4. 运行上面的 3 条命令
5. 完成！🎊

**祝您使用愉快!** 
