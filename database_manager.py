import models
print("Models module location:", models.__file__)
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from models import Structure, StructureGroup, ComponentType, StructureComponent
import hashlib
import logging
from logger import AppLogger
from sqlite3 import Error, IntegrityError, OperationalError, ProgrammingError
from db_migrations import create_migrations

class User:
    def __init__(self, id: int, username: str, email: str):
        self.id = id
        self.username = username
        self.email = email

class Project:
    def __init__(self, id: int, name: str, owner_id: int, description: str = ""):
        self.id = id
        self.name = name
        self.owner_id = owner_id
        self.description = description

class DatabaseManager:
    def __init__(self, db_path: str = "structures.db"):
        """Initialize the database manager and run migrations"""
        self.db_path = db_path
        self.logger = AppLogger().logger
        
        # Create base tables
        self.initialize_database()
        
        # Setup and run migrations
        self.migrations = create_migrations(self.logger)
        current_version = self.migrations.get_current_version()
        self.migrations.migrate()  # Migrate to latest version
        latest_version = self.migrations.get_current_version()
        
        if current_version != latest_version:
            self.logger.info(f"Database migrated from version {current_version} to {latest_version}")
        else:
            self.logger.info(f"Database is at the latest version: {current_version}")
        
        # Initialize default component types
        self.initialize_component_types()
        
        self.logger.info(f"Database initialized: {db_path}")

    def initialize_database(self):
        """Create base tables if they don't exist (migration system will handle schema evolution)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
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
                
                # No need to check for columns here anymore - migrations will handle that

        except sqlite3.Error as e:
            self.logger.critical(f"Database initialization failed: {e}", exc_info=True)
            raise
    
        # === Component Management Methods ===

    def initialize_component_types(self):
        """Initialize default component types if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if component types exist
                cursor.execute("SELECT COUNT(*) FROM structure_component_types")
                count = cursor.fetchone()[0]
                
                if count == 0:
                    # Add default component types
                    now = datetime.now().isoformat()
                    default_types = [
                        ("Base", "Structure base component"),
                        ("Riser", "Vertical riser component"),
                        ("Lid", "Structure top/lid component"),
                        ("Frame", "Structure frame component")
                    ]
                    
                    for name, description in default_types:
                        cursor.execute('''
                            INSERT INTO structure_component_types (name, description, created_at)
                            VALUES (?, ?, ?)
                        ''', (name, description, now))
                    
                    self.logger.info(f"Initialized default component types: {len(default_types)}")
        except sqlite3.Error as e:
            self.logger.error(f"Error initializing component types: {e}", exc_info=True)
            
    def get_all_component_types(self) -> List[ComponentType]:
        """Get all component types"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, description, created_at
                    FROM structure_component_types
                    ORDER BY name
                ''')
                
                types = []
                for row in cursor.fetchall():
                    types.append(ComponentType(
                        id=row[0],
                        name=row[1],
                        description=row[2],
                        created_at=self.safe_date_parse(row[3])
                    ))
                return types
        except sqlite3.Error as e:
            self.logger.error(f"Error getting component types: {e}", exc_info=True)
            return []

    def get_structure_components(self, structure_id: str, project_id: int) -> List[StructureComponent]:
        """Get all components for a structure"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT sc.id, sc.structure_id, sc.component_type_id, sc.status,
                        sc.order_date, sc.expected_delivery_date, sc.actual_delivery_date,
                        sc.notes, sc.created_at, sc.updated_at, ct.name
                    FROM structure_components sc
                    JOIN structure_component_types ct ON sc.component_type_id = ct.id
                    WHERE sc.structure_id = ? AND sc.project_id = ?
                    ORDER BY ct.name
                ''', (structure_id, project_id))
                
                components = []
                for row in cursor.fetchall():
                    components.append(StructureComponent(
                        id=row[0],
                        structure_id=row[1],
                        component_type_id=row[2],
                        status=row[3],
                        order_date=self.safe_date_parse(row[4]),
                        expected_delivery_date=self.safe_date_parse(row[5]),
                        actual_delivery_date=self.safe_date_parse(row[6]),
                        notes=row[7],
                        created_at=self.safe_date_parse(row[8]),
                        updated_at=self.safe_date_parse(row[9]),
                        component_type_name=row[10],
                        project_id=project_id
                    ))
                return components
        except sqlite3.Error as e:
            self.logger.error(f"Error getting structure components: {e}", exc_info=True)
            return []
            
    def add_structure_component(self, component: StructureComponent, project_id: int) -> bool:
        """Add a new component for a structure"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                
                # Format dates properly
                order_date = component.order_date.isoformat() if component.order_date else None
                expected_date = component.expected_delivery_date.isoformat() if component.expected_delivery_date else None
                actual_date = component.actual_delivery_date.isoformat() if component.actual_delivery_date else None
                
                cursor.execute('''
                    INSERT INTO structure_components (
                        structure_id, project_id, component_type_id, status,
                        order_date, expected_delivery_date, actual_delivery_date,
                        notes, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    component.structure_id, project_id, component.component_type_id,
                    component.status, order_date, expected_date, actual_date,
                    component.notes, now, now
                ))
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Error adding structure component: {e}", exc_info=True)
            return False
            
    def update_component_status(self, component_id: int, status: str, notes: str = None,
                            actual_delivery_date: datetime = None) -> bool:
        """Update a component's status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                
                # Format date properly
                delivery_date = actual_delivery_date.isoformat() if actual_delivery_date else None
                
                if notes:
                    cursor.execute('''
                        UPDATE structure_components SET
                            status = ?,
                            notes = ?,
                            actual_delivery_date = ?,
                            updated_at = ?
                        WHERE id = ?
                    ''', (status, notes, delivery_date, now, component_id))
                else:
                    cursor.execute('''
                        UPDATE structure_components SET
                            status = ?,
                            actual_delivery_date = ?,
                            updated_at = ?
                        WHERE id = ?
                    ''', (status, delivery_date, now, component_id))
                    
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            self.logger.error(f"Error updating component status: {e}", exc_info=True)
            return False
            
    def delete_structure_component(self, component_id: int) -> bool:
        """Delete a structure component"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM structure_components WHERE id = ?
                ''', (component_id,))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting component: {e}", exc_info=True)
            return False
    
    # === User Management Methods ===
    
    def create_user(self, username: str, email: str, password: str) -> Optional[User]:
        """Create a new user account"""
        try:
            # Hash the password
            password_hash = self._hash_password(password)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (username, email, password_hash, now))
                
                user_id = cursor.lastrowid
                return User(id=user_id, username=username, email=email)
        except sqlite3.IntegrityError:
            # Username or email already exists
            return None
        except sqlite3.Error as e:
            print(f"Error creating user: {e}")
            return None
            
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get user by username
                cursor.execute('''
                    SELECT id, username, email, password_hash FROM users
                    WHERE username = ?
                ''', (username,))
                
                user_row = cursor.fetchone()
                if not user_row:
                    return None
                    
                # Verify password
                stored_hash = user_row[3]
                if self._verify_password(password, stored_hash):
                    return User(id=user_row[0], username=user_row[1], email=user_row[2])
                    
                return None
        except sqlite3.Error as e:
            print(f"Error authenticating user: {e}")
            return None
            
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, username, email FROM users
                    WHERE username = ?
                ''', (username,))
                
                user_row = cursor.fetchone()
                if user_row:
                    return User(id=user_row[0], username=user_row[1], email=user_row[2])
                return None
        except sqlite3.Error as e:
            print(f"Error getting user: {e}")
            return None
            
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
        
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against a hash"""
        return self._hash_password(password) == password_hash
    
    # === Project Management Methods ===
    
    def create_project(self, name: str, owner_id: int, description: str = "") -> Optional[Project]:
        """Create a new project"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                
                cursor.execute('''
                    INSERT INTO projects (name, description, owner_id, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (name, description, owner_id, now, now))
                
                project_id = cursor.lastrowid
                return Project(id=project_id, name=name, owner_id=owner_id, description=description)
        except sqlite3.IntegrityError:
            # Project name already exists for this owner
            return None
        except sqlite3.Error as e:
            print(f"Error creating project: {e}")
            return None
    
    def get_project(self, project_id: int) -> Optional[Project]:
        """Get a project by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, name, owner_id, description FROM projects
                    WHERE id = ?
                ''', (project_id,))
                
                project_row = cursor.fetchone()
                if project_row:
                    return Project(
                        id=project_row[0], 
                        name=project_row[1], 
                        owner_id=project_row[2],
                        description=project_row[3]
                    )
                return None
        except sqlite3.Error as e:
            print(f"Error getting project: {e}")
            return None
    
    def get_project_by_name(self, name: str, owner_id: int) -> Optional[Project]:
        """Get a project by name and owner"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, name, owner_id, description FROM projects
                    WHERE name = ? AND owner_id = ?
                ''', (name, owner_id))
                
                project_row = cursor.fetchone()
                if project_row:
                    return Project(
                        id=project_row[0], 
                        name=project_row[1], 
                        owner_id=project_row[2],
                        description=project_row[3]
                    )
                return None
        except sqlite3.Error as e:
            print(f"Error getting project by name: {e}")
            return None
    
    def get_user_projects(self, user_id: int) -> Dict[str, List[Project]]:
        """Get all projects owned by or shared with a user"""
        try:
            owned_projects = []
            shared_projects = []
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get owned projects
                cursor.execute('''
                    SELECT id, name, owner_id, description FROM projects
                    WHERE owner_id = ?
                    ORDER BY name
                ''', (user_id,))
                
                for row in cursor.fetchall():
                    owned_projects.append(Project(
                        id=row[0],
                        name=row[1],
                        owner_id=row[2],
                        description=row[3]
                    ))
                
                # Get shared projects
                cursor.execute('''
                    SELECT p.id, p.name, p.owner_id, p.description
                    FROM projects p
                    JOIN project_sharing ps ON p.id = ps.project_id
                    WHERE ps.user_id = ?
                    ORDER BY p.name
                ''', (user_id,))
                
                for row in cursor.fetchall():
                    shared_projects.append(Project(
                        id=row[0],
                        name=row[1],
                        owner_id=row[2],
                        description=row[3]
                    ))
                
                return {
                    'owned': owned_projects,
                    'shared': shared_projects
                }
        except sqlite3.Error as e:
            print(f"Error getting user projects: {e}")
            return {'owned': [], 'shared': []}
    
    def share_project(self, project_id: int, username: str, role: str = 'viewer') -> bool:
        """Share a project with another user"""
        if role not in ('viewer', 'editor'):
            return False
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get user ID from username
                cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
                user_row = cursor.fetchone()
                if not user_row:
                    return False
                
                user_id = user_row[0]
                now = datetime.now().isoformat()
                
                # Check if project exists
                cursor.execute('SELECT id FROM projects WHERE id = ?', (project_id,))
                if not cursor.fetchone():
                    return False
                
                # Add sharing record
                cursor.execute('''
                    INSERT OR REPLACE INTO project_sharing (project_id, user_id, role, shared_at)
                    VALUES (?, ?, ?, ?)
                ''', (project_id, user_id, role, now))
                
                return True
        except sqlite3.Error as e:
            print(f"Error sharing project: {e}")
            return False
    
    def get_project_users(self, project_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """Get all users who have access to a project"""
        try:
            owner = None
            shared_users = []
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get project owner
                cursor.execute('''
                    SELECT u.id, u.username, u.email
                    FROM users u
                    JOIN projects p ON u.id = p.owner_id
                    WHERE p.id = ?
                ''', (project_id,))
                
                owner_row = cursor.fetchone()
                if owner_row:
                    owner = {
                        'id': owner_row[0],
                        'username': owner_row[1],
                        'email': owner_row[2],
                        'role': 'owner'
                    }
                
                # Get users with shared access
                cursor.execute('''
                    SELECT u.id, u.username, u.email, ps.role
                    FROM users u
                    JOIN project_sharing ps ON u.id = ps.user_id
                    WHERE ps.project_id = ?
                    ORDER BY u.username
                ''', (project_id,))
                
                for row in cursor.fetchall():
                    shared_users.append({
                        'id': row[0],
                        'username': row[1],
                        'email': row[2],
                        'role': row[3]
                    })
                
                return {
                    'owner': owner,
                    'shared_users': shared_users
                }
        except sqlite3.Error as e:
            print(f"Error getting project users: {e}")
            return {'owner': None, 'shared_users': []}

    def remove_user_from_project(self, project_id: int, user_id: int) -> bool:
        """Remove a user's access to a project"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM project_sharing
                    WHERE project_id = ? AND user_id = ?
                ''', (project_id, user_id))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error removing user from project: {e}")
            return False

    def delete_project(self, project_id: int) -> bool:
        """Delete a project and all its structures and groups"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete all group memberships for this project
                cursor.execute('''
                    DELETE FROM group_memberships 
                    WHERE project_id = ?
                ''', (project_id,))
                
                # Delete all structure groups for this project
                cursor.execute('''
                    DELETE FROM structure_groups 
                    WHERE project_id = ?
                ''', (project_id,))
                
                # Delete all structures for this project
                cursor.execute('''
                    DELETE FROM structures 
                    WHERE project_id = ?
                ''', (project_id,))
                
                # Delete all project sharing records
                cursor.execute('''
                    DELETE FROM project_sharing 
                    WHERE project_id = ?
                ''', (project_id,))
                
                # Delete the project
                cursor.execute('''
                    DELETE FROM projects 
                    WHERE id = ?
                ''', (project_id,))
                
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting project: {e}")
            return False

    def get_structure(self, structure_id: str, project_id: int) -> Optional[Structure]:
        """Retrieve a structure by its ID and project"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM structures 
                    WHERE structure_id = ? AND project_id = ?
                ''', (structure_id, project_id))
                row = cursor.fetchone()
                if row:
                    return self.row_to_structure(row)
            return None
        except sqlite3.Error as e:
            print(f"Error getting structure: {e}")
            return None

    def get_upstream_structures(self, structure_id: str, project_id: int) -> List[Structure]:
        """
        Get all structures that have the specified structure as their downstream connection
        (i.e., structures that flow into this one).
        
        Args:
            structure_id: The ID of the downstream structure
            project_id: The project ID
            
        Returns:
            List of Structure objects that have their upstream_structure_id set to the given structure_id
        """
        try:
            structures = []
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Find structures where upstream_structure_id equals the given structure_id
                cursor.execute('''
                    SELECT * FROM structures 
                    WHERE upstream_structure_id = ? AND project_id = ?
                    ORDER BY structure_id
                ''', (structure_id, project_id))
                
                for row in cursor.fetchall():
                    structures.append(self.row_to_structure(row))
                    
            return structures
        except sqlite3.Error as e:
            self.logger.error(f"Error getting upstream structures: {e}", exc_info=True)
            return []

    def get_all_structures(self, project_id: int) -> List[Structure]:
        """Retrieve all structures for a project"""
        try:
            structures = []
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM structures 
                    WHERE project_id = ?
                    ORDER BY structure_id
                ''', (project_id,))
                for row in cursor.fetchall():
                    structures.append(self.row_to_structure(row))
            return structures
        except sqlite3.Error as e:
            print(f"Error getting all structures: {e}")
            return []

    def add_structure(self, structure: Structure, project_id: int) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                
                cursor.execute('''
                    INSERT INTO structures (
                        structure_id, structure_type, rim_elevation, invert_out_elevation, 
                        invert_out_angle, vert_drop, upstream_structure_id, pipe_length, 
                        pipe_diameter, pipe_type, frame_type, description, project_id, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    structure.structure_id, structure.structure_type, structure.rim_elevation,
                    structure.invert_out_elevation, structure.invert_out_angle, structure.vert_drop,
                    structure.upstream_structure_id, structure.pipe_length, structure.pipe_diameter,
                    structure.pipe_type, structure.frame_type, structure.description, project_id, now, now
                ))
                return True
        except IntegrityError as e:
            # Handle specific constraint violations
            if "UNIQUE constraint failed" in str(e):
                self.logger.warning(f"Structure ID '{structure.structure_id}' already exists in project {project_id}")
                return False
            elif "FOREIGN KEY constraint failed" in str(e):
                self.logger.error(f"Foreign key constraint violation: {e}, structure: {structure.structure_id}")
                return False
            else:
                self.logger.error(f"Integrity error when adding structure: {e}", exc_info=True)
                return False
        except OperationalError as e:
            # Handle database operational issues (locked DB, timeout, etc.)
            self.logger.error(f"Database operational error: {e}", exc_info=True)
            return False
        except Error as e:
            # Handle any other SQLite errors
            self.logger.error(f"Error adding structure {structure.structure_id}: {e}", exc_info=True)
            return False
        
        self.load_structures()

    def update_structure(self, structure: Structure, project_id: int) -> bool:
        """Update an existing structure in the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                
                cursor.execute('''
                    UPDATE structures SET
                        structure_type = ?,
                        rim_elevation = ?,
                        invert_out_elevation = ?,
                        invert_out_angle = ?,
                        vert_drop = ?,
                        upstream_structure_id = ?,
                        pipe_length = ?,
                        pipe_diameter = ?,
                        pipe_type = ?,
                        frame_type = ?,
                        description = ?,
                        updated_at = ?
                    WHERE structure_id = ? AND project_id = ?
                ''', (
                    structure.structure_type,
                    structure.rim_elevation,
                    structure.invert_out_elevation,
                    structure.invert_out_angle,
                    structure.vert_drop,
                    structure.upstream_structure_id,
                    structure.pipe_length,
                    structure.pipe_diameter,
                    structure.pipe_type,
                    structure.frame_type,
                    structure.description,
                    now,
                    structure.structure_id,
                    project_id
                ))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating structure: {e}")
            return False
        
        self.load_structures()

    def delete_structure(self, structure_id: str, project_id: int) -> bool:
        """Delete a structure from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # First remove any group memberships
                cursor.execute('''
                    DELETE FROM group_memberships 
                    WHERE structure_id = ? AND project_id = ?
                ''', (structure_id, project_id))
                # Then delete the structure
                cursor.execute('''
                    DELETE FROM structures 
                    WHERE structure_id = ? AND project_id = ?
                ''', (structure_id, project_id))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting structure: {e}")
            return False

    # === Modified Group Methods to Include Project ID ===

    def create_group(self, name: str, project_id: int, description: str = "") -> bool:
        """Create a new structure group"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                
                cursor.execute('''
                    INSERT INTO structure_groups (name, description, project_id, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (name, description, project_id, now, now))
                return True
        except sqlite3.IntegrityError:
            return False
        except sqlite3.Error as e:
            print(f"Error creating group: {e}")
            return False

    def safe_date_parse(self, date_value):
        """Safely parse a date value from the database"""
        if not date_value:
            return None
            
        # If it's already a datetime object
        if isinstance(date_value, datetime):
            return date_value
            
        # Try parsing as ISO format
        try:
            return datetime.fromisoformat(str(date_value))
        except ValueError:
            pass
            
        # Try parsing as timestamp (integer)
        try:
            if isinstance(date_value, int) or str(date_value).isdigit():
                return datetime.fromtimestamp(int(date_value))
        except (ValueError, OverflowError):
            pass
            
        # If all else fails
        return None

    def get_all_groups(self, project_id: int) -> List[StructureGroup]:
        """Get all structure groups for a project"""
        try:
            groups = []
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM structure_groups 
                    WHERE project_id = ?
                    ORDER BY name
                ''', (project_id,))
                
                rows = cursor.fetchall()
                
                # Debug: Print row information
                for row in rows:
                    print(f"Row: {row}")
                    print(f"Type of row[3]: {type(row[3])}, Value: {row[3]}")
                    
                    # Try getting the id and name at least
                    group = StructureGroup(
                        id=row[0],
                        name=row[1],
                        description=row[2],
                        created_at=None,
                        updated_at=None
                    )
                    groups.append(group)
                    
                return groups
        except Exception as e:
            self.logger.error(f"Error getting groups: {e}", exc_info=True)
            print(f"Exception in get_all_groups: {e}")
            return []

    def add_structures_to_group(self, group_name: str, structure_ids: List[str], project_id: int) -> bool:
        """Add multiple structures to a group"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Get group ID
                cursor.execute('''
                    SELECT id FROM structure_groups 
                    WHERE name = ? AND project_id = ?
                ''', (group_name, project_id))
                group_row = cursor.fetchone()
                if not group_row:
                    return False
                
                group_id = group_row[0]
                now = datetime.now().isoformat()
                
                # Add structures to group
                for structure_id in structure_ids:
                    cursor.execute('''
                        INSERT OR IGNORE INTO group_memberships 
                        (group_id, structure_id, project_id, added_at)
                        VALUES (?, ?, ?, ?)
                    ''', (group_id, structure_id, project_id, now))
                
                return True
        except sqlite3.Error as e:
            print(f"Error adding structures to group: {e}")
            return False

    def get_group_structures(self, group_name: str, project_id: int) -> List[Structure]:
        """Get all structures in a group"""
        try:
            structures = []
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT s.* FROM structures s
                    JOIN group_memberships gm ON s.structure_id = gm.structure_id AND s.project_id = gm.project_id
                    JOIN structure_groups g ON gm.group_id = g.id AND gm.project_id = g.project_id
                    WHERE g.name = ? AND g.project_id = ?
                    ORDER BY s.structure_id
                ''', (group_name, project_id))
                for row in cursor.fetchall():
                    structures.append(self.row_to_structure(row))
            return structures
        except sqlite3.Error as e:
            print(f"Error getting group structures: {e}")
            return []

    def get_all_pipe_types(self) -> List[str]:
        """Get all pipe types sorted alphabetically"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT name FROM pipe_types
                    ORDER BY name
                ''')
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            self.logger.error(f"Error getting pipe types: {e}", exc_info=True)
            return []

    def add_pipe_type(self, name: str) -> bool:
        """Add a new pipe type"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                cursor.execute('''
                    INSERT INTO pipe_types (name, created_at, updated_at)
                    VALUES (?, ?, ?)
                ''', (name, now, now))
                return True
        except sqlite3.IntegrityError:
            self.logger.warning(f"Pipe type '{name}' already exists")
            return False
        except sqlite3.Error as e:
            self.logger.error(f"Error adding pipe type: {e}", exc_info=True)
            return False

    def delete_pipe_type(self, name: str) -> bool:
        """Delete a pipe type"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM pipe_types WHERE name = ?
                ''', (name,))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting pipe type: {e}", exc_info=True)
            return False

    def row_to_structure(self, row) -> Structure:
        """
        Convert database row to Structure object using a more robust approach.
        
        This method dynamically maps database columns to structure attributes
        based on column position (index) in the result set.
        """
        # Get column names from cursor description if available
        column_names = []
        if hasattr(row, 'cursor') and hasattr(row.cursor, 'description'):
            column_names = [desc[0] for desc in row.cursor.description]
        
        # Create dictionary mapping column names or indices to values
        data = {}
        
        # First, handle the case where row is a tuple (standard sqlite result)
        if isinstance(row, tuple):
            # These are standard columns that should always be present
            # Map by position to ensure backward compatibility
            standard_fields = [
                'id', 'structure_id', 'structure_type', 'rim_elevation', 
                'invert_out_elevation', 'invert_out_angle', 'vert_drop',
                'upstream_structure_id', 'pipe_length', 'pipe_diameter', 'pipe_type'
            ]
            
            # Map all available standard fields
            for i, field in enumerate(standard_fields):
                if i < len(row):
                    data[field] = row[i]
            
            # Check for additional columns that might be present in newer schema versions
            # If we have column names, use them for mapping
            if column_names:
                for i, col_name in enumerate(column_names):
                    if col_name not in standard_fields and i < len(row):
                        data[col_name] = row[i]
            else:
                # If no column names, try to map remaining columns by position
                # Add special handling for known extended fields
                extended_fields = ['frame_type', 'description', 'group_name', 'created_at', 'updated_at']
                offset = len(standard_fields)
                
                for i, field in enumerate(extended_fields):
                    if offset + i < len(row):
                        data[field] = row[offset + i]
        
        # Handle dictionaries (e.g., for Row objects in some SQL libraries)
        elif isinstance(row, dict):
            data = row.copy()
        
        # Create the structure with all available data
        kwargs = {
            'id': data.get('id'),
            'structure_id': data.get('structure_id'),
            'structure_type': data.get('structure_type'),
            'rim_elevation': data.get('rim_elevation'),
            'invert_out_elevation': data.get('invert_out_elevation'),
            'invert_out_angle': data.get('invert_out_angle'),
            'vert_drop': data.get('vert_drop'),
            'upstream_structure_id': data.get('upstream_structure_id'),
            'pipe_length': data.get('pipe_length'),
            'pipe_diameter': data.get('pipe_diameter'),
            'pipe_type': data.get('pipe_type')
        }
        
        # Add optional fields that might be present in newer schema versions
        if 'frame_type' in data:
            kwargs['frame_type'] = data.get('frame_type')
        if 'description' in data:
            # Pass description as a normal parameter now
            kwargs['description'] = data.get('description')
        if 'group_name' in data:
            kwargs['group_name'] = data.get('group_name')
        
        # Handle timestamps
        if 'created_at' in data:
            kwargs['created_at'] = self.safe_date_parse(data.get('created_at'))
        if 'updated_at' in data:
            kwargs['updated_at'] = self.safe_date_parse(data.get('updated_at'))
        
        # Create and return the structure
        structure = Structure(**kwargs)
        return structure

    def delete_group(self, group_name: str, project_id: int) -> bool:
        """Delete a group and all its memberships"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Get group ID
                cursor.execute('''
                    SELECT id FROM structure_groups 
                    WHERE name = ? AND project_id = ?
                ''', (group_name, project_id))
                group_row = cursor.fetchone()
                if not group_row:
                    return False
                
                group_id = group_row[0]
                
                # Delete memberships first
                cursor.execute('''
                    DELETE FROM group_memberships 
                    WHERE group_id = ? AND project_id = ?
                ''', (group_id, project_id))
                # Then delete the group
                cursor.execute('''
                    DELETE FROM structure_groups 
                    WHERE id = ? AND project_id = ?
                ''', (group_id, project_id))
                
                return True
        except sqlite3.Error as e:
            print(f"Error deleting group: {e}")
            return False