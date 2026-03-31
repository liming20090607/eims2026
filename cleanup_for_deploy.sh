#!/bin/bash
# EIMS 部署前清理脚本
# 用于删除开发环境的冗余文件

echo "======================================"
echo "EIMS 部署前清理工具"
echo "======================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 统计
deleted_count=0
skipped_count=0

# 函数：删除文件
delete_files() {
    local pattern=$1
    local description=$2
    
    echo -e "${BLUE}正在清理：${description}${NC}"
    
    for file in $pattern; do
        if [ -f "$file" ]; then
            rm -v "$file"
            ((deleted_count++))
        fi
    done
}

# 确认提示
echo -e "${YELLOW}即将删除以下类型的文件:${NC}"
echo "  - 测试文件 (test_*.py)"
echo "  - 调试文件 (debug_*.py)"
echo "  - 检查脚本 (check_*.py)"
echo "  - Windows 批处理文件 (*.bat, *.lnk)"
echo ""

read -p "是否继续？这将永久删除文件 [y/N]: " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}已取消清理操作${NC}"
    exit 0
fi

echo ""
echo "开始清理..."
echo "----------------------------------------"

# 1. 清理测试文件
delete_files "test_*.py" "测试文件"

# 2. 清理调试文件
delete_files "debug_*.py" "调试文件"

# 3. 清理检查脚本
delete_files "check_*.py" "检查脚本"

# 4. 清理 Windows 批处理文件（可选）
echo -e "${BLUE}正在清理：Windows 批处理文件${NC}"
for file in *.bat *.lnk; do
    if [ -f "$file" ]; then
        # 保留重要的批处理文件
        case "$file" in
            "restore_db.BAT"|"setup_backup.BAT"|"backup_auto.BAT")
                echo -e "${YELLOW}跳过：$file (备份相关，建议保留)${NC}"
                ((skipped_count++))
                ;;
            *)
                rm -v "$file"
                ((deleted_count++))
                ;;
        esac
    fi
done

# 5. 清理一次性脚本（可选）
echo ""
echo -e "${YELLOW}以下是一次性脚本，是否删除？${NC}"
one_time_scripts=(
    "add_is_deleted_field.py"
    "add_remark_field.py"
    "fix_contract_table_complete.py"
    "fix_personnel_db.py"
    "manage_user_names.py"
    "migrate_file_manage.py"
    "migrate_old_data.py"
    "recreate_contract_table.py"
    "reset_file_manage.py"
    "set_user_chinese_names.py"
    "update_db.py"
    "update_publish_time.py"
)

for script in "${one_time_scripts[@]}"; do
    if [ -f "$script" ]; then
        read -p "删除 $script ? [y/N]: " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -v "$script"
            ((deleted_count++))
        else
            echo -e "${YELLOW}跳过：$script${NC}"
            ((skipped_count++))
        fi
    fi
done

echo ""
echo "----------------------------------------"
echo -e "${GREEN}✓ 清理完成！${NC}"
echo ""
echo "统计:"
echo "  - 已删除文件数：${deleted_count}"
echo "  - 跳过文件数：${skipped_count}"
echo ""

# 显示保留的重要文件
echo -e "${BLUE}保留的重要文件:${NC}"
echo "  ✓ settings.py / settings_production.py"
echo "  ✓ .env"
echo "  ✓ urls.py"
echo "  ✓ manage.py"
echo "  ✓ requirements.txt"
echo "  ✓ docs/ (所有文档)"
echo "  ✓ backup_before_phase4.json (数据备份)"
echo ""

echo -e "${YELLOW}下一步操作:${NC}"
echo "  1. 检查 .env 文件配置"
echo "  2. 修改 MySQL 数据库配置"
echo "  3. 生成新的 SECRET_KEY"
echo "  4. 设置 ALLOWED_HOSTS"
echo "  5. 关闭 DEBUG 模式"
echo ""
