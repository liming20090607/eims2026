# EIMS MySQL Local Setup Script
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "MySQL Local Setup Tool" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

$MYSQL_HOME = "C:\Program Files\MySQL\MySQL Server 8.0"
$MYSQL_BIN = "$MYSQL_HOME\bin"

# Check MySQL installation
if (-not (Test-Path $MYSQL_BIN)) {
    Write-Host "[ERROR] MySQL not installed at: $MYSQL_HOME" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] MySQL installed: $MYSQL_HOME" -ForegroundColor Green

# Add MySQL to PATH (current session)
$env:Path += ";$MYSQL_BIN"

# Check if service exists
$serviceName = "MySQL80"
$service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue

if ($service) {
    Write-Host "[OK] MySQL service exists: $serviceName" -ForegroundColor Green
    Write-Host "    Status: $($service.Status)" -ForegroundColor Yellow
} else {
    Write-Host "[1/5] Initialize MySQL data directory..." -ForegroundColor Yellow
    Set-Location $MYSQL_BIN
    & .\mysqld.exe --initialize-insecure --user=mysql
    Start-Sleep -Seconds 5

    Write-Host "[2/5] Install MySQL service..." -ForegroundColor Yellow
    & .\mysqld.exe --install $serviceName
    Start-Sleep -Seconds 2

    Write-Host "[OK] MySQL service created" -ForegroundColor Green
}

# Start service
Write-Host "[3/5] Start MySQL service..." -ForegroundColor Yellow
try {
    Start-Service -Name $serviceName
    Start-Sleep -Seconds 3
    Write-Host "[OK] MySQL service started" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Cannot start MySQL service: $_" -ForegroundColor Red
    exit 1
}

# Set root password
Write-Host "[4/5] Set MySQL root password..." -ForegroundColor Yellow
& "$MYSQL_BIN\mysql.exe" -u root --execute="ALTER USER 'root'@'localhost' IDENTIFIED BY 'root123'; FLUSH PRIVILEGES;"
Start-Sleep -Seconds 2

# Create database
Write-Host "[5/5] Create EIMS database..." -ForegroundColor Yellow
& "$MYSQL_BIN\mysql.exe" -u root -proot123 --execute="CREATE DATABASE IF NOT EXISTS eims DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
& "$MYSQL_BIN\mysql.exe" -u root -proot123 --execute="SHOW DATABASES;"

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Database Info:" -ForegroundColor Yellow
Write-Host "  - Host: localhost" -ForegroundColor White
Write-Host "  - Port: 3306" -ForegroundColor White
Write-Host "  - Database: eims" -ForegroundColor White
Write-Host "  - Username: root" -ForegroundColor White
Write-Host "  - Password: root123" -ForegroundColor White
Write-Host ""
