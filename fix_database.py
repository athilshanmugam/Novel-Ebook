#!/usr/bin/env python3
import sqlite3
import os
from datetime import datetime

def fix_database_schema():
    """Fix the database schema by creating a new table with correct structure"""
    print("=== Fixing Database Schema ===")
    
    try:
        # Connect to database
        conn = sqlite3.connect('names.db')
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute('PRAGMA table_info(user_names)')
        current_columns = [row[1] for row in cursor.fetchall()]
        print(f"Current columns: {current_columns}")
        
        # Backup existing data
        cursor.execute('SELECT * FROM user_names')
        existing_data = cursor.fetchall()
        print(f"Found {len(existing_data)} existing records to backup")
        
        # Create new table with correct schema
        print("Creating new table with correct schema...")
        cursor.execute('DROP TABLE IF EXISTS user_names_new')
        cursor.execute('''
            CREATE TABLE user_names_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                female_name TEXT NOT NULL,
                male_name TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                usage_count INTEGER DEFAULT 1
            )
        ''')
        
        # Migrate existing data
        print("Migrating existing data...")
        for i, row in enumerate(existing_data):
            # Handle different possible old schemas
            if len(row) >= 3:
                # Old schema: female_name, male_name, timestamp
                female_name = row[0] if row[0] else ''
                male_name = row[1] if row[1] else ''
                timestamp = row[2] if row[2] else datetime.now()
            elif len(row) >= 2:
                # Minimal schema: female_name, male_name
                female_name = row[0] if row[0] else ''
                male_name = row[1] if row[1] else ''
                timestamp = datetime.now()
            else:
                continue
            
            # Generate a default user_id for existing records
            default_user_id = f"migrated_user_{i+1}"
            
            cursor.execute('''
                INSERT INTO user_names_new (user_id, female_name, male_name, created_at, usage_count)
                VALUES (?, ?, ?, ?, ?)
            ''', (default_user_id, female_name, male_name, timestamp, 1))
        
        # Replace old table with new one
        print("Replacing old table...")
        cursor.execute('DROP TABLE user_names')
        cursor.execute('ALTER TABLE user_names_new RENAME TO user_names')
        
        # Commit changes
        conn.commit()
        print("✅ Database schema fixed successfully!")
        
        # Verify the new schema
        cursor.execute('PRAGMA table_info(user_names)')
        new_columns = [row[1] for row in cursor.fetchall()]
        print(f"New schema columns: {new_columns}")
        
        # Check data
        cursor.execute('SELECT COUNT(*) FROM user_names')
        count = cursor.fetchone()[0]
        print(f"Total records in new table: {count}")
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_database_schema() 