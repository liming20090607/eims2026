@echo off
chcp 65001 >nul
echo ======================================
echo 阿里云 SSL 证书部署 - 快速指南
echo ======================================
echo.
echo 📋 部署步骤：
echo.
echo 步骤 1: 申请阿里云 SSL 证书
echo   访问：https://www.aliyun.com
echo   产品 → 安全 → SSL 证书 → 免费证书
echo.
echo 步骤 2: 下载证书（Nginx 格式）
echo   证书文件：.pem（证书）和.key（私钥）
echo.
echo 步骤 3: 上传证书到服务器
echo   使用 SCP 或 FTP 工具上传到 /etc/nginx/ssl/
echo.
echo 步骤 4: 配置 Nginx
echo   编辑 /etc/nginx/conf.d/https.conf
echo.
echo 步骤 5: 重启 Nginx 并验证
echo   systemctl restart nginx
echo   curl -I https://yourdomain.com
echo.
echo ======================================
echo 📖 详细指南请查看：
echo   阿里云 SSL 证书部署指南.md
echo ======================================
echo.
pause
