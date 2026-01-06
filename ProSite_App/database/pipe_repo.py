import sqlite3
from sqlite3 import Error, IntegrityError
from datetime import datetime
from typing import List, Dict, Optional, Any
import logging

# You need Structure because create_pipe_order iterates over structure objects
from models import Structure

class PipeRepository:
    def create_pipe_order(self, order_number: str, supplier: str, expected_delivery_date: datetime = None,
                        notes: str = None, pipe_groups: dict = None, project_id: int = None) -> bool:
            """Create a new pipe order with associated pipe items"""
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    now = datetime.now().isoformat()
                    
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

