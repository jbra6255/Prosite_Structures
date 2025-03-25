import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
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

    # === Modified Structure Methods to Include Project ID ===
    
    def add_structure(self):
        """Add a new structure to the database based on form fields"""
        try:
            # Get the current project ID
            project = self.db.get_project_by_name(self.current_project, self.current_user.id)
            if not project:
                messagebox.showerror("Error", "Could not find current project")
                return
                
            # Get structure data from form fields
            structure_id = self.entries['Structure ID:'].get()
            structure_type = self.entries['Structure Type:'].get()
            rim_elevation = float(self.entries['Rim Elevation: '].get())
            invert_out_elevation = float(self.entries['Invert Out Elevation: '].get())
            
            # Optional fields
            upstream_structure_id = self.entries['Upstream Structure:'].get() or None
            
            try:
                pipe_length = float(self.entries['Pipe Length:'].get()) if self.entries['Pipe Length:'].get() else None
                pipe_diameter = float(self.entries['Pipe Diameter:'].get()) if self.entries['Pipe Diameter:'].get() else None
                vert_drop = float(self.entries['Drop (VF):'].get()) if self.entries['Drop (VF):'].get() else None
            except ValueError:
                messagebox.showerror("Error", "Invalid numeric input in one or more fields")
                return
                
            pipe_type = self.entries['Pipe Type:'].get() or None
            frame_type = self.entries['Frame Type:'].get() or None
            
            # Validation
            if not structure_id or not structure_type or not rim_elevation or not invert_out_elevation:
                messagebox.showerror("Error", "Structure ID, Type, Rim Elevation and Invert Out Elevation are required")
                return
                
            # Create structure object
            new_structure = Structure(
                structure_id=structure_id,
                structure_type=structure_type,
                rim_elevation=rim_elevation,
                invert_out_elevation=invert_out_elevation,
                invert_out_angle=None,  # You could add this to your form if needed
                vert_drop=vert_drop,
                upstream_structure_id=upstream_structure_id,
                pipe_length=pipe_length,
                pipe_diameter=pipe_diameter,
                pipe_type=pipe_type
            )
            
            # Add to database
            success = self.db.add_structure(new_structure, project.id)
            
            if success:
                messagebox.showinfo("Success", f"Structure {structure_id} added successfully")
                # Clear form fields
                self.clear_structure_form()
                # Refresh structure list
                self.load_structures()
            else:
                messagebox.showerror("Error", f"Failed to add structure. ID may already exist.")
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def clear_structure_form(self):
        """Clear all structure form fields"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        
        # Clear invert entries
        for angle_entry, elevation_entry in self.invert_entries:
            angle_entry.delete(0, tk.END)
            elevation_entry.delete(0, tk.END)

    def show_structure_details(self, event):
        """Show details for selected structure"""
        selection = self.structure_listbox.curselection()
        if not selection:
            return
            
        # Get structure ID from listbox
        structure_id = self.structure_listbox.get(selection[0]).split(" (")[0]
        
        # Get project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            return
            
        # Get structure from database
        structure = self.db.get_structure(structure_id, project.id)
        if not structure:
            return
            
        # Clear form first
        self.clear_structure_form()
        
        # Fill in form with structure details
        self.entries['Structure ID:'].insert(0, structure.structure_id)
        self.entries['Structure Type:'].set(structure.structure_type)
        self.entries['Rim Elevation: '].insert(0, str(structure.rim_elevation))
        self.entries['Invert Out Elevation: '].insert(0, str(structure.invert_out_elevation))
        
        if structure.vert_drop:
            self.entries['Drop (VF):'].insert(0, str(structure.vert_drop))
        if structure.upstream_structure_id:
            self.entries['Upstream Structure:'].insert(0, structure.upstream_structure_id)
        if structure.pipe_length:
            self.entries['Pipe Length:'].insert(0, str(structure.pipe_length))
        if structure.pipe_diameter:
            self.entries['Pipe Diameter:'].insert(0, str(structure.pipe_diameter))
        if structure.pipe_type:
            self.entries['Pipe Type:'].insert(0, structure.pipe_type)

def load_structures(self):
    """Load structures from database into listbox"""
    # Clear existing items
    self.structure_listbox.delete(0, tk.END)
    
    # Get current project ID
    project = self.db.get_project_by_name(self.current_project, self.current_user.id)
    if not project:
        return
        
    # Get structures for this project
    structures = self.db.get_all_structures(project.id)
    
    # Add to listbox
    for structure in structures:
        self.structure_listbox.insert(tk.END, f"{structure.structure_id} ({structure.structure_type})")
        
    # Add selection handler to show details when clicked
    self.structure_listbox.bind('<<ListboxSelect>>', self.show_structure_details)



    def update_structure(self):
        """Update an existing structure with form data"""
        try:
            # Get the current project ID
            project = self.db.get_project_by_name(self.current_project, self.current_user.id)
            if not project:
                messagebox.showerror("Error", "Could not find current project")
                return
                
            # Get structure data from form fields
            structure_id = self.entries['Structure ID:'].get()
            
            # Check if structure exists
            existing_structure = self.db.get_structure(structure_id, project.id)
            if not existing_structure:
                messagebox.showerror("Error", f"Structure {structure_id} not found")
                return
                
            # Get updated fields
            structure_type = self.entries['Structure Type:'].get()
            
            try:
                rim_elevation = float(self.entries['Rim Elevation: '].get())
                invert_out_elevation = float(self.entries['Invert Out Elevation: '].get())
                pipe_length = float(self.entries['Pipe Length:'].get()) if self.entries['Pipe Length:'].get() else None
                pipe_diameter = float(self.entries['Pipe Diameter:'].get()) if self.entries['Pipe Diameter:'].get() else None
                vert_drop = float(self.entries['Drop (VF):'].get()) if self.entries['Drop (VF):'].get() else None
            except ValueError:
                messagebox.showerror("Error", "Invalid numeric input in one or more fields")
                return
                
            upstream_structure_id = self.entries['Upstream Structure:'].get() or None
            pipe_type = self.entries['Pipe Type:'].get() or None
            
            # Update structure object
            updated_structure = Structure(
                structure_id=structure_id,
                structure_type=structure_type,
                rim_elevation=rim_elevation,
                invert_out_elevation=invert_out_elevation,
                invert_out_angle=existing_structure.invert_out_angle,  # Preserve existing value
                vert_drop=vert_drop,
                upstream_structure_id=upstream_structure_id,
                pipe_length=pipe_length,
                pipe_diameter=pipe_diameter,
                pipe_type=pipe_type,
                group_name=existing_structure.group_name  # Preserve existing group
            )
            
            # Update in database
            success = self.db.update_structure(updated_structure, project.id)
            
            if success:
                messagebox.showinfo("Success", f"Structure {structure_id} updated successfully")
                # Refresh structure list
                self.load_structures()
            else:
                messagebox.showerror("Error", "Failed to update structure")
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

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
    
    def create_group(self):
        """Create a new structure group and add selected structures to it"""
        # Get selected structures from listbox
        selected_indices = self.structure_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select structures to add to the group")
            return
            
        # Get structure IDs
        structure_ids = []
        for index in selected_indices:
            structure_id = self.structure_listbox.get(index).split(" (")[0]
            structure_ids.append(structure_id)
        
        # Get group name from user
        group_name = simpledialog.askstring("New Group", "Enter group name:")
        if not group_name:
            return
            
        # Get project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            messagebox.showerror("Error", "Could not find current project")
            return
            
        # Create group
        success = self.db.create_group(group_name, project.id)
        if not success:
            messagebox.showerror("Error", "Failed to create group. Group name may already exist.")
            return
            
        # Add structures to group
        success = self.db.add_structures_to_group(group_name, structure_ids, project.id)
        if success:
            messagebox.showinfo("Success", f"Created group '{group_name}' with {len(structure_ids)} structures")
        else:
            messagebox.showerror("Error", "Failed to add structures to group")

    def generate_report(self):
        """Generate a summary report of the current project structures"""
        # Get project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            messagebox.showerror("Error", "Could not find current project")
            return
            
        # Get all structures for this project
        structures = self.db.get_all_structures(project.id)
        if not structures:
            messagebox.showinfo("Report", "No structures found in this project")
            return
            
        # Create report window
        report_window = tk.Toplevel(self.root)
        report_window.title(f"Report: {self.current_project}")
        report_window.geometry("700x500")
        
        # Report text widget with scrollbar
        report_frame = ttk.Frame(report_window)
        report_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        report_text = tk.Text(report_frame, wrap='word')
        scrollbar = ttk.Scrollbar(report_frame, orient='vertical', command=report_text.yview)
        report_text.configure(yscrollcommand=scrollbar.set)
        
        report_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Generate report content
        report_text.insert(tk.END, f"Project: {self.current_project}\n")
        report_text.insert(tk.END, f"Total Structures: {len(structures)}\n\n")
        
        # Structure type summary
        structure_types = {}
        for structure in structures:
            structure_types[structure.structure_type] = structure_types.get(structure.structure_type, 0) + 1
        
        report_text.insert(tk.END, "Structure Types:\n")
        for type_name, count in structure_types.items():
            report_text.insert(tk.END, f"  {type_name}: {count}\n")
        
        report_text.insert(tk.END, "\nStructure Details:\n")
        for structure in structures:
            report_text.insert(tk.END, f"\n{structure.structure_id} ({structure.structure_type})\n")
            report_text.insert(tk.END, f"  Rim Elevation: {structure.rim_elevation}\n")
            report_text.insert(tk.END, f"  Invert Out: {structure.invert_out_elevation}\n")
            report_text.insert(tk.END, f"  Total Drop: {structure.total_drop}\n")
            if structure.pipe_length:
                report_text.insert(tk.END, f"  Pipe Length: {structure.pipe_length}\n")
            if structure.pipe_diameter:
                report_text.insert(tk.END, f"  Pipe Diameter: {structure.pipe_diameter}\n")
        
        # Make text readonly
        report_text.configure(state='disabled')
        
        # Add buttons
        button_frame = ttk.Frame(report_window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Close", command=report_window.destroy).pack(side='left', padx=5)
        
        # Save report button could be added here

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