import sqlite3
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

def fix_migration_state():
    """
    This script fixes the migration state by checking which columns 
    already exist in the structures table and then updating the
    schema_migrations table accordingly.
    """
    db_path = "structures.db"
    
    logger.info("Starting migration state fix for %s", db_path)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the schema_migrations table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'")
        if not cursor.fetchone():
            logger.info("Creating schema_migrations table")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    applied_at TIMESTAMP NOT NULL
                )
            ''')
        
        # Check if the structures table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='structures'")
        if not cursor.fetchone():
            logger.error("Structures table doesn't exist! Cannot fix migration state.")
            return
        
        # Get existing columns in the structures table
        cursor.execute("PRAGMA table_info(structures)")
        columns = [info[1] for info in cursor.fetchall()]
        
        # Check for our migrated columns
        has_description = "description" in columns
        has_frame_type = "frame_type" in columns
        
        # Clean out any existing migration records to avoid duplicates
        cursor.execute("DELETE FROM schema_migrations WHERE version IN (1, 2)")
        
        now = datetime.now().isoformat()
        
        # Record migrations based on what columns exist
        if has_description:
            logger.info("Recording migration 1 (description column) as applied")
            cursor.execute('''
                INSERT INTO schema_migrations (version, name, applied_at) 
                VALUES (?, ?, ?)
            ''', (1, "Add description column to structures", now))
        
        if has_frame_type:
            logger.info("Recording migration 2 (frame_type column) as applied")
            cursor.execute('''
                INSERT INTO schema_migrations (version, name, applied_at) 
                VALUES (?, ?, ?)
            ''', (2, "Add frame_type column to structures", now))
        
        conn.commit()
        
        # Get the current migration version
        cursor.execute("SELECT MAX(version) FROM schema_migrations")
        version = cursor.fetchone()[0] or 0
        logger.info("Database migration state fixed. Current version: %s", version)
        
    except sqlite3.Error as e:
        logger.error("Database error: %s", e)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    fix_migration_state()