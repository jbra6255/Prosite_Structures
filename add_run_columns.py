import sqlite3
import logging
from datetime import datetime

def column_exists(conn, table, column):
    """Check if a column exists in a table"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [info[1] for info in cursor.fetchall()]
    return column in columns

def add_run_support():
    """Add the new columns to support multiple runs per structure"""
    db_path = "structures.db"
    
    print("Adding run support to database...")
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Show current structure
            print("Current table structure:")
            cursor.execute("PRAGMA table_info(structures)")
            for col in cursor.fetchall():
                print(f"  {col[1]} ({col[2]})")
            
            print("\nAdding new columns...")
            
            # Add the new columns that match your models.py
            new_columns = [
                ("run_designation", "TEXT DEFAULT 'A'"),
                ("upstream_run_designation", "TEXT"),
                ("is_primary_run", "INTEGER DEFAULT 1")
            ]
            
            changes_made = False
            for column_name, column_def in new_columns:
                if not column_exists(conn, "structures", column_name):
                    print(f"  Adding {column_name}...")
                    cursor.execute(f"ALTER TABLE structures ADD COLUMN {column_name} {column_def}")
                    changes_made = True
                else:
                    print(f"  {column_name} already exists")
            
            if changes_made:
                # Update existing structures to have proper default values
                print("Updating existing structures with default values...")
                cursor.execute("""
                    UPDATE structures 
                    SET run_designation = 'A', is_primary_run = 1 
                    WHERE run_designation IS NULL OR run_designation = '' OR is_primary_run IS NULL
                """)
                
                rows_updated = cursor.rowcount
                print(f"Updated {rows_updated} existing structures")
            
            # Create the schema_migrations table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    applied_at TIMESTAMP NOT NULL
                )
            ''')
            
            # Record this migration if it hasn't been recorded yet
            cursor.execute("SELECT COUNT(*) FROM schema_migrations WHERE version = 4")
            if cursor.fetchone()[0] == 0:
                now = datetime.now().isoformat()
                cursor.execute('''
                    INSERT INTO schema_migrations (version, name, applied_at) 
                    VALUES (?, ?, ?)
                ''', (4, "Add run support for multiple inverts per structure", now))
                print("Recorded migration in schema_migrations table")
            
            conn.commit()
            
            # Show final structure
            print("\nFinal table structure:")
            cursor.execute("PRAGMA table_info(structures)")
            for col in cursor.fetchall():
                print(f"  {col[1]} ({col[2]})")
            
            print("\n✅ Database migration completed successfully!")
            print("You can now add multiple runs per structure (e.g., MH-31-A, MH-31-B, MH-31-C)")
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_run_support()