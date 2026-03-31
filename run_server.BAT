@echo off
chcp 65001 > nul
echo ============== 启动EIMS系统 ==============

:: 激活conda环境
call conda activate eims_env

:: 数据库迁移
python manage.py makemigrations eims_app
python manage.py migrate

:: 导入初始测试数据
echo 正在导入初始测试数据...
python manage.py loaddata eims_app\fixtures\initial_data.json

:: 创建超级用户（首次运行）
echo 请创建超级用户（用于后台管理）：
python manage.py createsuperuser

:: 启动开发服务器
python manage.py runserver 0.0.0.0:8000

pause