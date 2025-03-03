import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.simpledialog as simpledialog
from database_manager import DatabaseManager
from typing import List, Dict, Optional
import hashlib

class StructureManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Structure Management System")
        self.db = DatabaseManager()
        self.current_user = None
        self.current_project = None
        
        # Structure type options
        self.structure_types = ['CB', 'JB', 'DI', 'HW', 'UGDS']
        
        # Start with login screen
        self.show_login_screen()

    def show_login_screen(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        login_frame = ttk.Frame(self.root, padding="20")
        login_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(login_frame, text="Username:").grid(row=0, column=0, pady=5)
        self.username_entry = ttk.Entry(login_frame)
        self.username_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, pady=5)
        self.password_entry = ttk.Entry(login_frame, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)
        
        ttk.Button(login_frame, text="Login", command=self.login).grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(login_frame, text="Register", command=self.show_register_screen).grid(row=3, column=0, columnspan=2)

    def show_register_screen(self):
        register_window = tk.Toplevel(self.root)
        register_window.title("Register New User")
        register_window.geometry("300x200")
        
        ttk.Label(register_window, text="Username:").pack(pady=5)
        username_entry = ttk.Entry(register_window)
        username_entry.pack(pady=5)
        
        ttk.Label(register_window, text="Email:").pack(pady=5)
        email_entry = ttk.Entry(register_window)
        email_entry.pack(pady=5)
        
        ttk.Label(register_window, text="Password:").pack(pady=5)
        password_entry = ttk.Entry(register_window, show="*")
        password_entry.pack(pady=5)
        
        def register():
            try:
                user = self.db.create_user(
                    username_entry.get(),
                    email_entry.get(),
                    password_entry.get()
                )
                messagebox.showinfo("Success", "Registration successful! Please login.")
                register_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(register_window, text="Register", command=register).pack(pady=10)

    def login(self):
        user = self.db.authenticate_user(
            self.username_entry.get(),
            self.password_entry.get()
        )
        
        if user:
            self.current_user = user
            self.show_project_selection()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def show_project_selection(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        projects_frame = ttk.Frame(self.root, padding="20")
        projects_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Get user's projects
        projects = self.db.get_user_projects(self.current_user.id)
        
        ttk.Label(projects_frame, text="Your Projects", font=('Arial', 14, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Create project list
        project_frame = ttk.Frame(projects_frame)
        project_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.project_listbox = tk.Listbox(project_frame, height=10, width=40)
        scrollbar = ttk.Scrollbar(project_frame, orient="vertical", command=self.project_listbox.yview)
        self.project_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.project_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Populate project list
        for project in projects['owned']:
            self.project_listbox.insert(tk.END, f"{project.name} (Owner)")
        for project in projects['shared']:
            self.project_listbox.insert(tk.END, f"{project.name} (Shared)")
        
        # Buttons
        ttk.Button(projects_frame, text="Open Project", command=self.open_project).grid(row=2, column=0, pady=10, padx=5)
        ttk.Button(projects_frame, text="New Project", command=self.create_new_project).grid(row=2, column=1, pady=10, padx=5)
        ttk.Button(projects_frame, text="Share Project", command=self.share_project).grid(row=3, column=0, pady=5, padx=5)
        ttk.Button(projects_frame, text="Logout", command=self.show_login_screen).grid(row=3, column=1, pady=5, padx=5)

    def create_new_project(self):
        name = simpledialog.askstring("New Project", "Enter project name:")
        if name:
            description = simpledialog.askstring("New Project", "Enter project description (optional):")
            project = self.db.create_project(name, self.current_user.id, description or "")
            self.show_project_selection()

    def share_project(self):
        selection = self.project_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a project to share")
            return
        
        project_name = self.project_listbox.get(selection[0]).split(" (")[0]
        username = simpledialog.askstring("Share Project", "Enter username to share with:")
        if username:
            role = simpledialog.askstring("Share Project", "Enter role (viewer/editor):",
                                        initialvalue="viewer")
            # Implement sharing logic here
            messagebox.showinfo("Success", f"Project shared with {username}")

    def open_project(self):
        selection = self.project_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a project")
            return
        
        project_name = self.project_listbox.get(selection[0]).split(" (")[0]
        self.current_project = project_name  # You'll need to get the actual project object
        self.setup_main_interface()

    def setup_main_interface(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, expand=True, fill='both')
        
        # Structures tab
        self.structures_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.structures_frame, text='Structures')
        
        # Project info at top
        project_info = ttk.Frame(self.structures_frame)
        project_info.pack(fill='x', padx=5, pady=5)
        ttk.Label(project_info, text=f"Project: {self.current_project}").pack(side='left')
        ttk.Button(project_info, text="Change Project", command=self.show_project_selection).pack(side='right')
        
        # Split into left and right panes
        paned_window = ttk.PanedWindow(self.structures_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left side - Structure list
        list_frame = ttk.Frame(paned_window)
        paned_window.add(list_frame, weight=1)
        
        # Structure listbox with scrollbar
        self.structure_listbox = tk.Listbox(list_frame, selectmode='extended')
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.structure_listbox.yview)
        self.structure_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.structure_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Right side - Structure details
        details_frame = ttk.Frame(paned_window)
        paned_window.add(details_frame, weight=2)
        
        # Structure details entry fields
        labels = ['Structure ID:', 'Structure Type:', 'Rim Elevation: ', 'Invert Out Elevation: ', 'Frame Type:', 
                  'Drop (VF):', 'Upstream Structure:', 'Pipe Length:', 'Pipe Diameter:', 'Pipe Type:']
        self.entries: Dict[str, ttk.Entry] = {}
        
        for i, label in enumerate(labels):
            ttk.Label(details_frame, text=label).grid(row=i, column=0, padx=5, pady=2, sticky='e')
            
            if label == 'Structure Type:':
                self.entries[label] = ttk.Combobox(details_frame, values=self.structure_types)
            else:
                self.entries[label] = ttk.Entry(details_frame)
            self.entries[label].grid(row=i, column=1, padx=5, pady=2, sticky='ew')
        
        # Invert frame
        invert_frame = ttk.LabelFrame(details_frame, text='Inverts')
        invert_frame.grid(row=len(labels), column=0, columnspan=2, pady=10, sticky='ew')
        
        self.invert_entries = []
        self.add_invert_entry(invert_frame)
        
        ttk.Button(invert_frame, text='Add Invert', command=lambda: self.add_invert_entry(invert_frame)).pack(pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(details_frame)
        button_frame.grid(row=len(labels)+1, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text='Add Structure', command=self.add_structure).pack(side='left', padx=5)
        ttk.Button(button_frame, text='Update Structure', command=self.update_structure).pack(side='left', padx=5)
        ttk.Button(button_frame, text='Create Group', command=self.create_group).pack(side='left', padx=5)
        ttk.Button(button_frame, text='Generate Report', command=self.generate_report).pack(side='left', padx=5)
        
        # Load structures for current project
        self.load_structures()

    def add_invert_entry(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill='x', padx=5, pady=2)
        
        angle_entry = ttk.Entry(frame, width=10)
        angle_entry.insert(0, "Angle")
        angle_entry.pack(side='left', padx=2)
        
        elevation_entry = ttk.Entry(frame, width=10)
        elevation_entry.insert(0, "Elevation")
        elevation_entry.pack(side='left', padx=2)
        
        remove_btn = ttk.Button(frame, text="X", width=2, 
                              command=lambda: frame.destroy() and self.invert_entries.remove((angle_entry, elevation_entry)))
        remove_btn.pack(side='left', padx=2)
        
        self.invert_entries.append((angle_entry, elevation_entry))

    # Implement other methods (add_structure, update_structure, create_group, generate_report)
    # Make sure to include project_id in all database calls

if __name__ == "__main__":
    root = tk.Tk()
    app = StructureManagementApp(root)
    root.mainloop()