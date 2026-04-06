# MySQL 密码重置指南
# 如果找不到密码，可以使用此方法重置

# ===== 方法 1：使用 root 用户重置密码 =====
# 使用 root 登录 MySQL
mysql -u root -p

# 在 MySQL 命令行中执行：
# USE mysql;
# ALTER USER 'eims_user'@'localhost' IDENTIFIED BY '新密码';
# FLUSH PRIVILEGES;
# EXIT;

# ===== 方法 2：忘记 root 密码时的重置方法 =====
# 1. 停止 MySQL 服务
# systemctl stop mysqld  或  systemctl stop mariadb

# 2. 以跳过权限表方式启动 MySQL
# mysqld_safe --skip-grant-tables &

# 3. 无密码登录 MySQL
# mysql -u root

# 4. 重置 eims_user 密码
# USE mysql;
# UPDATE user SET authentication_string=PASSWORD('新密码') WHERE User='eims_user' AND Host='localhost';
# FLUSH PRIVILEGES;
# EXIT;

# 5. 重启 MySQL 服务
# systemctl restart mysqld

# ===== 方法 3：创建新用户并授权 =====
# mysql -u root -p
# CREATE USER 'eims_user_new'@'localhost' IDENTIFIED BY '新密码';
# GRANT ALL PRIVILEGES ON eims_db.* TO 'eims_user_new'@'localhost';
# FLUSH PRIVILEGES;
# EXIT;
