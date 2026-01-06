import sqlite3
from sqlite3 import Error, IntegrityError, OperationalError
from typing import List, Tuple
import logging
from logger import AppLogger
from db_migrations import create_migrations

class DatabaseManager:
    def __init__(self, db_path: str = "structures.db"):
        """Initialize the database manager and run migrations"""
        self.db_path = db_path
        self.logger = AppLogger().logger
        
        # Create base tables
        self.initialize_database()
        
        # Setup and run migrations
        self.migrations = create_migrations(self.db_path, self.logger)
        current_version = self.migrations.get_current_version()
        self.migrations.migrate()  # Migrate to latest version
        latest_version = self.migrations.get_current_version()
        
        if current_version != latest_version:
            self.logger.info(f"Database migrated from version {current_version} to {latest_version}")
        else:
            self.logger.info(f"Database is at the latest version: {current_version}")

        # Verify Database Table Consistancy
        if not self.verify_table_consistency():
            self.logger.warning("Table schema verification failed - some operations may not work correctly")
        else:
            self.logger.info("Table schema verification passed")
        
        # Initialize default component types
        self.initialize_component_types()
        
        self.logger.info(f"Database initialized: {db_path}")

    def initialize_database(self):
        """Create base tables if they don't exist (migration system will handle schema evolution)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                
                # Create users table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        created_at TIMESTAMP NOT NULL
                    )
                ''')
                
                # Create projects table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS projects (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT,
                        owner_id INTEGER NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL,
                        FOREIGN KEY (owner_id) REFERENCES users (id),
                        UNIQUE (name, owner_id)
                    )
                ''')
                
                # Create project_sharing table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS project_sharing (
                        project_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        role TEXT NOT NULL,
                        shared_at TIMESTAMP NOT NULL,
                        FOREIGN KEY (project_id) REFERENCES projects (id),
                        FOREIGN KEY (user_id) REFERENCES users (id),
                        PRIMARY KEY (project_id, user_id)
                    )
                ''')
                
                # Create structures table with core fields only
                # Additional fields like description and frame_type will be added through migrations
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS structures (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        structure_id TEXT NOT NULL,
                        structure_type TEXT NOT NULL,
                        rim_elevation REAL NOT NULL,
                        invert_out_elevation REAL NOT NULL,
                        invert_out_angle INTEGER,
                        vert_drop REAL,
                        upstream_structure_id TEXT,
                        pipe_length REAL,
                        pipe_diameter REAL,
                        pipe_type TEXT,
                        group_name TEXT,
                        project_id INTEGER NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL,
                        FOREIGN KEY (upstream_structure_id, project_id) REFERENCES structures (structure_id, project_id),
                        FOREIGN KEY (project_id) REFERENCES projects (id),
                        UNIQUE (structure_id, project_id)
                    )
                ''')
                
                # Create structure groups table with project_id
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS structure_groups (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT,
                        project_id INTEGER NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL,
                        FOREIGN KEY (project_id) REFERENCES projects (id),
                        UNIQUE (name, project_id)
                    )
                ''')
                
                # Create group memberships table for many-to-many relationship
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS group_memberships (
                        group_id INTEGER,
                        structure_id TEXT,
                        project_id INTEGER,
                        added_at TIMESTAMP NOT NULL,
                        FOREIGN KEY (group_id) REFERENCES structure_groups (id),
                        FOREIGN KEY (structure_id, project_id) REFERENCES structures (structure_id, project_id),
                        FOREIGN KEY (project_id) REFERENCES projects (id),
                        PRIMARY KEY (group_id, structure_id, project_id)
                    )
                ''')

                # Create structure component types table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS structure_component_types (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT,
                        created_at TIMESTAMP NOT NULL,
                        UNIQUE (name)
                    )
                ''')

                # Create structure components table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS structure_components (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        structure_id TEXT NOT NULL,
                        project_id INTEGER NOT NULL,
                        component_type_id INTEGER NOT NULL,
                        status TEXT NOT NULL,
                        order_date TIMESTAMP,
                        expected_delivery_date TIMESTAMP,
                        actual_delivery_date TIMESTAMP,
                        notes TEXT,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL,
                        FOREIGN KEY (structure_id, project_id) REFERENCES structures (structure_id, project_id),
                        FOREIGN KEY (component_type_id) REFERENCES structure_component_types (id),
                        FOREIGN KEY (project_id) REFERENCES projects (id)
                    )
                ''')

                # Create pipe_orders table if it doesn't exist
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS pipe_orders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        order_number TEXT NOT NULL,
                        supplier TEXT,
                        project_id INTEGER NOT NULL,
                        status TEXT NOT NULL DEFAULT 'pending',
                        order_date TIMESTAMP NOT NULL,
                        expected_delivery_date TIMESTAMP,
                        actual_delivery_date TIMESTAMP,
                        notes TEXT,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL,
                        FOREIGN KEY (project_id) REFERENCES projects (id),
                        UNIQUE (order_number, project_id)
                    )
                ''')
                
                # Create pipe_order_items table if it doesn't exist
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS pipe_order_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        order_id INTEGER NOT NULL,
                        structure_id TEXT NOT NULL,
                        pipe_type TEXT NOT NULL,
                        diameter REAL NOT NULL,
                        length REAL NOT NULL,
                        delivered_length REAL DEFAULT 0,
                        status TEXT NOT NULL DEFAULT 'pending',
                        notes TEXT,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL,
                        FOREIGN KEY (order_id) REFERENCES pipe_orders (id) ON DELETE CASCADE,
                        FOREIGN KEY (structure_id, order_id) REFERENCES structures (structure_id, project_id)
                    )
                ''')

        except sqlite3.Error as e:
            self.logger.critical(f"Database initialization failed: {e}", exc_info=True)
            raise

    def _get_structures_table_columns(self) -> List[Tuple[str, str]]:
        """
        Get column information for the structures table.
        Returns list of (column_name, column_type) tuples.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(structures)")
                columns_info = cursor.fetchall()
                # Return (name, type) tuples
                return [(col[1], col[2]) for col in columns_info]
        except sqlite3.Error as e:
            self.logger.error(f"Error getting table column info: {e}", exc_info=True)
            return []

    def verify_table_consistency(self):
        """
        Verify that the structures table schema matches expectations.
        Call this during initialization to catch schema issues early.
        """
        expected_columns = [
            'id', 'structure_id', 'structure_type', 'rim_elevation', 
            'invert_out_elevation', 'invert_out_angle', 'vert_drop',
            'upstream_structure_id', 'pipe_length', 'pipe_diameter', 
            'pipe_type', 'group_name', 'project_id', 'created_at', 
            'updated_at', 'frame_type', 'description', 'run_designation', 
            'upstream_run_designation', 'is_primary_run'
        ]
        
        try:
            column_info = self._get_structures_table_columns()
            actual_columns = [col[0] for col in column_info]
            
            missing_columns = set(expected_columns) - set(actual_columns)
            extra_columns = set(actual_columns) - set(expected_columns)
            
            if missing_columns:
                self.logger.warning(f"Missing expected columns: {missing_columns}")
            if extra_columns:
                self.logger.info(f"Extra columns found: {extra_columns}")
                
            self.logger.info(f"Table has {len(actual_columns)} columns, expected {len(expected_columns)}")
            
            return len(missing_columns) == 0  # Return True if no missing columns
            
        except Exception as e:
            self.logger.error(f"Error verifying table consistency: {e}")
            return False