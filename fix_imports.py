#!/usr/bin/env python3
"""
Script to fix import statements in the backend directory.
Changes 'from backend.X' to 'from X' for relative imports within the backend.
"""

import os
import re

def fix_imports_in_file(filepath):
    """Fix backend imports in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match 'from backend.X import Y'
        pattern = r'from backend\.([a-zA-Z_][a-zA-Z0-9_.]*)( import .+)'
        
        # Replace with 'from X import Y'
        new_content = re.sub(pattern, r'from \1\2', content)
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Fixed imports in: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def fix_imports_in_directory(directory):
    """Fix imports in all Python files in a directory."""
    fixed_count = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if fix_imports_in_file(filepath):
                    fixed_count += 1
    
    return fixed_count

if __name__ == "__main__":
    backend_dir = "backend"
    if os.path.exists(backend_dir):
        print(f"Fixing imports in {backend_dir} directory...")
        count = fix_imports_in_directory(backend_dir)
        print(f"Fixed imports in {count} files.")
    else:
        print(f"Directory {backend_dir} not found!")
