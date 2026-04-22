# EIMS2026 VS Code 同步部署指南

## 📋 目录
1. [VS Code Remote-SSH 连接](#方式一vs-code-remote-ssh-推荐)
2. [自动化部署脚本](#方式二使用自动化部署脚本)
3. [手动Git部署](#方式三手动git部署)

---

## 方式一：VS Code Remote-SSH（推荐）

### ✅ 优点
- 直接在VS Code中编辑服务器文件
- 实时同步修改
- 支持智能提示和调试

### 📝 配置步骤

#### 1. 安装扩展
打开VS Code，按 `Ctrl+Shift+X`，搜索安装：
- **Remote - SSH** (微软官方扩展)

#### 2. 配置SSH连接

**方法A：通过命令面板**
1. 按 `Ctrl+Shift+P`
2. 输入：`Remote-SSH: Add New SSH Host`
3. 输入连接命令：
   ```
   ssh root@39.106.41.239 -i ~/.ssh/id_rsa
   ```
4. 选择SSH配置文件：`C:\Users\Administrator\.ssh\config`
5. 点击"Reload"重新加载窗口

**方法B：手动编辑config文件**
编辑 `C:\Users\Administrator\.ssh\config`，添加：

```ssh-config
Host eims-server
    HostName 39.106.41.239
    User root
    IdentityFile ~/.ssh/id_rsa
    Port 22
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

#### 3. 连接服务器
1. 点击VS Code左下角的绿色图标 `><`
2. 选择 `Connect to Host...`
3. 选择 `eims-server`
4. 等待连接建立（首次连接可能需要安装VS Code Server）

#### 4. 打开项目目录
1. 连接成功后，点击 `File` → `Open Folder...`
2. 输入服务器项目路径：`/var/www/eims`
3. 确认打开

#### 5. 同步代码
在VS Code中直接编辑文件，保存后自动同步到服务器。

### ⚡ 快速部署命令

连接服务器后，在VS Code终端中执行：

```bash
# 从Gitee拉取最新代码
cd /var/www/eims
git pull

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 应用迁移
python manage.py migrate

# 重启服务
pkill -9 -f gunicorn
sleep 2
nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 --daemon wsgi:application &

# 验证
curl http://127.0.0.1:8000/login/
```

---

## 方式二：使用自动化部署脚本

### ✅ 优点
- 一键完成所有部署步骤
- 包含错误检查和验证
- 适合频繁部署

### 📝 使用方法

#### 1. 确保SSH密钥配置正确

测试SSH连接：
```bash
ssh root@39.106.41.239 -i ~/.ssh/id_rsa
```

#### 2. 运行部署脚本

在本地VS Code终端中执行：

```bash
# 方式A：使用现有的pull_and_deploy.py
python pull_and_deploy.py

# 方式B：创建新的简化部署脚本
python deploy_simple.py
```

#### 3. 部署流程

脚本会自动完成：
1. ✅ SSH连接到服务器
2. ✅ 从Gitee拉取最新代码
3. ✅ 安装Python依赖
4. ✅ 应用数据库迁移
5. ✅ 重启Gunicorn服务
6. ✅ 验证服务状态
7. ✅ 显示访问地址

---

## 方式三：手动Git部署

### ✅ 优点
- 完全控制每个步骤
- 适合调试和排查问题

### 📝 操作步骤

#### 1. 本地推送到Gitee
```bash
cd e:\EIMS2026
git add .
git commit -m "更新说明"
git push gitee master
```

#### 2. SSH登录服务器
```bash
ssh root@39.106.41.239 -i ~/.ssh/id_rsa
```

#### 3. 在服务器上拉取代码
```bash
cd /var/www/eims
git pull
```

#### 4. 更新环境
```bash
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

#### 5. 重启服务
```bash
# 停止旧进程
pkill -9 -f gunicorn

# 等待2秒
sleep 2

# 启动新进程
cd /var/www/eims
source venv/bin/activate
nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 --daemon wsgi:application &
```

#### 6. 验证
```bash
# 检查进程
ps aux | grep gunicorn

# 测试HTTP
curl http://127.0.0.1:8000/login/

# 查看日志
tail -f /var/www/eims/logs/gunicorn_error.log
```

---

## 🔧 VS Code 实用技巧

### 1. 多窗口同时编辑本地和远程
- 一个窗口编辑本地代码
- 另一个窗口通过Remote-SSH编辑服务器代码
- 方便对比和同步

### 2. 同步本地修改到服务器

**方法A：使用Git**
```bash
# 本地
git add .
git commit -m "修改说明"
git push gitee master

# 服务器（Remote-SSH终端）
cd /var/www/eims
git pull
```

**方法B：使用VS Code扩展**
安装扩展：**SFTP** 或 **Sync-Rsync**
配置自动同步

### 3. 远程调试

在VS Code中配置远程调试：

1. 服务器安装debugpy：
```bash
source venv/bin/activate
pip install debugpy
```

2. 在VS Code中配置 `.vscode/launch.json`：
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Remote Attach",
            "type": "python",
            "request": "attach",
            "connect": {
                "host": "39.106.41.239",
                "port": 5678
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}",
                    "remoteRoot": "/var/www/eims"
                }
            ]
        }
    ]
}
```

---

## 📊 服务器信息

| 项目 | 信息 |
|------|------|
| **服务器IP** | 39.106.41.239 |
| **SSH用户** | root |
| **项目路径** | /var/www/eims |
| **虚拟环境** | /var/www/eims/venv |
| **Gunicorn端口** | 127.0.0.1:8000 |
| **数据库** | MySQL (本地) |
| **代码仓库** | Gitee + GitHub |
| **认证方式** | SSH密钥 (~/.ssh/id_rsa) |

---

## 🌐 访问地址

- **主站**: http://39.106.41.239/login/
- **域名**: http://www.xietongai.com.cn/login/

---

## ⚠️ 注意事项

### 1. 安全提示
- ✅ 使用SSH密钥认证，避免密码泄露
- ✅ 定期更新服务器密码
- ✅ 不要将 `.env` 文件提交到Git
- ✅ 定期备份数据库

### 2. 部署检查清单
- [ ] 本地代码已推送到Gitee
- [ ] SSH连接正常
- [ ] 服务器磁盘空间充足
- [ ] MySQL服务正常运行
- [ ] Gunicorn进程正常
- [ ] 网站访问正常

### 3. 常见问题

**Q: SSH连接失败？**
```bash
# 检查SSH密钥权限
chmod 600 ~/.ssh/id_rsa

# 测试连接
ssh -v root@39.106.41.239
```

**Q: Git pull失败？**
```bash
# 检查远程仓库
git remote -v

# 强制同步
git fetch --all
git reset --hard origin/master
```

**Q: Gunicorn启动失败？**
```bash
# 查看错误日志
tail -100 /var/www/eims/logs/gunicorn_error.log

# 手动测试启动
cd /var/www/eims
source venv/bin/activate
python manage.py check
```

---

## 🎯 推荐工作流程

### 日常开发流程

1. **本地开发**
   ```bash
   # 在本地VS Code中编辑代码
   # 测试功能
   python manage.py runserver
   ```

2. **推送到仓库**
   ```bash
   git add .
   git commit -m "更新说明"
   git push gitee master
   ```

3. **部署到服务器**
   ```bash
   # 方式A：使用脚本
   python pull_and_deploy.py
   
   # 方式B：通过Remote-SSH手动操作
   ssh root@39.106.41.239
   cd /var/www/eims
   git pull
   source venv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate
   pkill -9 -f gunicorn
   sleep 2
   nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 --daemon wsgi:application &
   ```

4. **验证部署**
   - 访问 http://39.106.41.239/login/
   - 检查功能是否正常
   - 查看日志是否有错误

---

## 📞 技术支持

如遇问题，请检查：
1. VS Code Remote-SSH 扩展日志
2. 服务器系统日志：`journalctl -u nginx`
3. Gunicorn错误日志：`/var/www/eims/logs/gunicorn_error.log`
4. Django日志：`/var/www/eims/logs/django.log`

---

**最后更新**: 2026-04-22  
**版本**: 1.0
