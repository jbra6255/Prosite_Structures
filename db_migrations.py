import sqlite3
from typing import List, Dict, Any, Callable
import logging
from datetime import datetime

class DatabaseMigration:
    """
    A class to manage database schema migrations.
    Tracks schema version and applies necessary migrations in order.
    """
    
    def __init__(self, db_path: str, logger=None):
        """Initialize the migration manager with a database path and optional logger"""
        self.db_path = db_path
        self.logger = logger or logging.getLogger(__name__)
        self.migrations: List[Dict[str, Any]] = []
        
        # Ensure migration tracking table exists
        self._create_migration_table()
    
    def _create_migration_table(self):
        """Create the migration tracking table if it doesn't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        version INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        applied_at TIMESTAMP NOT NULL
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Failed to create migration table: {e}", exc_info=True)
            raise
    
    def register_migration(self, version: int, name: str, up_func: Callable, down_func: Callable = None):
        """Register a migration with up and optional down functions"""
        self.migrations.append({
            'version': version,
            'name': name,
            'up': up_func,
            'down': down_func
        })
        # Sort migrations by version to ensure they run in order
        self.migrations.sort(key=lambda m: m['version'])
    
    def get_current_version(self) -> int:
        """Get the current schema version from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT MAX(version) FROM schema_migrations')
                result = cursor.fetchone()
                return result[0] if result[0] is not None else 0
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get current schema version: {e}", exc_info=True)
            return 0
    
    def migrate(self, target_version: int = None):
        """
        Run migrations to reach the target version.
        If target_version is None, run all available migrations.
        """
        current_version = self.get_current_version()
        
        if target_version is None:
            # If no target specified, use the latest version
            if not self.migrations:
                return
            target_version = max(m['version'] for m in self.migrations)
        
        if current_version == target_version:
            self.logger.info(f"Database is already at version {current_version}")
            return
        
        if current_version > target_version:
            self._migrate_down(current_version, target_version)
        else:
            self._migrate_up(current_version, target_version)
    
    def _migrate_up(self, current_version: int, target_version: int):
        """Apply forward migrations to reach target version"""
        pending_migrations = [
            m for m in self.migrations 
            if current_version < m['version'] <= target_version
        ]
        
        if not pending_migrations:
            self.logger.info(f"No migrations needed to reach version {target_version}")
            return
        
        self.logger.info(f"Migrating UP from version {current_version} to {target_version}")
        
        for migration in pending_migrations:
            version = migration['version']
            name = migration['name']
            
            self.logger.info(f"Running migration {version}: {name}")
            
            try:
                with sqlite3.connect(self.db_path) as conn:
                    # Run the migration
                    migration['up'](conn)
                    
                    # Record the migration
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO schema_migrations (version, name, applied_at) 
                        VALUES (?, ?, ?)
                    ''', (version, name, datetime.now().isoformat()))
                    
                    conn.commit()
                    self.logger.info(f"Successfully applied migration {version}: {name}")
            except Exception as e:
                self.logger.error(f"Migration {version} failed: {e}", exc_info=True)
                # Don't break - try to continue with remaining migrations
    
    def _migrate_down(self, current_version: int, target_version: int):
        """Apply reverse migrations to reach target version"""
        pending_migrations = [
            m for m in self.migrations 
            if target_version < m['version'] <= current_version
        ]
        
        # Reverse the order for downgrading
        pending_migrations.reverse()
        
        if not pending_migrations:
            self.logger.info(f"No migrations needed to reach version {target_version}")
            return
        
        self.logger.info(f"Migrating DOWN from version {current_version} to {target_version}")
        
        for migration in pending_migrations:
            version = migration['version']
            name = migration['name']
            
            if migration['down'] is None:
                self.logger.warning(f"No down migration available for {version}: {name}")
                continue
            
            self.logger.info(f"Reverting migration {version}: {name}")
            
            try:
                with sqlite3.connect(self.db_path) as conn:
                    # Run the down migration
                    migration['down'](conn)
                    
                    # Remove the migration record
                    cursor = conn.cursor()
                    cursor.execute('''
                        DELETE FROM schema_migrations WHERE version = ?
                    ''', (version,))
                    
                    conn.commit()
                    self.logger.info(f"Successfully reverted migration {version}: {name}")
            except Exception as e:
                self.logger.error(f"Reverting migration {version} failed: {e}", exc_info=True)
                break

def column_exists(conn, table, column):
    """Check if a column exists in a table"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [info[1] for info in cursor.fetchall()]
    return column in columns

# Define our migrations for the structures database

def create_migrations(logger):
    """Create all migrations for the application"""
    migrations = DatabaseMigration("structures.db", logger)
    
    # Migration 1: Add description column to structures table
    def add_description_column_up(conn):
        cursor = conn.cursor()
        
        # Check if the column already exists first
        if not column_exists(conn, "structures", "description"):
            logger.info("Adding description column to structures table")
            cursor.execute("ALTER TABLE structures ADD COLUMN description TEXT")
        else:
            logger.info("Description column already exists in structures table")
    
    def add_description_column_down(conn):
        # SQLite doesn't support dropping columns directly
        # In a real implementation, you'd need to recreate the table
        pass
    
    migrations.register_migration(
        1, 
        "Add description column to structures",
        add_description_column_up,
        add_description_column_down
    )
    
    # Migration 2: Add frame_type column to structures table
    def add_frame_type_column_up(conn):
        cursor = conn.cursor()
        
        # Check if the column already exists first
        if not column_exists(conn, "structures", "frame_type"):
            logger.info("Adding frame_type column to structures table")
            cursor.execute("ALTER TABLE structures ADD COLUMN frame_type TEXT")
        else:
            logger.info("Frame_type column already exists in structures table")
    
    def add_frame_type_column_down(conn):
        # SQLite doesn't support dropping columns directly
        pass
    
    migrations.register_migration(
        2, 
        "Add frame_type column to structures",
        add_frame_type_column_up,
        add_frame_type_column_down
    )
    
    def add_pipe_types_configuration(conn):
        """Create pipe types configuration table and add initial pipe types"""
        cursor = conn.cursor()
        
        # Create pipe types table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pipe_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL
            )
        ''')
        
        # Add default pipe types
        default_pipe_types = [
            "RCP CL3 T&G",
            "RCP CL3 O-Ring",
            "RCP CL3 NCDOT",
            "RCP CL4 T&G",
            "RCP CL4 O-Ring",
            "RCP CL4 NCDOT"
        ]
        
        now = datetime.now().isoformat()
        for pipe_type in default_pipe_types:
            cursor.execute('''
                INSERT OR IGNORE INTO pipe_types (name, created_at, updated_at)
                VALUES (?, ?, ?)
            ''', (pipe_type, now, now))

    # Add this to your create_migrations function:
    migrations.register_migration(
        3, 
        "Add pipe types configuration",
        add_pipe_types_configuration,
        None  # No down migration
    )

    # Add more migrations here as needed
    
    return migrations