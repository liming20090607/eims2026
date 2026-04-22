@echo off
echo ======================================================================
echo MySQL Emergency Fix via SSH
echo ======================================================================
echo.

REM Use plink (PuTTY Link) or ssh with password in environment
set SSHPASS=fjkl546#

echo [1/3] Stopping MySQL and cleaning up...
sshpass -p "%SSHPASS%" ssh -o StrictHostKeyChecking=no root@39.106.41.239 "killall -9 mysqld mysqld_safe 2>/dev/null; rm -f /var/lib/mysql/mysql.sock; sleep 2"

echo [2/3] Starting MySQL in recovery mode and resetting password...
sshpass -p "%SSHPASS%" ssh -o StrictHostKeyChecking=no root@39.106.41.239 ^
"mysqld --user=mysql --skip-grant-tables --socket=/var/lib/mysql/mysql.sock ^&
sleep 10 ^&^&
mysql -u root --socket=/var/lib/mysql/mysql.sock -e \"
FLUSH PRIVILEGES;
DROP USER IF EXISTS 'root'@'localhost';
CREATE USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'EIMS2026_mysql';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;\" ^&^&
mysqladmin -u root --socket=/var/lib/mysql/mysql.sock shutdown ^&^&
sleep 3 ^&^&
systemctl start mysqld || service mysql start"

echo [3/3] Verifying fix...
timeout /t 10 /nobreak >nul
sshpass -p "%SSHPASS%" ssh -o StrictHostKeyChecking=no root@39.106.41.239 "mysql -uroot -pEIMS2026_mysql -e 'SELECT 1 AS test;'"

echo.
echo ======================================================================
echo Fix complete! Please check the output above.
echo ======================================================================
pause
