import sqlite3
from sqlite3 import Error, IntegrityError, OperationalError
from datetime import datetime
from typing import List, Dict, Optional, Any
from structure_repo import Structure
import logging

# Import your data models
from models import Project

class ProjectRepository:
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
        
