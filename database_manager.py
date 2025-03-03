import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple
from models import Structure, StructureGroup

class DatabaseManager:
    def __init__(self, db_path: str = "structures.db"):
        self.db_path = db_path
        self.initialize_database()

    def initialize_database(self):
        """Create tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create structures table with optional fields
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS structures (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        structure_id TEXT UNIQUE NOT NULL,
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
                        FOREIGN KEY (upstream_structure_id) REFERENCES structures (structure_id)
                    )
                ''')
                
                # Create structure groups table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS structure_groups (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        description TEXT,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL
                    )
                ''')
                
                # Create group memberships table for many-to-many relationship
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS group_memberships (
                        group_id INTEGER,
                        structure_id TEXT,
                        added_at TIMESTAMP NOT NULL,
                        FOREIGN KEY (group_id) REFERENCES structure_groups (id),
                        FOREIGN KEY (structure_id) REFERENCES structures (structure_id),
                        PRIMARY KEY (group_id, structure_id)
                    )
                ''')
                
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            raise

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