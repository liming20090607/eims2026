#!/bin/bash
# 生产环境启动脚本
source /root/anaconda3/bin/activate
conda activate eims_env
cd /data/eims
supervisorctl start eims
echo "EIMS系统生产环境启动成功！"