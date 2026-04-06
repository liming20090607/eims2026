# Sync User Data from Cloud Server to Local
# Usage: .\sync_users.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Sync User Data from Cloud Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server: 39.106.41.239" -ForegroundColor Yellow
Write-Host "Action: Export and import user accounts" -ForegroundColor Yellow
Write-Host ""
Write-Host "Note: You will need to enter the server root password" -ForegroundColor Magenta
Write-Host ""

$confirm = Read-Host "Continue? (y/n)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Cancelled" -ForegroundColor Yellow
    exit 0
}

# Step 1: Export user data from server
Write-Host ""
Write-Host "[Step 1/3] Exporting user data from server..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Gray

$sshCmd = 'ssh root@39.106.41.239 "cd /var/www/eims && source venv/bin/activate && python manage.py dumpdata auth.User auth.Group auth.Permission --indent 2 > /tmp/users_export.json"'

Write-Host "Connecting to server and exporting data..." -ForegroundColor Gray
Write-Host "Please enter the server root password" -ForegroundColor Magenta
Write-Host ""

Invoke-Expression $sshCmd

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Export FAILED!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "Export SUCCESS" -ForegroundColor Green
Write-Host ""

# Step 2: Download the exported data file
Write-Host "[Step 2/3] Downloading data file..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Gray

# Create fixtures directory
$fixturesDir = "eims_app\fixtures"
if (-not (Test-Path $fixturesDir)) {
    New-Item -ItemType Directory -Path $fixturesDir -Force | Out-Null
    Write-Host "Created directory: $fixturesDir" -ForegroundColor Gray
}

$scpCmd = "scp root@39.106.41.239:/tmp/users_export.json $fixturesDir\users_export.json"

Write-Host "Downloading file..." -ForegroundColor Gray
Write-Host "Please enter the server root password" -ForegroundColor Magenta
Write-Host ""

Invoke-Expression $scpCmd

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Download FAILED!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "Download SUCCESS" -ForegroundColor Green
Write-Host ""

# Step 3: Import data to local database
Write-Host "[Step 3/3] Importing data to local database..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Gray

$fixturePath = "$fixturesDir\users_export.json"

if (-not (Test-Path $fixturePath)) {
    Write-Host "File not found: $fixturePath" -ForegroundColor Red
    exit 1
}

# Check file size
$fileSize = (Get-Item $fixturePath).Length
Write-Host "File size: $fileSize bytes" -ForegroundColor Gray

if ($fileSize -lt 100) {
    Write-Host "WARNING: File may be empty or corrupted!" -ForegroundColor Yellow
    $continue = Read-Host "Continue importing? (y/n)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 0
    }
}

Write-Host ""
Write-Host "Importing data..." -ForegroundColor Gray
Write-Host ""

$loadDataCmd = "python manage.py loaddata $fixturePath"
Invoke-Expression $loadDataCmd

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Import FAILED!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "Import SUCCESS" -ForegroundColor Green
Write-Host ""

# Verify import results
Write-Host "[Verify] Checking import results..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Gray
Write-Host ""

python manage.py shell -c "from django.contrib.auth.models import User; from eims_app.models import UserProfile; print(f'User accounts: {User.objects.count()}'); print(f'User profiles: {UserProfile.objects.count()}'); users = User.objects.order_by('-id')[:5]; print('\nLatest 5 users:'); [print(f'  - {u.username} (ID:{u.id})') for u in users]"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   User Data Sync COMPLETED!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "You can now access:" -ForegroundColor Cyan
Write-Host "  User Management: http://127.0.0.1:8000/user-management/" -ForegroundColor White
Write-Host "  Django Admin: http://127.0.0.1:8000/admin/" -ForegroundColor White
Write-Host ""

# Clean up temporary file
$cleanup = Read-Host "Delete temporary file users_export.json? (y/n)"
if ($cleanup -eq "y" -or $cleanup -eq "Y") {
    Remove-Item $fixturePath -Force
    Write-Host "Temporary file deleted" -ForegroundColor Green
}

Write-Host ""
