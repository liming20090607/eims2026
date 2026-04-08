#!/bin/bash
# EIMS 云服务器同步完整指南
# 按照以下步骤完成本地系统到云服务器的同步

echo "========================================="
echo "EIMS 云服务器同步完整指南"
echo "========================================="
echo ""

echo "📋 同步前准备清单"
echo "========================================="
echo ""
echo "【第一步】确认服务器信息"
echo "-----------------------------------------"
echo "服务器 IP: 39.106.41.239"
echo "SSH 用户: root"
echo "项目路径: /var/www/eims"
echo "虚拟环境: /var/www/eims/venv"
echo ""

echo "【第二步】确认本地数据完整"
echo "-----------------------------------------"
echo "✓ 检查数据库文件: db.sqlite3"
echo "✓ 检查媒体文件: media/ 目录"
echo "✓ 检查代码更新: 所有修改已保存"
echo ""

echo "【第三步】选择同步方式"
echo "========================================="
echo ""
echo "方式 A: 自动同步（推荐）- 使用 sync_to_cloud.sh"
echo "方式 B: 手动同步 - 按步骤逐个执行"
echo "方式 C: Git 同步 - 通过 Git 仓库更新代码"
echo ""

read -p "请选择同步方式 (A/B/C): " method

case $method in
    A|a)
        echo ""
        echo "========================================="
        echo "方式 A: 自动同步"
        echo "========================================="
        echo ""
        echo "即将执行自动同步脚本，此脚本将："
        echo "  1. 备份服务器当前数据"
        echo "  2. 同步代码文件"
        echo "  3. 同步数据库数据"
        echo "  4. 同步媒体文件"
        echo "  5. 更新服务器配置"
        echo "  6. 重启服务"
        echo "  7. 清理临时文件"
        echo ""
        read -p "确认执行自动同步？(y/n): " confirm
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            echo ""
            echo "开始执行自动同步..."
            echo ""
            bash sync_to_cloud.sh
        else
            echo "已取消自动同步"
            exit 0
        fi
        ;;
    
    B|b)
        echo ""
        echo "========================================="
        echo "方式 B: 手动同步步骤"
        echo "========================================="
        echo ""
        echo "步骤 1: 测试 SSH 连接"
        echo "-----------------------------------------"
        echo "命令: ssh root@39.106.41.239"
        read -p "按回车继续..."
        
        echo ""
        echo "步骤 2: 备份服务器数据"
        echo "-----------------------------------------"
        echo "命令:"
        echo "  ssh root@39.106.41.239 'cd /var/www/eims && source venv/bin/activate && python manage.py dumpdata --natural-foreign --natural-primary --indent=2 > backup_before_$(date +%Y%m%d_%H%M%S).json'"
        read -p "按回车继续..."
        
        echo ""
        echo "步骤 3: 导出本地数据库"
        echo "-----------------------------------------"
        echo "命令: python manage.py dumpdata --natural-foreign --natural-primary --indent=2 > local_data.json"
        read -p "按回车继续..."
        
        echo ""
        echo "步骤 4: 传输数据到服务器"
        echo "-----------------------------------------"
        echo "命令: scp local_data.json root@39.106.41.239:/var/www/eims/"
        read -p "按回车继续..."
        
        echo ""
        echo "步骤 5: 导入数据到服务器"
        echo "-----------------------------------------"
        echo "命令:"
        echo "  ssh root@39.106.41.239 'cd /var/www/eims && source venv/bin/activate && python manage.py loaddata local_data.json'"
        read -p "按回车继续..."
        
        echo ""
        echo "步骤 6: 同步代码文件"
        echo "-----------------------------------------"
        echo "使用 WinSCP 或 FileZilla 上传整个项目目录到 /var/www/eims/"
        echo "注意排除: venv/, __pycache__/, *.pyc, db.sqlite3, backup/"
        read -p "按回车继续..."
        
        echo ""
        echo "步骤 7: 同步媒体文件"
        echo "-----------------------------------------"
        echo "命令: rsync -avz --progress media/ root@39.106.41.239:/var/www/eims/media/"
        read -p "按回车继续..."
        
        echo ""
        echo "步骤 8: 更新服务器配置"
        echo "-----------------------------------------"
        echo "命令:"
        echo "  ssh root@39.106.41.239 'cd /var/www/eims && source venv/bin/activate && python manage.py collectstatic --noinput'"
        echo "  ssh root@39.106.41.239 'cd /var/www/eims && source venv/bin/activate && python manage.py migrate --noinput'"
        read -p "按回车继续..."
        
        echo ""
        echo "步骤 9: 重启服务"
        echo "-----------------------------------------"
        echo "命令:"
        echo "  ssh root@39.106.41.239 'supervisorctl restart eims'"
        echo "  ssh root@39.106.41.239 'systemctl restart nginx'"
        read -p "按回车继续..."
        
        echo ""
        echo "步骤 10: 清理临时文件"
        echo "-----------------------------------------"
        echo "命令: rm -f local_data.json"
        echo "命令: ssh root@39.106.41.239 'rm -f /var/www/eims/local_data.json'"
        read -p "按回车继续..."
        
        echo ""
        echo "========================================="
        echo "手动同步步骤已完成！"
        echo "========================================="
        ;;
    
    C|c)
        echo ""
        echo "========================================="
        echo "方式 C: Git 同步"
        echo "========================================="
        echo ""
        echo "注意: 此方式仅同步代码，数据需单独处理"
        echo ""
        echo "步骤 1: 在本地创建 Git 仓库并提交代码"
        echo "-----------------------------------------"
        echo "命令:"
        echo "  git init"
        echo "  git add ."
        echo "  git commit -m 'Sync to cloud server'"
        read -p "按回车继续..."
        
        echo ""
        echo "步骤 2: 在服务器上拉取代码"
        echo "-----------------------------------------"
        echo "命令:"
        echo "  ssh root@39.106.41.239"
        echo "  cd /var/www/eims"
        echo "  git pull origin main"
        read -p "按回车继续..."
        
        echo ""
        echo "步骤 3: 在服务器上更新依赖和配置"
        echo "-----------------------------------------"
        echo "命令:"
        echo "  source venv/bin/activate"
        echo "  pip install -r requirements.txt"
        echo "  python manage.py migrate --noinput"
        echo "  python manage.py collectstatic --noinput"
        echo "  supervisorctl restart eims"
        echo "  systemctl restart nginx"
        read -p "按回车继续..."
        
        echo ""
        echo "步骤 4: 单独同步数据库数据"
        echo "-----------------------------------------"
        echo "参考方式 B 的步骤 2-7"
        read -p "按回车继续..."
        
        echo ""
        echo "========================================="
        echo "Git 同步步骤已完成！"
        echo "========================================="
        ;;
    
    *)
        echo "无效选择，退出"
        exit 1
        ;;
esac

echo ""
echo "========================================="
echo "同步完成！"
echo "========================================="
echo ""
echo "验证步骤："
echo "  1. 访问 http://39.106.41.239 检查网站是否正常"
echo "  2. 登录系统验证数据完整性"
echo "  3. 测试各个功能模块"
echo ""
echo "如遇问题，请查看："
echo "  - 同步日志: /var/www/eims/logs/"
echo "  - Gunicorn 日志: supervisorctl status eims"
echo "  - Nginx 日志: /var/log/nginx/error.log"
echo ""
