import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from models import Structure, StructureGroup

import hashlib

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
        self.db_path = db_path
        self.initialize_database()

    def initialize_database(self):
        """Create tables if they don't exist"""
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
                    CREATE TABLE IF NOT EXISTS projects_SHARING (
                        proeject_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        role TEXT NOT NULL,
                        shared_at TIMESTAMP NOT NULL,
                        FOREIGN KEY (project_id_) REFERENCES projects (id),
                        FOREIGN KEY (user_id) REFERENCES users (id),
                        PRIMARY KEY (project_id, user_id)
                    )
                ''')            

                # Create structures table with optional fields and project_id
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
                        project_id TEXT,
                        added_at TIMESTAMP NOT NULL,
                        FOREIGN KEY (group_id) REFERENCES structure_groups (id),
                        FOREIGN KEY (structure_id, project_id) REFERENCES structures (structure_id, project_id),
                        FOREIGN KEY (project_id) REFERENCES projects (id),
                        PRIMARY KEY (group_id, structure_id, project_id)
                    )
                ''')
                
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            raise

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





    # STOPPING HERE WILL CONTINUE LATER





    def row_to_structure(self, row) -> Structure:
        """Convert a database row to a Structure object"""
        try:
            return Structure(
                id=row[0],
                structure_id=row[1],
                structure_type=row[2],
                rim_elevation=row[3],
                invert_out_elevation=row[4],
                invert_out_angle=row[5],
                vert_drop=row[6],
                upstream_structure_id=row[7],
                pipe_length=row[8],
                pipe_diameter=row[9],
                pipe_type=row[10],
                group_name=row[11],
                created_at=datetime.fromisoformat(row[12]) if row[12] else None,
                updated_at=datetime.fromisoformat(row[13]) if row[13] else None
            )
        except Exception as e:
            print(f"Error converting row to structure: {e}")
            raise

    def add_structure(self, structure: Structure) -> bool:
        """Add a new structure to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                cursor.execute('''
                    INSERT INTO structures (
                        structure_id, structure_type, rim_elevation,
                        invert_out_elevation, invert_out_angle, vert_drop,
                        upstream_structure_id, pipe_length, pipe_diameter,
                        pipe_type, group_name, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    structure.structure_id,
                    structure.structure_type,
                    structure.rim_elevation,
                    structure.invert_out_elevation,
                    structure.invert_out_angle,
                    structure.vert_drop,
                    structure.upstream_structure_id,
                    structure.pipe_length,
                    structure.pipe_diameter,
                    structure.pipe_type,
                    structure.group_name,
                    now,
                    now
                ))
                return True
        except sqlite3.IntegrityError:
            return False
        except sqlite3.Error as e:
            print(f"Error adding structure: {e}")
            return False

    def update_structure(self, structure: Structure) -> bool:
        """Update an existing structure"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
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
                        group_name = ?,
                        updated_at = ?
                    WHERE structure_id = ?
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
                    structure.group_name,
                    datetime.now().isoformat(),
                    structure.structure_id
                ))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating structure: {e}")
            return False

    def get_structure(self, structure_id: str) -> Optional[Structure]:
        """Retrieve a structure by its ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM structures WHERE structure_id = ?', (structure_id,))
                row = cursor.fetchone()
                if row:
                    return self.row_to_structure(row)
            return None
        except sqlite3.Error as e:
            print(f"Error getting structure: {e}")
            return None

    def get_all_structures(self) -> List[Structure]:
        """Retrieve all structures"""
        try:
            structures = []
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM structures ORDER BY structure_id')
                for row in cursor.fetchall():
                    structures.append(self.row_to_structure(row))
            return structures
        except sqlite3.Error as e:
            print(f"Error getting all structures: {e}")
            return []

    def delete_structure(self, structure_id: str) -> bool:
        """Delete a structure from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # First remove any group memberships
                cursor.execute('DELETE FROM group_memberships WHERE structure_id = ?', (structure_id,))
                # Then delete the structure
                cursor.execute('DELETE FROM structures WHERE structure_id = ?', (structure_id,))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting structure: {e}")
            return False

    def create_group(self, name: str, description: str = "") -> bool:
        """Create a new structure group"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                cursor.execute('''
                    INSERT INTO structure_groups (name, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                ''', (name, description, now, now))
                return True
        except sqlite3.IntegrityError:
            return False
        except sqlite3.Error as e:
            print(f"Error creating group: {e}")
            return False

    def get_all_groups(self) -> List[StructureGroup]:
        """Get all structure groups"""
        try:
            groups = []
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM structure_groups ORDER BY name')
                for row in cursor.fetchall():
                    groups.append(StructureGroup(
                        id=row[0],
                        name=row[1],
                        description=row[2],
                        created_at=datetime.fromisoformat(row[3]) if row[3] else None,
                        updated_at=datetime.fromisoformat(row[4]) if row[4] else None
                    ))
            return groups
        except sqlite3.Error as e:
            print(f"Error getting groups: {e}")
            return []

    def add_structures_to_group(self, group_name: str, structure_ids: List[str]) -> bool:
        """Add multiple structures to a group"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Get group ID
                cursor.execute('SELECT id FROM structure_groups WHERE name = ?', (group_name,))
                group_row = cursor.fetchone()
                if not group_row:
                    return False
                
                group_id = group_row[0]
                now = datetime.now().isoformat()
                
                # Add structures to group
                for structure_id in structure_ids:
                    cursor.execute('''
                        INSERT OR IGNORE INTO group_memberships (group_id, structure_id, added_at)
                        VALUES (?, ?, ?)
                    ''', (group_id, structure_id, now))
                
                return True
        except sqlite3.Error as e:
            print(f"Error adding structures to group: {e}")
            return False

    def remove_structures_from_group(self, group_name: str, structure_ids: List[str]) -> bool:
        """Remove structures from a group"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM structure_groups WHERE name = ?', (group_name,))
                group_row = cursor.fetchone()
                if not group_row:
                    return False
                
                group_id = group_row[0]
                cursor.execute('''
                    DELETE FROM group_memberships 
                    WHERE group_id = ? AND structure_id IN ({})
                '''.format(','.join(['?'] * len(structure_ids))), 
                    [group_id] + structure_ids)
                
                return True
        except sqlite3.Error as e:
            print(f"Error removing structures from group: {e}")
            return False

    def get_group_structures(self, group_name: str) -> List[Structure]:
        """Get all structures in a group"""
        try:
            structures = []
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT s.* FROM structures s
                    JOIN group_memberships gm ON s.structure_id = gm.structure_id
                    JOIN structure_groups g ON gm.group_id = g.id
                    WHERE g.name = ?
                    ORDER BY s.structure_id
                ''', (group_name,))
                for row in cursor.fetchall():
                    structures.append(self.row_to_structure(row))
            return structures
        except sqlite3.Error as e:
            print(f"Error getting group structures: {e}")
            return []

    def delete_group(self, group_name: str) -> bool:
        """Delete a group and all its memberships"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Get group ID
                cursor.execute('SELECT id FROM structure_groups WHERE name = ?', (group_name,))
                group_row = cursor.fetchone()
                if not group_row:
                    return False
                
                group_id = group_row[0]
                
                # Delete memberships first
                cursor.execute('DELETE FROM group_memberships WHERE group_id = ?', (group_id,))
                # Then delete the group
                cursor.execute('DELETE FROM structure_groups WHERE id = ?', (group_id,))
                
                return True
        except sqlite3.Error as e:
            print(f"Error deleting group: {e}")
            return False