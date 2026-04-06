# Python 虚拟环境使用指南

**适用项目**: EIMS Django 项目  
**服务器**: Alibaba Cloud CentOS  

---

## 🎯 **什么是虚拟环境？**

虚拟环境（Virtual Environment）是一个独立的 Python 环境，可以：

- ✅ **隔离依赖包** - 不同项目使用不同版本的库
- ✅ **避免冲突** - 系统 Python 和项目 Python 互不影响
- ✅ **便于管理** - 每个项目有自己的依赖列表

---

## 📋 **EIMS 项目的虚拟环境**

### **位置**
```bash
/var/www/eims/venv/
```

### **包含的包**
```bash
Django 4.2.7
mysqlclient
gunicorn
其他依赖...
```

---

## ⚠️ **什么时候需要激活虚拟环境？**

### **必须激活的情况** ✅

#### **1. 运行 Django 管理命令**
```bash
# ❌ 错误（未激活）
python manage.py runserver
# ModuleNotFoundError: No module named 'django'

# ✅ 正确（已激活）
source venv/bin/activate
python manage.py runserver
```

#### **2. 安装 Python 包**
```bash
# ❌ 错误（会安装到系统 Python）
pip install django

# ✅ 正确（安装到项目虚拟环境）
source venv/bin/activate
pip install django
```

#### **3. 执行 Python 脚本（使用项目依赖）**
```bash
# ❌ 错误
python script.py

# ✅ 正确
source venv/bin/activate
python script.py
```

#### **4. 进入 Django Shell**
```bash
# ❌ 错误
python manage.py shell

# ✅ 正确
source venv/bin/activate
python manage.py shell
```

#### **5. 数据库迁移**
```bash
# ❌ 错误
python manage.py migrate

# ✅ 正确
source venv/bin/activate
python manage.py migrate
```

#### **6. 导出/导入数据**
```bash
# ❌ 错误
python manage.py dumpdata

# ✅ 正确
source venv/bin/activate
python manage.py dumpdata
```

---

### **不需要激活的情况** ✅

#### **1. 使用 Supervisor/Gunicorn 运行**
```bash
# Supervisor 配置中已指定虚拟环境的 Python 路径
# /etc/supervisor/conf.d/eims.conf

[program:eims]
command=/var/www/eims/venv/bin/python /var/www/eims/manage.py run_gunicorn
# 不需要手动激活，Supervisor 会自动使用指定的 Python
```

#### **2. 使用 Nginx + Gunicorn（生产环境）**
```bash
# Gunicorn 启动脚本中已指定虚拟环境
#!/bin/bash
source /var/www/eims/venv/bin/activate
cd /var/www/eims
gunicorn eims.wsgi:application
```

#### **3. 普通的 Linux 命令**
```bash
# 这些命令不使用 Python，不需要激活
ls -lh
cd /var/www/eims
tail -f logs/eims.log
supervisorctl status
```

#### **4. 使用完整路径执行命令**
```bash
# 不激活虚拟环境，直接使用完整路径
/var/www/eims/venv/bin/python manage.py shell
/var/www/eims/venv/bin/pip list
```

---

## 🔧 **如何激活虚拟环境？**

### **方法 1：使用 source 命令**
```bash
cd /var/www/eims
source venv/bin/activate

# 成功后提示符会变化
# (venv) [root@iZ2ze74hagmo3egfxeffrcZ eims]#
```

### **方法 2：使用点号（简写）**
```bash
cd /var/www/eims
. venv/bin/activate

# 效果相同
```

### **方法 3：退出虚拟环境**
```bash
deactivate

# 提示符恢复为
# [root@iZ2ze74hagmo3egfxeffrcZ eims]#
```

---

## 📊 **实际案例对比**

### **案例 1：今天的角色导入**

#### **❌ 失败方式（未激活）**
```bash
[root@iZ2ze74hagmo3egfxeffrcZ eims]# python manage.py shell
ModuleNotFoundError: No module named 'django'
```

#### **✅ 成功方式（已激活）**
```bash
[root@iZ2ze74hagmo3egfxeffrcZ eims]# source venv/bin/activate
(venv) [root@iZ2ze74hagmo3egfxeffrcZ eims]# python manage.py shell
# 成功进入 Django Shell
```

---

### **案例 2：安装新依赖**

#### **❌ 错误方式**
```bash
[root@iZ2ze74hagmo3egfxeffrcZ ~]# pip install requests
# 安装到系统 Python，EIMS 项目用不了
```

#### **✅ 正确方式**
```bash
[root@iZ2ze74hagmo3egfxeffrcZ ~]# cd /var/www/eims
[root@iZ2ze74hagmo3egfxeffrcZ eims]# source venv/bin/activate
(venv) [root@iZ2ze74hagmo3egfxeffrcZ eims]# pip install requests
# 安装到项目虚拟环境，EIMS 可以使用
```

---

### **案例 3：日常维护命令**

#### **不需要激活的情况**
```bash
# 查看服务状态（Linux 命令）
supervisorctl status

# 查看日志（文件操作）
tail -f /var/log/supervisor/eims.log

# 重启服务（Supervisor 命令）
supervisorctl restart eims
```

#### **需要激活的情况**
```bash
# 清理数据库（Django 命令）
source venv/bin/activate
python manage.py flush

# 创建超级用户（Django 命令）
source venv/bin/activate
python manage.py createsuperuser

# 检查数据库表（Django Shell）
source venv/bin/activate
python manage.py shell
```

---

## 🎯 **快速判断规则**

### **问自己这个问题**：

> **"这个命令是否需要使用 Django 或项目的 Python 包？"**

- ✅ **是** → 需要激活虚拟环境
- ❌ **否** → 不需要激活

---

### **常见命令分类**

| 命令类型 | 示例 | 需要激活？ |
|---------|------|-----------|
| **Django 管理命令** | `python manage.py ...` | ✅ 是 |
| **Python 脚本（使用项目依赖）** | `python script.py` | ✅ 是 |
| **安装包** | `pip install ...` | ✅ 是 |
| **进入 Shell** | `python manage.py shell` | ✅ 是 |
| **Linux 基础命令** | `ls`, `cd`, `tail` | ❌ 否 |
| **Supervisor 命令** | `supervisorctl ...` | ❌ 否 |
| **Git 命令** | `git status`, `git pull` | ❌ 否 |
| **文件操作** | `cp`, `mv`, `rm` | ❌ 否 |

---

## 💡 **最佳实践**

### **1. 在脚本开头激活**
```bash
#!/bin/bash
cd /var/www/eims
source venv/bin/activate

# 然后执行 Django 相关命令
python manage.py migrate
python manage.py collectstatic
```

### **2. 在 Supervisor 配置中使用完整路径**
```ini
[program:eims]
command=/var/www/eims/venv/bin/python /var/www/eims/manage.py run_gunicorn
directory=/var/www/eims
# 这样不需要 activate
```

### **3. 在 Cron 定时任务中使用完整路径**
```bash
# /etc/crontab
0 2 * * * root /var/www/eims/venv/bin/python /var/www/eims/manage.py cleanup > /dev/null 2>&1
```

---

## 🚨 **常见错误和解决方法**

### **错误 1：ModuleNotFoundError**
```bash
# 现象
ModuleNotFoundError: No module named 'django'

# 原因
未激活虚拟环境

# 解决
source venv/bin/activate
```

### **错误 2：包版本冲突**
```bash
# 现象
Django 4.2.7 需要 mysqlclient 2.x，但系统是 1.x

# 原因
使用了系统 Python 而不是虚拟环境

# 解决
source venv/bin/activate
pip install -r requirements.txt
```

### **错误 3：命令找不到**
```bash
# 现象
bash: python: command not found

# 原因
未激活虚拟环境，或 PATH 中没有 Python

# 解决
source venv/bin/activate
# 或使用完整路径
/var/www/eims/venv/bin/python
```

---

## 📝 **总结**

### **记住这个口诀**：

> **Django 命令必激活**  
> **Linux 命令不用管**  
> **Supervisor 已配置**  
> **完整路径可替代**

---

### **今天的教训**

您遇到的错误：
```bash
python manage.py shell
# ModuleNotFoundError: No module named 'django'
```

**原因**：没有激活虚拟环境  
**解决**：先执行 `source venv/bin/activate`

---

**位置**: `E:\EIMS2026\bat\Python 虚拟环境使用指南.md`  
**状态**: ✅ 立即可参考  
**时间**: 2026-04-02  

---

🎯 **现在明白了吗？下次记得先激活虚拟环境！** 🚀✨
