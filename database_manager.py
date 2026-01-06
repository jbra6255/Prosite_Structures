import models
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
        Convert database row to Structure object with robust column mapping
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

    def _debug_table_structure(self):
        """Debug method to print current table structure - can be removed in production"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(structures)")
                columns_info = cursor.fetchall()
                
                self.logger.debug("Current structures table schema:")
                for i, col in enumerate(columns_info):
                    self.logger.debug(f"  {i}: {col[1]} ({col[2]}) - NotNull: {col[3]}, Default: {col[4]}, PK: {col[5]}")
                    
                # Also check if we can get a sample row
                cursor.execute("SELECT * FROM structures LIMIT 1")
                sample_row = cursor.fetchone()
                if sample_row:
                    self.logger.debug(f"Sample row length: {len(sample_row)}")
                    self.logger.debug(f"Expected columns: {len(columns_info)}")
                    
        except sqlite3.Error as e:
            self.logger.error(f"Error debugging table structure: {e}")
            
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
    
    def create_pipe_order(self, order_number: str, supplier: str, expected_delivery_date: datetime = None,
                     notes: str = None, pipe_groups: dict = None, project_id: int = None) -> bool:
        """Create a new pipe order with associated pipe items"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                
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
                
                # Format expected delivery date
                expected_date_str = expected_delivery_date.isoformat() if expected_delivery_date else None
                
                # Insert pipe order
                cursor.execute('''
                    INSERT INTO pipe_orders (
                        order_number, supplier, project_id, status, order_date,
                        expected_delivery_date, notes, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    order_number, supplier, project_id, 'pending', now,
                    expected_date_str, notes, now, now
                ))
                
                order_id = cursor.lastrowid
                
                # Insert pipe order items if provided
                if pipe_groups:
                    for key, group_data in pipe_groups.items():
                        for structure in group_data['structures']:
                            cursor.execute('''
                                INSERT INTO pipe_order_items (
                                    order_id, structure_id, pipe_type, diameter, length,
                                    status, created_at, updated_at
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                order_id, structure.structure_id, group_data['pipe_type'],
                                group_data['diameter'], structure.pipe_length,
                                'pending', now, now
                            ))
                
                self.logger.info(f"Created pipe order {order_number} with {len(pipe_groups) if pipe_groups else 0} pipe groups")
                return True
                
        except sqlite3.Error as e:
            self.logger.error(f"Error creating pipe order: {e}", exc_info=True)
            return False
        
    def get_pipe_orders(self, project_id: int) -> List[Dict[str, Any]]:
        """Get all pipe orders for a project"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if tables exist first
                cursor.execute('''
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='pipe_orders'
                ''')
                
                if not cursor.fetchone():
                    return []
                
                cursor.execute('''
                    SELECT po.*, 
                        COUNT(poi.id) as item_count,
                        SUM(poi.length) as total_length,
                        GROUP_CONCAT(DISTINCT poi.pipe_type) as pipe_types
                    FROM pipe_orders po
                    LEFT JOIN pipe_order_items poi ON po.id = poi.order_id
                    WHERE po.project_id = ?
                    GROUP BY po.id
                    ORDER BY po.created_at DESC
                ''', (project_id,))
                
                orders = []
                for row in cursor.fetchall():
                    orders.append({
                        'id': row[0],
                        'order_number': row[1],
                        'supplier': row[2],
                        'project_id': row[3],
                        'status': row[4],
                        'order_date': row[5],
                        'expected_delivery_date': row[6],
                        'actual_delivery_date': row[7],
                        'notes': row[8],
                        'created_at': row[9],
                        'updated_at': row[10],
                        'item_count': row[11] or 0,
                        'total_length': row[12] or 0,
                        'pipe_types': row[13] or '',
                        'pipe_type': (row[13] or '').split(',')[0] if row[13] else '',  # First pipe type for display
                        'diameter': self._get_primary_diameter_for_order(row[0])
                    })
                
                return orders
        except sqlite3.Error as e:
            self.logger.error(f"Error getting pipe orders: {e}", exc_info=True)
            return []
        
    def _get_primary_diameter_for_order(self, order_id: int) -> str:
        """Get the primary diameter for an order (most common diameter)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT diameter, COUNT(*) as count
                    FROM pipe_order_items
                    WHERE order_id = ?
                    GROUP BY diameter
                    ORDER BY count DESC
                    LIMIT 1
                ''', (order_id,))
                
                result = cursor.fetchone()
                if result and result[0]:
                    return f"{int(result[0])}\""
                return "Mixed"
        except sqlite3.Error:
            return "Unknown"

    def get_pipe_order_items(self, order_id: int) -> List[Dict[str, Any]]:
        """Get all items for a specific pipe order"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT poi.*, s.structure_type
                    FROM pipe_order_items poi
                    LEFT JOIN structures s ON poi.structure_id = s.structure_id
                    WHERE poi.order_id = ?
                    ORDER BY poi.structure_id
                ''', (order_id,))
                
                items = []
                for row in cursor.fetchall():
                    items.append({
                        'id': row[0],
                        'order_id': row[1],
                        'structure_id': row[2],
                        'pipe_type': row[3],
                        'diameter': row[4],
                        'length': row[5],
                        'delivered_length': row[6],
                        'status': row[7],
                        'notes': row[8],
                        'created_at': row[9],
                        'updated_at': row[10],
                        'structure_type': row[11]
                    })
                
                return items
        except sqlite3.Error as e:
            self.logger.error(f"Error getting pipe order items: {e}", exc_info=True)
            return []

    def update_pipe_order_status(self, order_id: int, status: str, delivery_date: datetime = None, notes: str = None) -> bool:
        """Update the status of a pipe order"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                
                # Format delivery date
                delivery_date_str = delivery_date.isoformat() if delivery_date else None
                
                if delivery_date_str:
                    cursor.execute('''
                        UPDATE pipe_orders SET
                            status = ?,
                            actual_delivery_date = ?,
                            notes = ?,
                            updated_at = ?
                        WHERE id = ?
                    ''', (status, delivery_date_str, notes, now, order_id))
                else:
                    cursor.execute('''
                        UPDATE pipe_orders SET
                            status = ?,
                            notes = ?,
                            updated_at = ?
                        WHERE id = ?
                    ''', (status, notes, now, order_id))
                
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            self.logger.error(f"Error updating pipe order status: {e}", exc_info=True)
            return False

    def update_pipe_item_delivery(self, item_id: int, delivered_length: float, status: str = "delivered", notes: str = None) -> bool:
        """Update delivery status for a specific pipe item"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                
                cursor.execute('''
                    UPDATE pipe_order_items SET
                        delivered_length = ?,
                        status = ?,
                        notes = ?,
                        updated_at = ?
                    WHERE id = ?
                ''', (delivered_length, status, notes, now, item_id))
                
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            self.logger.error(f"Error updating pipe item delivery: {e}", exc_info=True)
            return False
        
    def delete_pipe_order(self, order_id: int) -> bool:
        """Delete a pipe order and all its associated items"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Begin transaction for atomic operation
                cursor.execute('BEGIN TRANSACTION')
                
                try:
                    # First delete all order items
                    cursor.execute('''
                        DELETE FROM pipe_order_items 
                        WHERE order_id = ?
                    ''', (order_id,))
                    
                    items_deleted = cursor.rowcount
                    
                    # Then delete the order itself
                    cursor.execute('''
                        DELETE FROM pipe_orders 
                        WHERE id = ?
                    ''', (order_id,))
                    
                    order_deleted = cursor.rowcount
                    
                    # Commit the transaction
                    cursor.execute('COMMIT')
                    
                    self.logger.info(f"Deleted pipe order {order_id} with {items_deleted} items")
                    return order_deleted > 0
                    
                except Exception as e:
                    # Rollback on any error
                    cursor.execute('ROLLBACK')
                    self.logger.error(f"Error during delete transaction: {e}", exc_info=True)
                    return False
                    
        except sqlite3.Error as e:
            self.logger.error(f"Database error deleting pipe order: {e}", exc_info=True)
            return False

    def get_pipe_order_details(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a pipe order for confirmation dialogs"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get order details
                cursor.execute('''
                    SELECT po.*, 
                        COUNT(poi.id) as item_count,
                        SUM(poi.length) as total_length
                    FROM pipe_orders po
                    LEFT JOIN pipe_order_items poi ON po.id = poi.order_id
                    WHERE po.id = ?
                    GROUP BY po.id
                ''', (order_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                return {
                    'id': row[0],
                    'order_number': row[1],
                    'supplier': row[2],
                    'project_id': row[3],
                    'status': row[4],
                    'order_date': row[5],
                    'expected_delivery_date': row[6],
                    'actual_delivery_date': row[7],
                    'notes': row[8],
                    'created_at': row[9],
                    'updated_at': row[10],
                    'item_count': row[11] or 0,
                    'total_length': row[12] or 0
                }
                
        except sqlite3.Error as e:
            self.logger.error(f"Error getting pipe order details: {e}", exc_info=True)
            return None
        
    def update_pipe_order_enhanced(self, order_id: int, status: str, supplier: str = None,
                                order_date: datetime = None, expected_delivery_date: datetime = None,
                                actual_delivery_date: datetime = None, notes: str = None) -> bool:
        """Enhanced pipe order update with all fields"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                
                # Format dates properly
                order_date_str = order_date.isoformat() if order_date else None
                expected_date_str = expected_delivery_date.isoformat() if expected_delivery_date else None
                delivery_date_str = actual_delivery_date.isoformat() if actual_delivery_date else None
                
                # Always update notes field, even when None (to clear notes)
                cursor.execute('''
                    UPDATE pipe_orders SET
                        status = ?,
                        supplier = ?,
                        order_date = ?,
                        expected_delivery_date = ?,
                        actual_delivery_date = ?,
                        notes = ?,
                        updated_at = ?
                    WHERE id = ?
                ''', (status, supplier, order_date_str, expected_date_str, delivery_date_str, notes, now, order_id))
                
                success = cursor.rowcount > 0
                if success:
                    self.logger.info(f"Enhanced update for pipe order {order_id}")
                return success
                
        except sqlite3.Error as e:
            self.logger.error(f"Error updating pipe order enhanced: {e}", exc_info=True)
            return False

    def get_pipe_item_details(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific pipe item"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT poi.*, s.structure_type, po.order_number
                    FROM pipe_order_items poi
                    LEFT JOIN structures s ON poi.structure_id = s.structure_id
                    LEFT JOIN pipe_orders po ON poi.order_id = po.id
                    WHERE poi.id = ?
                ''', (item_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'order_id': row[1],
                        'structure_id': row[2],
                        'pipe_type': row[3],
                        'diameter': row[4],
                        'length': row[5],
                        'delivered_length': row[6],
                        'status': row[7],
                        'notes': row[8],
                        'created_at': row[9],
                        'updated_at': row[10],
                        'structure_type': row[11],
                        'order_number': row[12]
                    }
                return None
                
        except sqlite3.Error as e:
            self.logger.error(f"Error getting pipe item details: {e}", exc_info=True)
            return None

    def update_pipe_item_delivery_enhanced(self, item_id: int, delivered_length: float = None, 
                                    status: str = None, notes: str = None,
                                    delivery_date: datetime = None, update_notes: bool = False) -> bool:
        """Enhanced pipe item delivery update with optional delivery date tracking
        
        Args:
            item_id: ID of the pipe item to update
            delivered_length: New delivered length (optional)
            status: New status (optional)
            notes: New notes - can be None to clear notes, empty string, or actual notes (optional)
            delivery_date: Delivery date (optional)
            update_notes: Force update of notes field even if notes is None (useful for clearing notes)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                
                # Build dynamic query based on provided parameters
                update_fields = []
                update_values = []
                
                if delivered_length is not None:
                    update_fields.append("delivered_length = ?")
                    update_values.append(delivered_length)
                
                if status is not None:
                    update_fields.append("status = ?")
                    update_values.append(status)
                
                # Fix: Always update notes if explicitly requested or if notes is provided
                if notes is not None or update_notes:
                    update_fields.append("notes = ?")
                    update_values.append(notes)  # This will be None for clearing notes
                
                # Add delivery date if provided
                if delivery_date is not None:
                    update_fields.append("delivery_date = ?")
                    update_values.append(delivery_date.isoformat())
                
                # Always update the timestamp
                update_fields.append("updated_at = ?")
                update_values.append(now)
                
                # Add the item_id for the WHERE clause
                update_values.append(item_id)
                
                if not update_fields:
                    return False  # Nothing to update
                
                query = f"UPDATE pipe_order_items SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(query, update_values)
                
                success = cursor.rowcount > 0
                if success:
                    self.logger.info(f"Enhanced delivery update for pipe item {item_id}")
                return success
                
        except sqlite3.Error as e:
            self.logger.error(f"Error updating pipe item delivery enhanced: {e}", exc_info=True)
            return False

    def get_pipe_delivery_summary(self, project_id: int) -> Dict[str, Any]:
        """Get comprehensive delivery summary for pipe tracking dashboard"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if tables exist
                cursor.execute('''
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name IN ('pipe_orders', 'pipe_order_items')
                ''')
                
                existing_tables = [row[0] for row in cursor.fetchall()]
                if len(existing_tables) < 2:
                    return {
                        'total_orders': 0,
                        'total_length': 0,
                        'delivered_length': 0,
                        'pending_length': 0,
                        'completion_percentage': 0,
                        'orders_by_status': {}
                    }
                
                # Get order counts by status
                cursor.execute('''
                    SELECT status, COUNT(*) as count
                    FROM pipe_orders
                    WHERE project_id = ?
                    GROUP BY status
                ''', (project_id,))
                
                orders_by_status = {}
                for row in cursor.fetchall():
                    orders_by_status[row[0]] = row[1]
                
                # Get total pipe lengths
                cursor.execute('''
                    SELECT 
                        COUNT(DISTINCT po.id) as total_orders,
                        COALESCE(SUM(poi.length), 0) as total_length,
                        COALESCE(SUM(poi.delivered_length), 0) as delivered_length
                    FROM pipe_orders po
                    LEFT JOIN pipe_order_items poi ON po.id = poi.order_id
                    WHERE po.project_id = ?
                ''', (project_id,))
                
                row = cursor.fetchone()
                total_orders = row[0] if row else 0
                total_length = row[1] if row else 0
                delivered_length = row[2] if row else 0
                
                pending_length = total_length - delivered_length
                completion_percentage = (delivered_length / total_length * 100) if total_length > 0 else 0
                
                return {
                    'total_orders': total_orders,
                    'total_length': total_length,
                    'delivered_length': delivered_length,
                    'pending_length': pending_length,
                    'completion_percentage': completion_percentage,
                    'orders_by_status': orders_by_status
                }
                
        except sqlite3.Error as e:
            self.logger.error(f"Error getting pipe delivery summary: {e}", exc_info=True)
            return {
                'total_orders': 0,
                'total_length': 0,
                'delivered_length': 0,
                'pending_length': 0,
                'completion_percentage': 0,
                'orders_by_status': {}
            }