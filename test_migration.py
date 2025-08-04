#!/usr/bin/env python3
import sqlite3
import sys
import os

# Add the current directory to Python path to import from app.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import init_db, migrate_database

def check_database_schema():
    """Check the current database schema"""
    print("=== Checking Database Schema ===")
    
    try:
        conn = sqlite3.connect('names.db')
        cursor = conn.cursor()
        
        # Check if user_names table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_names'")
        if not cursor.fetchone():
            print("❌ user_names table does not exist")
            return False
        
        # Get table schema
        cursor.execute('PRAGMA table_info(user_names)')
        columns = cursor.fetchall()
        
        print("Current user_names table schema:")
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
        
        # Check for required columns
        required_columns = ['id', 'user_id', 'female_name', 'male_name', 'created_at', 'usage_count']
        current_columns = [col[1] for col in columns]
        
        missing_columns = [col for col in required_columns if col not in current_columns]
        
        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
            return False
        else:
            print("✅ All required columns present")
            return True
            
    except Exception as e:
        print(f"❌ Error checking schema: {e}")
        return False
    finally:
        conn.close()

def main():
    print("=== Database Migration Test ===")
    
    # Check initial schema
    print("\n1. Checking initial schema...")
    initial_ok = check_database_schema()
    
    if not initial_ok:
        print("\n2. Running database migration...")
        try:
            migrate_database()
            print("✅ Migration completed")
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return
    
    # Check final schema
    print("\n3. Checking final schema...")
    final_ok = check_database_schema()
    
    if final_ok:
        print("\n✅ Database schema is now correct!")
    else:
        print("\n❌ Database schema still has issues")

if __name__ == "__main__":
    main() 