#!/bin/bash
# Create admin and root superuser accounts on server
# Run this script directly on the server via VS Code remote terminal

echo "=========================================="
echo "🔧 Creating admin and root accounts"
echo "=========================================="

cd /var/www/eims

# Step 1: Ensure databases exist
echo ""
echo "[1] Ensuring databases exist..."
mysql -u root -p"EIMS2026_mysql" -e "
CREATE DATABASE IF NOT EXISTS eims_dingce CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS eims_shengchang CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS eims_jiachengda CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS root_admin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
SHOW DATABASES LIKE 'eims_%';
SHOW DATABASES LIKE 'root_admin';
"

# Step 2: Run migrations
echo ""
echo "[2] Running database migrations..."
venv/bin/python manage.py migrate --database=root_admin

# Step 3: Create admin account
echo ""
echo "[3] Creating admin superuser..."
venv/bin/python manage.py shell << 'EOF'
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@eims.com',
        password='Admin@2026!'
    )
    print(f"✅ Created admin user (ID: {admin.id})")
else:
    admin = User.objects.get(username='admin')
    admin.set_password('Admin@2026!')
    admin.save()
    print(f"✅ Updated admin password (ID: {admin.id})")
EOF

# Step 4: Create root account
echo ""
echo "[4] Creating root superuser..."
venv/bin/python manage.py shell << 'EOF'
from django.contrib.auth.models import User
if not User.objects.filter(username='root').exists():
    root = User.objects.create_superuser(
        username='root',
        email='root@eims.com',
        password='Root@2026!'
    )
    print(f"✅ Created root user (ID: {root.id})")
else:
    root = User.objects.get(username='root')
    root.set_password('Root@2026!')
    root.save()
    print(f"✅ Updated root password (ID: {root.id})")
EOF

# Step 5: Verify accounts
echo ""
echo "[5] Verifying accounts..."
mysql -u root -p"EIMS2026_mysql" -e "
USE root_admin;
SELECT id, username, email, is_superuser, is_staff, is_active 
FROM auth_user 
WHERE username IN ('admin', 'root')
ORDER BY id;
"

# Summary
echo ""
echo "=========================================="
echo "📋 Account Credentials:"
echo "=========================================="
echo ""
echo "✅ Admin Account:"
echo "   Username: admin"
echo "   Password: Admin@2026!"
echo "   Email: admin@eims.com"
echo "   Role: Superuser (full access)"
echo ""
echo "✅ Root Account:"
echo "   Username: root"
echo "   Password: Root@2026!"
echo "   Email: root@eims.com"
echo "   Role: Superuser (full access)"
echo ""
echo "⚠️  IMPORTANT:"
echo "   1. Change passwords after first login"
echo "   2. Login URL: http://www.xietongai.com.cn/login/"
echo "=========================================="
