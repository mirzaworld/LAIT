#!/usr/bin/env python3
import os
import re

def fix_datetime_imports_and_calls(file_path):
    """Fix datetime imports and replace utcnow() calls"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (UnicodeDecodeError, UnicodeError):
        # Skip binary files
        return False
    
    original_content = content
    
    # Replace datetime.now(timezone.utc) with datetime.now(timezone.utc)
    content = re.sub(r'datetime\.utcnow\(\)', 'datetime.now(timezone.utc)', content)
    
    # Check if timezone is imported
    has_timezone_import = 'from datetime import' in content and 'timezone' in content
    has_datetime_import = 'import datetime' in content or 'from datetime import' in content
    
    if 'datetime.now(timezone.utc)' in content and not has_timezone_import and has_datetime_import:
        # Add timezone to existing datetime import
        if 'from datetime import datetime, timedelta' in content:
            content = content.replace(
                'from datetime import datetime, timedelta',
                'from datetime import datetime, timedelta, timezone'
            )
        elif 'from datetime import datetime' in content:
            content = content.replace(
                'from datetime import datetime',
                'from datetime import datetime, timezone'
            )
    
    if content != original_content:
        print(f"Fixed: {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return content != original_content

# Find all Python files and fix them
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.py'):
            file_path = os.path.join(root, file)
            fix_datetime_imports_and_calls(file_path)

print("DateTime fixes complete!")
