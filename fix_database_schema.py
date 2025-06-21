"""
Simple database schema fix for LAIT
Adds missing columns to existing tables
"""

import sqlite3
import os
from pathlib import Path

def fix_database_schema():
    """Fix database schema issues"""
    
    # Get the database path
    db_path = "lait_enhanced.db"
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if is_flagged column exists in line_items table
        cursor.execute("PRAGMA table_info(line_items)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'is_flagged' not in columns:
            print("Adding is_flagged column to line_items table...")
            cursor.execute("ALTER TABLE line_items ADD COLUMN is_flagged BOOLEAN DEFAULT 0")
            
        if 'flag_reason' not in columns:
            print("Adding flag_reason column to line_items table...")
            cursor.execute("ALTER TABLE line_items ADD COLUMN flag_reason VARCHAR(255)")
            
        conn.commit()
        print("✅ Database schema updated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error updating database schema: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    fix_database_schema()
