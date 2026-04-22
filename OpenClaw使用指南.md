# 🤖 OpenClaw 自动化运维指南

## 快速开始

### 1️⃣ 查看系统当前状态
```bash
# 方法1: 查看JSON状态文件
cat /root/.openclaw/monitoring/status.json

# 方法2: 通过API查询（浏览器访问）
http://39.106.41.239/openclaw/api/status/

# 方法3: 使用Python脚本
python verify_openclaw_config.py
```

### 2️⃣ 查看实时监控日志
```bash
# 实时查看健康检查（推荐）
tail -f /root/.openclaw/monitoring/logs/health_check.log

# 查看自动修复记录
tail -f /root/.openclaw/monitoring/logs/auto_fix.log

# 查看部署记录
tail -f /root/.openclaw/monitoring/logs/deploy.log
```

### 3️⃣ 手动触发操作

#### 触发MySQL修复
```bash
bash /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh
```

#### 执行代码部署
```bash
bash /root/.openclaw/monitoring/scripts/auto_deploy.sh
```

#### 立即执行健康检查
```bash
bash /root/.openclaw/monitoring/scripts/health_check.sh
```

---

## 📊 状态解读

### status.json 字段说明
```json
{
  "timestamp": "2026-04-22 06:06:57",  // 检查时间
  "gunicorn": "OK",                     // Gunicorn状态
  "nginx": "OK",                        // Nginx状态
  "mysql": "OK",                        // MySQL状态
  "disk": "37%",                        // 磁盘使用率
  "http_code": "200"                    // HTTP状态码
}
```

### 状态值含义
- **OK**: 正常运行
- **RESTARTED**: 已自动重启
- **FIXED**: 已自动修复
- **FAIL**: 故障（正在修复）
- **FAILED**: 修复失败（需人工干预）

---

## 🔧 常见问题处理

### 问题1: 网站无法访问
```bash
# 1. 检查Gunicorn
ps aux | grep gunicorn

# 2. 检查Nginx
ps aux | grep nginx

# 3. 查看错误日志
tail -50 /var/www/eims/logs/gunicorn_error.log

# 4. 手动重启
pkill -9 -f gunicorn
cd /var/www/eims && source venv/bin/activate
nohup gunicorn --bind 127.0.0.1:8000 --workers 4 wsgi:application > logs/gunicorn.log 2>&1 &
```

### 问题2: MySQL连接失败
```bash
# 直接触发自动修复
bash /root/.openclaw/monitoring/scripts/enhanced_mysql_fix.sh

# 或等待2分钟，OpenClaw会自动修复
```

### 问题3: 需要更新代码
```bash
# 方法1: 手动部署（推荐）
bash /root/.openclaw/monitoring/scripts/auto_deploy.sh

# 方法2: 本地推送后等待自动部署（如果启用了定时任务）
git push
```

### 问题4: 磁盘空间不足
```bash
# 查看磁盘使用
df -h

# 清理旧日志
find /root/.openclaw/monitoring/logs -name "*.log" -mtime +7 -delete

# 清理Django日志
find /var/www/eims/logs -name "*.log" -mtime +7 -delete
```

---

## ⏰ 定时任务说明

### 查看当前定时任务
```bash
crontab -l
```

### 默认配置
```bash
# 每2分钟健康检查
*/2 * * * * bash /root/.openclaw/monitoring/scripts/health_check.sh

# 每天凌晨2点清理7天前的日志
0 2 * * * find /root/.openclaw/monitoring/logs -name "*.log" -mtime +7 -delete
```

### 修改定时任务
```bash
crontab -e
```

---

## 🌐 API使用说明

### 1. 查询系统状态
```
GET http://39.106.41.239/openclaw/api/status/

返回示例:
{
  "timestamp": "2026-04-22 06:06:57",
  "gunicorn": "OK",
  "nginx": "OK",
  "mysql": "OK",
  "disk": "37%",
  "http_code": "200"
}
```

### 2. 触发MySQL修复
```
POST http://39.106.41.239/openclaw/api/trigger-fix/

返回示例:
{
  "message": "Fix triggered"
}
```

---

## 📈 监控最佳实践

### 日常检查（建议每天）
```bash
# 早上检查系统状态
cat /root/.openclaw/monitoring/status.json

# 查看昨晚的日志
tail -100 /root/.openclaw/monitoring/logs/health_check.log | grep "$(date -d yesterday +%Y-%m-%d)"
```

### 周维护（建议每周）
```bash
# 检查磁盘使用趋势
df -h

# 检查日志文件大小
du -sh /root/.openclaw/monitoring/logs/*

# 验证备份（如果有）
ls -lh /var/backups/
```

### 月维护（建议每月）
```bash
# 更新系统包
yum update -y

# 检查Python依赖更新
cd /var/www/eims && source venv/bin/activate
pip list --outdated

# 审查OpenClaw日志
grep "FAILED" /root/.openclaw/monitoring/logs/*.log
```

---

## 🚨 告警设置（可选）

### 邮件告警示例
在 health_check.sh 中添加：
```bash
if [ "$M_STATUS" == "FAILED" ]; then
    echo "MySQL修复失败！请立即检查！" | mail -s "EIMS告警" admin@example.com
fi
```

### 微信/钉钉机器人
```bash
# 在脚本中添加webhook调用
curl -X POST https://oapi.dingtalk.com/robot/send \
  -H 'Content-Type: application/json' \
  -d '{"msgtype":"text","text":{"content":"系统故障告警"}}'
```

---

## 🛠️ 高级用法

### 自定义监控项
编辑 `health_check.sh`，添加新的检查：
```bash
# 检查内存使用
MEM=$(free -m | awk 'NR==2{printf "%.1f%%", $3*100/$2}')
echo "[$TS] 💾 内存: $MEM" >> $LOG

# 检查CPU负载
LOAD=$(uptime | awk -F'load average:' '{print $2}' | cut -d, -f1 | xargs)
echo "[$TS] 🖥️  负载: $LOAD" >> $LOG
```

### 自定义修复脚本
创建新脚本 `/root/.openclaw/monitoring/scripts/custom_fix.sh`：
```bash
#!/bin/bash
# 你的自定义修复逻辑
echo "执行自定义修复..."
# ...
```

然后在 health_check.sh 中调用它。

---

## 📝 日志分析技巧

### 查找所有修复记录
```bash
grep "自动修复" /root/.openclaw/monitoring/logs/health_check.log
```

### 统计MySQL故障次数
```bash
grep -c "MySQL.*故障" /root/.openclaw/monitoring/logs/health_check.log
```

### 查看最近的HTTP错误
```bash
grep "HTTP:" /root/.openclaw/monitoring/logs/health_check.log | grep -v "200" | tail -20
```

### 生成日报
```bash
# 今天的健康检查摘要
grep "$(date +%Y-%m-%d)" /root/.openclaw/monitoring/logs/health_check.log | tail -50
```

---

## 🔐 安全注意事项

1. **不要公开status.json**: 包含系统敏感信息
2. **限制API访问**: 只允许内网或特定IP访问OpenClaw API
3. **定期更换密码**: MySQL密码应定期更新
4. **审计日志**: 定期检查auto_fix.log，确认没有异常修复
5. **备份配置**: 定期备份OpenClaw脚本和配置

---

## 💡 提示与技巧

### 提示1: 快速测试OpenClaw是否工作
```bash
# 等待2分钟，然后检查日志
sleep 120
tail -20 /root/.openclaw/monitoring/logs/health_check.log
```

### 提示2: 模拟故障测试
```bash
# 停止Gunicorn测试自动重启
pkill -9 -f gunicorn
# 等待2分钟，检查是否自动恢复
```

### 提示3: 查看完整的修复过程
```bash
# 查看最近一次MySQL修复的详细日志
tail -100 /root/.openclaw/monitoring/logs/auto_fix.log
```

### 提示4: 性能优化
```bash
# 如果服务器资源充足，可以增加Gunicorn workers
# 编辑 auto_deploy.sh，修改 --workers 参数
--workers 8  # 从4改为8
```

---

## 📞 获取帮助

### 诊断脚本
运行以下命令生成诊断报告：
```bash
echo "=== 系统信息 ==="
uname -a
echo ""
echo "=== 服务状态 ==="
ps aux | grep -E "(gunicorn|nginx|mysql)" | grep -v grep
echo ""
echo "=== 磁盘使用 ==="
df -h
echo ""
echo "=== 最近日志 ==="
tail -20 /root/.openclaw/monitoring/logs/health_check.log
```

### 联系支持
如遇无法解决的问题：
1. 保存诊断报告
2. 附上相关日志文件
3. 描述具体问题现象

---

**最后更新**: 2026-04-22  
**文档版本**: 1.0  
**维护者**: OpenClaw自动化系统
