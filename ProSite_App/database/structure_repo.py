import sqlite3
from sqlite3 import Error, IntegrityError, OperationalError
from typing import List, Optional, Dict, Tuple, Any
from datetime import datetime
import logging

# Import your data models
from models import Structure, StructureGroup, StructureComponent, ComponentType

class StructureRepository: 
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
    
    def add_structure(self, structure: Structure, project_id: int) -> bool:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    now = datetime.now().isoformat()
                    
                    cursor.execute('''
                        INSERT INTO structures (
                            structure_id, structure_type, rim_elevation, invert_out_elevation,
                            run_designation, invert_out_angle, vert_drop, upstream_structure_id,
                            upstream_run_designation, pipe_length, pipe_diameter, pipe_type,
                            frame_type, description, is_primary_run, project_id, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        structure.structure_id, structure.structure_type, structure.rim_elevation,
                        structure.invert_out_elevation, structure.run_designation, structure.invert_out_angle,
                        structure.vert_drop, structure.upstream_structure_id, structure.upstream_run_designation,
                        structure.pipe_length, structure.pipe_diameter, structure.pipe_type,
                        structure.frame_type, structure.description, structure.is_primary_run,
                        project_id, now, now
                    ))
                    return True
            except IntegrityError as e:
                # Handle specific constraint violations
                if "UNIQUE constraint failed" in str(e):
                    self.logger.warning(f"Structure run '{structure.structure_id}-{structure.run_designation}' already exists in project {project_id}")
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
                        run_designation = ?,
                        invert_out_angle = ?,
                        vert_drop = ?,
                        upstream_structure_id = ?,
                        upstream_run_designation = ?,
                        pipe_length = ?,
                        pipe_diameter = ?,
                        pipe_type = ?,
                        frame_type = ?,
                        description = ?,
                        is_primary_run = ?,
                        updated_at = ?
                    WHERE structure_id = ? AND run_designation = ? AND project_id = ?
                ''', (
                    structure.structure_type,
                    structure.rim_elevation,
                    structure.invert_out_elevation,
                    structure.run_designation,
                    structure.invert_out_angle,
                    structure.vert_drop,
                    structure.upstream_structure_id,
                    structure.upstream_run_designation,
                    structure.pipe_length,
                    structure.pipe_diameter,
                    structure.pipe_type,
                    structure.frame_type,
                    structure.description,
                    structure.is_primary_run,
                    now,
                    structure.structure_id,
                    structure.run_designation,
                    project_id
                ))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            self.logger.error(f"Error updating structure: {e}", exc_info=True)
            return False
        
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
        
    def get_structure(self, structure_id: str, project_id: int, run_designation: str = None) -> Optional[Structure]:
        """Retrieve a structure by its ID, project, and optionally run designation"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if run_designation:
                    cursor.execute('''
                        SELECT * FROM structures 
                        WHERE structure_id = ? AND project_id = ? AND run_designation = ?
                    ''', (structure_id, project_id, run_designation))
                else:
                    # Get the primary run if no run specified
                    cursor.execute('''
                        SELECT * FROM structures 
                        WHERE structure_id = ? AND project_id = ? AND is_primary_run = 1
                        LIMIT 1
                    ''', (structure_id, project_id))
                
                row = cursor.fetchone()
                if row:
                    return self.row_to_structure(row)
                return None
        except sqlite3.Error as e:
            self.logger.error(f"Error getting structure: {e}", exc_info=True)
            return None
        
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
                
                # Format dates properly - Fixed to handle None values correctly
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
                
                self.logger.info(f"Added component {component.component_type_id} to structure {component.structure_id}")
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Error adding structure component: {e}", exc_info=True)
            return False

    def add_structure_run(self, structure: Structure, project_id: int) -> bool:
        """Add a new run to an existing structure or create new structure"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if structure exists
                cursor.execute('''
                    SELECT COUNT(*) FROM structures 
                    WHERE structure_id = ? AND project_id = ?
                ''', (structure.structure_id, project_id))
                
                structure_exists = cursor.fetchone()[0] > 0
                
                # If structure doesn't exist, this becomes the primary run
                if not structure_exists:
                    structure.is_primary_run = True
                    structure.run_designation = structure.run_designation or "A"
                
                # Use the regular add_structure method since it's now updated
                return self.add_structure(structure, project_id)
                
        except sqlite3.Error as e:
            self.logger.error(f"Error adding structure run: {e}", exc_info=True)
            return False

    def rename_structure(self, old_structure_id: str, new_structure_id: str, project_id: int) -> bool:
        """
        Rename a structure and update all references to it.
        This is a complex operation that needs to maintain referential integrity.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if old structure exists
                cursor.execute('''
                    SELECT COUNT(*) FROM structures 
                    WHERE structure_id = ? AND project_id = ?
                ''', (old_structure_id, project_id))
                
                if cursor.fetchone()[0] == 0:
                    self.logger.error(f"Structure {old_structure_id} not found")
                    return False
                
                # Check if new structure ID already exists
                cursor.execute('''
                    SELECT COUNT(*) FROM structures 
                    WHERE structure_id = ? AND project_id = ?
                ''', (new_structure_id, project_id))
                
                if cursor.fetchone()[0] > 0:
                    self.logger.error(f"Structure {new_structure_id} already exists")
                    return False
                
                # Begin transaction for atomic operation
                cursor.execute('BEGIN TRANSACTION')
                
                try:
                    # Update the structure itself
                    cursor.execute('''
                        UPDATE structures 
                        SET structure_id = ?, updated_at = ?
                        WHERE structure_id = ? AND project_id = ?
                    ''', (new_structure_id, datetime.now().isoformat(), old_structure_id, project_id))
                    
                    # Update all references in upstream_structure_id field
                    cursor.execute('''
                        UPDATE structures 
                        SET upstream_structure_id = ?, updated_at = ?
                        WHERE upstream_structure_id = ? AND project_id = ?
                    ''', (new_structure_id, datetime.now().isoformat(), old_structure_id, project_id))
                    
                    # Update group memberships
                    cursor.execute('''
                        UPDATE group_memberships 
                        SET structure_id = ?
                        WHERE structure_id = ? AND project_id = ?
                    ''', (new_structure_id, old_structure_id, project_id))
                    
                    # Update structure components
                    cursor.execute('''
                        UPDATE structure_components 
                        SET structure_id = ?, updated_at = ?
                        WHERE structure_id = ? AND project_id = ?
                    ''', (new_structure_id, datetime.now().isoformat(), old_structure_id, project_id))
                    
                    # Commit the transaction
                    cursor.execute('COMMIT')
                    
                    self.logger.info(f"Successfully renamed structure from {old_structure_id} to {new_structure_id}")
                    return True
                    
                except Exception as e:
                    # Rollback on any error
                    cursor.execute('ROLLBACK')
                    self.logger.error(f"Error during rename transaction: {e}", exc_info=True)
                    return False
                    
        except sqlite3.Error as e:
            self.logger.error(f"Database error renaming structure: {e}", exc_info=True)
            return False

    def get_structure_runs_grouped(self, project_id: int) -> Dict[str, List[Structure]]:
        """Get all structures grouped by structure_id"""
        try:
            structures = self.get_all_structures(project_id)
            grouped = {}
            
            for structure in structures:
                if structure.structure_id not in grouped:
                    grouped[structure.structure_id] = []
                grouped[structure.structure_id].append(structure)
            
            # Sort runs within each structure by run_designation
            for structure_id in grouped:
                grouped[structure_id].sort(key=lambda s: s.run_designation or "A")
            
            return grouped
        except Exception as e:
            self.logger.error(f"Error grouping structure runs: {e}", exc_info=True)
            return {}

    def get_primary_structure(self, structure_id: str, project_id: int) -> Optional[Structure]:
        """Get the primary run for a structure (for main display)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # First try to get the run marked as primary
                cursor.execute('''
                    SELECT * FROM structures 
                    WHERE structure_id = ? AND project_id = ? AND is_primary_run = 1
                    LIMIT 1
                ''', (structure_id, project_id))
                
                row = cursor.fetchone()
                if row:
                    return self.row_to_structure(row)
                
                # If no primary run, get the first run (usually "A")
                cursor.execute('''
                    SELECT * FROM structures 
                    WHERE structure_id = ? AND project_id = ?
                    ORDER BY run_designation
                    LIMIT 1
                ''', (structure_id, project_id))
                
                row = cursor.fetchone()
                if row:
                    return self.row_to_structure(row)
                
                return None
        except sqlite3.Error as e:
            self.logger.error(f"Error getting primary structure: {e}", exc_info=True)
            return None

    def set_primary_run(self, structure_id: str, run_designation: str, project_id: int) -> bool:
        """Set which run should be the primary run for a structure"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # First, unset all primary flags for this structure
                cursor.execute('''
                    UPDATE structures 
                    SET is_primary_run = 0 
                    WHERE structure_id = ? AND project_id = ?
                ''', (structure_id, project_id))
                
                # Then set the specified run as primary
                cursor.execute('''
                    UPDATE structures 
                    SET is_primary_run = 1 
                    WHERE structure_id = ? AND run_designation = ? AND project_id = ?
                ''', (structure_id, run_designation, project_id))
                
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            self.logger.error(f"Error setting primary run: {e}", exc_info=True)
            return False

    def delete_structure_run(self, structure_id: str, run_designation: str, project_id: int) -> bool:
        """Delete a specific run of a structure"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if this is the only run for the structure
                cursor.execute('''
                    SELECT COUNT(*) FROM structures 
                    WHERE structure_id = ? AND project_id = ?
                ''', (structure_id, project_id))
                
                count = cursor.fetchone()[0]
                if count <= 1:
                    # If it's the last run, delete all related records
                    return self.delete_structure(structure_id, project_id)
                
                # Delete the specific run
                cursor.execute('''
                    DELETE FROM structures 
                    WHERE structure_id = ? AND run_designation = ? AND project_id = ?
                ''', (structure_id, run_designation, project_id))
                
                # If we deleted the primary run, make another run primary
                if cursor.rowcount > 0:
                    cursor.execute('''
                        SELECT COUNT(*) FROM structures 
                        WHERE structure_id = ? AND project_id = ? AND is_primary_run = 1
                    ''', (structure_id, project_id))
                    
                    if cursor.fetchone()[0] == 0:
                        # No primary run left, make the first one primary
                        cursor.execute('''
                            UPDATE structures 
                            SET is_primary_run = 1 
                            WHERE structure_id = ? AND project_id = ?
                            ORDER BY run_designation
                            LIMIT 1
                        ''', (structure_id, project_id))
                
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting structure run: {e}", exc_info=True)
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
        
    # ==========================================
    # Helper & Conversion Methods
    # ==========================================

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
    
    def _safe_float_convert(self, value) -> Optional[float]:
        """Safely convert value to float, return None if conversion fails"""
        if value is None or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def _safe_int_convert(self, value) -> Optional[int]:
        """Safely convert value to int, return None if conversion fails"""
        if value is None or value == '':
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
        
    def row_to_structure(self, row) -> Structure:
        """
        Convert database row to Structure object with column mapping
        """
        if not row:
            return None
        
        try:
            # Get actual column information from database
            column_info = self._get_structures_table_columns()
            if not column_info:
                self.logger.error("Could not retrieve table column information")
                return None
            
            # Create a mapping of column names to values
            data = {}
            for i, (column_name, _) in enumerate(column_info):
                if i < len(row):
                    data[column_name] = row[i]
                else:
                    data[column_name] = None
            
            # Create Structure object with explicit mapping and safe defaults
            structure = Structure(
                id=data.get('id'),
                structure_id=data.get('structure_id', ''),
                structure_type=data.get('structure_type', '').strip(),
                rim_elevation=self._safe_float_convert(data.get('rim_elevation')),
                invert_out_elevation=self._safe_float_convert(data.get('invert_out_elevation')),
                run_designation=data.get('run_designation', 'A'),
                invert_out_angle=self._safe_int_convert(data.get('invert_out_angle')),
                vert_drop=self._safe_float_convert(data.get('vert_drop')),
                upstream_structure_id=data.get('upstream_structure_id'),
                upstream_run_designation=data.get('upstream_run_designation'),
                pipe_length=self._safe_float_convert(data.get('pipe_length')),
                pipe_diameter=self._safe_float_convert(data.get('pipe_diameter')),
                pipe_type=data.get('pipe_type'),
                frame_type=data.get('frame_type'),
                description=data.get('description'),
                group_name=data.get('group_name'),
                is_primary_run=bool(data.get('is_primary_run', True)),
                created_at=self.safe_date_parse(data.get('created_at')),
                updated_at=self.safe_date_parse(data.get('updated_at'))
            )
            
            return structure
            
        except Exception as e:
            self.logger.error(f"Error converting row to structure: {e}", exc_info=True)
            self.logger.debug(f"Row data: {row}")
            return None

    # ==========================================
    # Structure Group Methods
    # ==========================================    

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
                
                for row in rows:
                    # row[0]=id, row[1]=name, row[2]=description, row[3]=project_id, row[4]=created_at, row[5]=updated_at
                    group = StructureGroup(
                        id=row[0],
                        name=row[1],
                        description=row[2],
                        created_at=self.safe_date_parse(row[4]),
                        updated_at=self.safe_date_parse(row[5])
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
        
    # ==========================================
    # Enhanced Component Methods
    # ==========================================

    def parse_component_date(self, date_value):
        """Enhanced date parsing specifically for component dates"""
        if not date_value:
            return None
            
        # If it's already a datetime object
        if isinstance(date_value, datetime):
            return date_value
            
        # Try parsing as ISO format first
        try:
            return datetime.fromisoformat(str(date_value))
        except ValueError:
            pass
            
        # Try parsing as MM/DD/YYYY format
        try:
            return datetime.strptime(str(date_value), "%m/%d/%Y")
        except ValueError:
            pass
            
        # Try parsing as YYYY-MM-DD format
        try:
            return datetime.strptime(str(date_value), "%Y-%m-%d")
        except ValueError:
            pass
            
        # Try parsing as timestamp (integer)
        try:
            if isinstance(date_value, int) or str(date_value).isdigit():
                return datetime.fromtimestamp(int(date_value))
        except (ValueError, OverflowError):
            pass
            
        # Log parsing failures for debugging
        self.logger.warning(f"Could not parse component date: {date_value} (type: {type(date_value)})")
        return None
    
    def get_structure_components_with_dates(self, structure_id: str, project_id: int) -> List[StructureComponent]:
        """Get all components for a structure with proper date handling"""
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
                    # Enhanced date parsing
                    order_date = self.parse_component_date(row[4])
                    expected_date = self.parse_component_date(row[5])
                    actual_date = self.parse_component_date(row[6])
                    
                    components.append(StructureComponent(
                        id=row[0],
                        structure_id=row[1],
                        component_type_id=row[2],
                        status=row[3],
                        order_date=order_date,
                        expected_delivery_date=expected_date,
                        actual_delivery_date=actual_date,
                        notes=row[7],
                        created_at=self.safe_date_parse(row[8]),
                        updated_at=self.safe_date_parse(row[9]),
                        component_type_name=row[10],
                        project_id=project_id
                    ))
                return components
        except sqlite3.Error as e:
            self.logger.error(f"Error getting structure components with dates: {e}", exc_info=True)
            return []

    def update_component_status_enhanced(self, component_id: int, status: str, notes: str = None,
                               order_date: datetime = None, expected_delivery_date: datetime = None,
                               actual_delivery_date: datetime = None) -> bool:
        """Update a component's status with all date fields"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                
                # Format dates properly
                order_date_str = order_date.isoformat() if order_date else None
                expected_date_str = expected_delivery_date.isoformat() if expected_delivery_date else None
                delivery_date_str = actual_delivery_date.isoformat() if actual_delivery_date else None
                
                cursor.execute('''
                    UPDATE structure_components SET
                        status = ?,
                        notes = ?,
                        order_date = ?,
                        expected_delivery_date = ?,
                        actual_delivery_date = ?,
                        updated_at = ?
                    WHERE id = ?
                ''', (status, notes, order_date_str, expected_date_str, delivery_date_str, now, component_id))
                    
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            self.logger.error(f"Error updating component status enhanced: {e}", exc_info=True)
            return False