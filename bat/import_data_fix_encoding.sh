#!/bin/bash

echo "======================================"
echo "EIMS Data Import - Fix Encoding
echo "======================================"
echo ""

# Check if files exist
if [ ! -f "/root/department_data.json" ]; then
    echo "ERROR: department_data.json not found"
    exit 1
fi

if [ ! -f "/root/role_data.json" ]; then
    echo "ERROR: role_data.json not found"
    exit 1
fi

echo "Files found. Starting encoding fix..."
echo ""

# Create Python script to fix encoding
cat > /tmp/fix_encoding.py << 'PYTHON_EOF'
#!/usr/bin/env python3
import sys
import os

def fix_encoding(filepath):
    """Convert file from GBK to UTF-8"""
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return False
    
    try:
        # Try reading as GBK
        with open(filepath, 'rb') as f:
            raw_content = f.read()
        
        # Try to decode as GBK
        try:
            content = raw_content.decode('gbk')
            
            # Write as UTF-8
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"SUCCESS: Fixed encoding for {filepath}")
            return True
            
        except UnicodeDecodeError:
            # Try UTF-8
            try:
                content = raw_content.decode('utf-8')
                print(f"INFO: Already UTF-8: {filepath}")
                return True
            except:
                print(f"ERROR: Unknown encoding: {filepath}")
                return False
                
    except Exception as e:
        print(f"ERROR: Failed to process {filepath}: {e}")
        return False

if __name__ == '__main__':
    files = sys.argv[1:]
    
    success_count = 0
    for filepath in files:
        if fix_encoding(filepath):
            success_count += 1
    
    print(f"\nProcessed {success_count}/{len(files)} files")
PYTHON_EOF

# Run the fix script
echo "[1/3] Fixing file encoding..."
python3 /tmp/fix_encoding.py /root/department_data.json /root/role_data.json

if [ $? -ne 0 ]; then
    echo "WARNING: Some files may still have encoding issues"
fi

echo ""
echo "[2/3] Importing data..."

# Navigate to project directory
cd /var/www/eims || exit 1

# Activate virtual environment
source venv/bin/activate

# Import department data
echo "Importing departments..."
python manage.py loaddata /root/department_data.json

if [ $? -eq 0 ]; then
    echo "  SUCCESS: Department data imported"
else
    echo "  ERROR: Failed to import department data"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check if JSON format is valid"
    echo "  2. Verify database connection"
    echo "  3. Check for ID conflicts"
    exit 1
fi

# Import role data
echo ""
echo "Importing roles..."
python manage.py loaddata /root/role_data.json

if [ $? -eq 0 ]; then
    echo "  SUCCESS: Role data imported"
else
    echo "  ERROR: Failed to import role data"
    exit 1
fi

echo ""
echo "[3/3] Verifying import..."
echo ""

# Get counts
DEPT_COUNT=$(python manage.py shell -c "from eims_app.models import Department; print(Department.objects.count())")
ROLE_COUNT=$(python manage.py shell -c "from eims_app.models import Role; print(Role.objects.count())")

echo "Import Statistics:"
echo "  Departments: $DEPT_COUNT"
echo "  Roles: $ROLE_COUNT"
echo ""

# Show sample data
echo "Sample departments:"
python manage.py shell -c "from eims_app.models import Department; [print(f'  - {d.department_code}: {d.department_name}') for d in Department.objects.all()[:5]]"

echo ""
echo "Sample roles:"
python manage.py shell -c "from eims_app.models import Role; [print(f'  - {r.get_role_display()}') for r in Role.objects.all()[:5]]"

echo ""
echo "======================================"
echo "Data import completed successfully!
echo "======================================"
echo ""
echo "Next steps:"
echo "  1. Visit your website to verify"
echo "  2. Check admin panel"
echo "  3. Test department and role functionality"
echo ""
