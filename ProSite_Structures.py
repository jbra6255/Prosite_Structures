import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import ttkbootstrap.dialogs as dialogs
from database_manager import DatabaseManager
from typing import List, Dict, Optional
from models import Structure, StructureGroup
from logger import AppLogger
import hashlib

class StructureManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Structure Management System")
        # Set window size and center it
        self.root.geometry("900x600")
        self.root.minsize(800, 500)

        # Initialize logger
        from logger import AppLogger
        self.logger = AppLogger().logger
        self.logger.info("Application starting")

        # Initialize database
        self.db = DatabaseManager()
        self.current_user = None
        self.current_project = None
        
        # Structure type options
        self.structure_types = ['CB', 'JB', 'DI', 'HW', 'UGDS']
        
        # Start with login screen
        self.show_login_screen()

    def show_login_screen(self):
        """Display the login screen with ttkbootstrap styling"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create a card frame for login with padding
        login_frame = ttk.Frame(self.root, padding="30")
        login_frame.pack(expand=True)
        
        # App title with brand styling
        title_frame = ttk.Frame(login_frame)
        title_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame, 
            text="Structure Management", 
            font=("Helvetica", 24, "bold"),
            bootstyle="primary"
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame, 
            text="Log in to manage your projects",
            font=("Helvetica", 12)
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Username field with improved styling
        username_frame = ttk.Frame(login_frame)
        username_frame.pack(fill="x", pady=10)
        
        ttk.Label(username_frame, text="Username:", font=("Helvetica", 10)).pack(anchor="w")
        self.username_entry = ttk.Entry(username_frame, width=30)
        self.username_entry.pack(fill="x", pady=(5, 0))
        
        # Password field with improved styling
        password_frame = ttk.Frame(login_frame)
        password_frame.pack(fill="x", pady=10)
        
        ttk.Label(password_frame, text="Password:", font=("Helvetica", 10)).pack(anchor="w")
        self.password_entry = ttk.Entry(password_frame, width=30, show="•")  # Nicer bullet for password masking
        self.password_entry.pack(fill="x", pady=(5, 0))
        
        # Button frame with cleaner layout
        button_frame = ttk.Frame(login_frame)
        button_frame.pack(fill="x", pady=(20, 10))
        
        # Primary login button
        login_btn = ttk.Button(
            button_frame, 
            text="Log In", 
            bootstyle="primary",  # Bootstrap-style primary button
            width=15,
            command=self.login
        )
        login_btn.pack(pady=5)
        
        # Outline style for secondary actions
        register_btn = ttk.Button(
            button_frame, 
            text="Create Account", 
            bootstyle="secondary-outline",  # Outline style for secondary action
            width=15,
            command=self.show_register_screen
        )
        register_btn.pack(pady=5)

        # Bind Enter key to login method for both entry fields
        self.username_entry.bind('<Return>', self.login)
        self.password_entry.bind('<Return>', self.login)

        # Set focus on username entry
        self.username_entry.focus()

    def show_register_screen(self):
        register_window = ttk.Toplevel(self.root)
        register_window.title("Create Your Account")
        register_window.geometry("400x400")
        
        # Add padding around the entire content
        main_frame = ttk.Frame(register_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title with primary color
        ttk.Label(
            main_frame, 
            text="Create Your Account", 
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        ).pack(pady=(0, 20))

        # Username field
        ttk.Label(main_frame, text="Username", font=("Helvetica", 10)).pack(anchor="w", pady=(10, 5))
        username_entry = ttk.Entry(main_frame)
        username_entry.pack(fill="x")
        
        # Email field  
        ttk.Label(main_frame, text="Email", font=("Helvetica", 10)).pack(anchor="w", pady=(10, 5))
        email_entry = ttk.Entry(main_frame)
        email_entry.pack(fill="x")
        
        # Password field
        ttk.Label(main_frame, text="Password", font=("Helvetica", 10)).pack(anchor="w", pady=(10, 5))
        password_entry = ttk.Entry(main_frame, show="•")
        password_entry.pack(fill="x")
                
        # Helper text
        ttk.Label(
            main_frame, 
            text="Password must be at least 8 characters",
            bootstyle="secondary",
            font=("Helvetica", 9)
        ).pack(anchor="w", pady=(5, 15))

        def register():
            try:
                # Basic validation
                if len(username_entry.get()) < 3:
                    Messagebox.show_error("Username must be at least 3 characters", "Validation Error")
                    return
                    
                if len(password_entry.get()) < 8:
                    Messagebox.show_error("Password must be at least 8 characters", "Validation Error")
                    return
                
                user = self.db.create_user(
                    username_entry.get(),
                    email_entry.get(),
                    password_entry.get()
                )
                if user:
                    Messagebox.show_info("Registration successful! Please log in with your new account.", "Account Created")
                    register_window.destroy()
                else:
                    Messagebox.show_error("Registration failed. Username or email may already exist.", "Registration Error")
            except Exception as e:
                Messagebox.show_error(str(e), "Error")
        
        # Register button with primary style
        ttk.Button(
            main_frame, 
            text="Create Account", 
            bootstyle="primary",
            command=register
        ).pack(pady=15, fill="x")
        
        # Cancel button with outline style
        ttk.Button(
            main_frame, 
            text="Cancel", 
            bootstyle="secondary-outline",
            command=register_window.destroy
        ).pack(fill="x")

    def login(self, event=None):
        """Log in a user with proper error logging"""
        try:
            user = self.db.authenticate_user(
                self.username_entry.get(),
                self.password_entry.get()
            )
            
            if user:
                self.current_user = user
                self.logger.info(f"User logged in: {user.username}")
                self.show_project_selection()
            else:
                self.logger.warning(f"Failed login attempt for username: {self.username_entry.get()}")
                Messagebox.show_error("Invalid username or password", "Login Failed")
        except Exception as e:
            self.logger.error(f"Login error: {e}", exc_info=True)
            Messagebox.show_error("An unexpected error occurred during login", "System Error")

    def show_project_selection(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Header with welcome message
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(
            header_frame, 
            text=f"Welcome, {self.current_user.username}",
            font=("Helvetica", 18, "bold")
        ).pack(side="left")
        
        ttk.Button(
            header_frame, 
            text="Log Out", 
            bootstyle="danger-outline",
            command=self.show_login_screen
        ).pack(side="right")
        
        # Projects section
        ttk.Label(
            main_frame, 
            text="Your Projects", 
            font=("Helvetica", 14, "bold"),
            bootstyle="primary"
        ).pack(anchor="w", pady=(0, 10))
        
        # Get user's projects
        projects = self.db.get_user_projects(self.current_user.id)
        
        # Project list with scrollbar in a card-like frame
        project_container = ttk.Frame(main_frame, bootstyle="default")
        project_container.pack(fill="both", expand=True, pady=10)
        
        # Create project list with headers
        columns = ("Project", "Role", "Description")
        
        project_tree = ttk.Treeview(
            project_container,
            columns=columns,
            show="headings",
            height=10,
            bootstyle="primary"
        )
        
        # Define column headings
        for col in columns:
            project_tree.heading(col, text=col)
            project_tree.column(col, width=150)
        
        project_tree.column("Description", width=300)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(project_container, orient="vertical", command=project_tree.yview)
        project_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack the treeview and scrollbar
        project_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Populate project list
        for project in projects['owned']:
            project_tree.insert("", "end", values=(project.name, "Owner", project.description or ""))
            
        for project in projects['shared']:
            project_tree.insert("", "end", values=(project.name, "Shared", project.description or ""))
        
        # Action buttons in a separate frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=15)
        
        # Button to open selected project (primary action)
        ttk.Button(
            button_frame, 
            text="Open Project", 
            bootstyle="primary",
            command=lambda: self.open_selected_project(project_tree)
        ).pack(side="left", padx=5)
        
        # Button to create new project
        ttk.Button(
            button_frame, 
            text="New Project", 
            bootstyle="success",
            command=self.create_new_project
        ).pack(side="left", padx=5)
        
        # Button to share selected project
        ttk.Button(
            button_frame, 
            text="Share Project", 
            bootstyle="info",
            command=lambda: self.share_selected_project(project_tree)
        ).pack(side="left", padx=5)
        
        # Status bar at bottom
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill="x", pady=(20, 0))
        
        ttk.Label(
            status_frame, 
            text=f"Connected as: {self.current_user.email}",
            bootstyle="secondary"
        ).pack(side="left")
        
        ttk.Label(
            status_frame, 
            text="Structure Management System v1.0",
            bootstyle="secondary"
        ).pack(side="right")

    def open_selected_project(self, tree):
        selection = tree.selection()
        if not selection:
            Messagebox.show_warning("Please select a project", "No Selection")
            return
        
        project_name = tree.item(selection[0], "values")[0]
        self.current_project = project_name
        self.setup_main_interface()

    def share_selected_project(self, tree):
        selection = tree.selection()
        if not selection:
            Messagebox.show_warning("Please select a project to share", "No Selection")
            return
        
        project_name = tree.item(selection[0], "values")[0]
        username = dialogs.dialogs.Querybox.get_string(
            "Enter username to share with:", 
            "Share Project"
        )
        
        if not username:
            return
            
        role = dialogs.dialogs.Querybox.get_string(
            "Enter role (viewer/editor):", 
            "Share Project",
            initialvalue="viewer"
        )
        
        # Implement sharing logic here
        Messagebox.show_info(f"Project shared with {username}", "Success")

    def create_new_project(self):
        name = dialogs.dialogs.Querybox.get_string("Enter project name:", "New Project")
        if name:
            description = dialogs.dialogs.Querybox.get_string("Enter project description (optional):", "New Project")
            project = self.db.create_project(name, self.current_user.id, description or "")
            self.show_project_selection()

    def setup_main_interface(self):
        """Setup the main interface with adjustable divider and properly aligned inputs"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create a modern layout with top navbar
        navbar = ttk.Frame(self.root, bootstyle="primary")
        navbar.pack(fill="x")
        
        # Project title on left
        ttk.Label(
            navbar, 
            text=f"{self.current_project}",
            font=("Helvetica", 14, "bold"),
            foreground="white",
            bootstyle="inverse-primary"
            # background="#007bff"  # Primary color background
        ).pack(side="left", padx=15, pady=10)
        
        # Navigation buttons on right
        ttk.Button(
            navbar, 
            text="Project List",
            bootstyle="primary-outline-toolbutton",
            command=self.show_project_selection
        ).pack(side="right", padx=5, pady=5)
        
        ttk.Button(
            navbar, 
            text="Log Out",
            bootstyle="primary-outline-toolbutton",
            command=self.show_login_screen
        ).pack(side="right", padx=5, pady=5)
        
        # Create main container that will fill available space
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure container to expand properly
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(0, weight=1)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.grid(row=0, column=0, sticky="nsew")
        
        # Structures tab
        self.structures_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.structures_frame, text='Structures')
        
        # Configure structures frame for proper expansion
        self.structures_frame.columnconfigure(0, weight=1)
        self.structures_frame.rowconfigure(0, weight=1)
        
        # Create PanedWindow with proper configuration
        paned_window = ttk.PanedWindow(self.structures_frame, orient="horizontal")
        paned_window.grid(row=0, column=0, sticky="nsew")
        
        # Left side - Structure list frame
        list_frame = ttk.Labelframe(paned_window, text="Structure List")
        
        # Configure list frame for proper expansion
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Right side - Details frame
        details_frame = ttk.Labelframe(paned_window, text="Structure Details")
        
        # Configure details frame for proper expansion
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(0, weight=1)
        
        # Add both frames to paned window
        paned_window.add(list_frame, weight=1)
        paned_window.add(details_frame, weight=2)
        
        # Left side - Structure list with treeview
        treeview_frame = ttk.Frame(list_frame)
        treeview_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure treeview frame
        treeview_frame.columnconfigure(0, weight=1)
        treeview_frame.rowconfigure(0, weight=1)

        # Structure treeview
        columns = ("ID", "Type", "Status")
        self.structure_tree = ttk.Treeview(
            treeview_frame, 
            columns=columns,
            show="headings", 
            selectmode="extended"
        )
        
        # Define column headings
        for col in columns:
            self.structure_tree.heading(col, text=col)
            self.structure_tree.column(col, width=80, anchor="center")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(treeview_frame, orient="vertical", command=self.structure_tree.yview)
        self.structure_tree.configure(yscrollcommand=scrollbar.set)
        
        # Place treeview and scrollbar
        self.structure_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Button frame below the treeview
        button_frame = ttk.Frame(list_frame)
        button_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        
        # Action buttons
        ttk.Button(
            button_frame, 
            text="Add", 
            bootstyle="success-outline",
            command=self.add_structure
        ).pack(side="left", padx=2)
        
        ttk.Button(
            button_frame, 
            text="Delete", 
            bootstyle="danger-outline",
            command=self.delete_selected_structure
        ).pack(side="left", padx=2)
        
        ttk.Button(
            button_frame, 
            text="Group", 
            bootstyle="info-outline",
            command=self.create_group
        ).pack(side="left", padx=2)
        
        # Right side - Form with scrolling capability

        # Create a canvas with scrollbar for the form
        canvas = tk.Canvas(details_frame, highlightthickness=0)
        form_scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=canvas.yview)
        
        # Place canvas and scrollbar
        canvas.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        form_scrollbar.grid(row=0, column=1, sticky="ns", pady=10)
        
        # Configure canvas
        canvas.configure(yscrollcommand=form_scrollbar.set)
        
        # Create a frame inside the canvas to hold the form elements
        form_frame = ttk.Frame(canvas)
        
        # Configure form frame columns to align labels and inputs
        form_frame.columnconfigure(0, weight=0)  # Labels column - fixed width
        form_frame.columnconfigure(1, weight=1)  # Inputs column - expands
        
        # Add all form fields with proper alignment
        row = 0
        labels = ['Structure ID:', 'Structure Type:', 'Rim Elevation: ', 'Invert Out Elevation: ', 
                'Frame Type:', 'Drop (VF):', 'Upstream Structure:', 'Pipe Length:', 
                'Pipe Diameter:', 'Pipe Type:']
        
        self.entries: Dict[str, ttk.Entry] = {}
        
        for label in labels:
            # Label in the first column - right aligned
            ttk.Label(form_frame, text=label).grid(
                row=row, 
                column=0, 
                sticky="e",  # Right align the label
                padx=(5, 10),
                pady=8
            )
            
            # Entry or combobox in the second column - expands to fill space
            if label == 'Structure Type:':
                self.entries[label] = ttk.Combobox(form_frame, values=self.structure_types)
            else:
                self.entries[label] = ttk.Entry(form_frame)
            
            # Make input field fill the available width
            self.entries[label].grid(
                row=row, 
                column=1, 
                sticky="ew",  # Make input expand horizontally
                padx=5, 
                pady=8
            )
            row += 1
        
        # Separator
        ttk.Separator(form_frame).grid(row=row, column=0, columnspan=2, sticky="ew", pady=15)
        row += 1
        
        # Add separator before action buttons
        ttk.Separator(form_frame).grid(row=row, column=0, columnspan=2, sticky="ew", pady=15)
        row += 1

        # Action buttons with modern styling
        action_frame = ttk.Frame(form_frame)
        action_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=10)
        
        ttk.Button(
            action_frame, 
            text='Save', 
            bootstyle="success",
            command=self.update_structure
        ).pack(side="left", padx=5)
        
        ttk.Button(
            action_frame, 
            text='Clear Form', 
            bootstyle="warning",
            command=self.clear_structure_form
        ).pack(side="left", padx=5)
        
        ttk.Button(
            action_frame, 
            text='Generate Report', 
            bootstyle="info",
            command=self.generate_report
        ).pack(side="right", padx=5)
        
        # Create window in canvas for the form frame
        canvas_window = canvas.create_window((0, 0), window=form_frame, anchor="nw")
        
        # Update the canvas scroll region when the form frame size changes
        def update_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=canvas.winfo_width())
        
        form_frame.bind("<Configure>", update_scroll_region)
        
        # Make sure the canvas window width fills the canvas
        def adjust_canvas_window(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", adjust_canvas_window)

        # Define the mousewheel functions
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"  # Prevents event from propagating

        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
            canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")
        
        # Bind the mousewheel functions to details_frame
        details_frame.bind("<Enter>", _bind_mousewheel)
        details_frame.bind("<Leave>", _unbind_mousewheel)
        
        # Reports tab
        reports_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(reports_frame, text='Reports')
        
        # Bind selection event to show details
        self.structure_tree.bind('<<TreeviewSelect>>', self.show_structure_details)
        
        # Load structures for current project
        self.load_structures()

        # Set initial position of the paned window divider
        self.root.update_idletasks()
        paned_window.sashpos(0, 300)

    def add_structure(self):
        """Add a new structure to the database based on form fields"""
        try:
            # Get the current project ID
            project = self.db.get_project_by_name(self.current_project, self.current_user.id)
            if not project:
                Messagebox.show_error("Could not find current project", "Project Error")
                return
                    
            # Get structure data from form fields
            structure_id = self.entries['Structure ID:'].get()
            structure_type = self.entries['Structure Type:'].get()
            
            # Validate required fields
            if not structure_id or not structure_type:
                Messagebox.show_error(
                    "Structure ID and Type are required fields",
                    "Validation Error"
                )
                return
            
            # Get numeric fields with validation
            try:
                rim_elevation = float(self.entries['Rim Elevation: '].get())
                invert_out_elevation = float(self.entries['Invert Out Elevation: '].get())
                
                # Optional numeric fields
                pipe_length = float(self.entries['Pipe Length:'].get()) if self.entries['Pipe Length:'].get() else None
                pipe_diameter = float(self.entries['Pipe Diameter:'].get()) if self.entries['Pipe Diameter:'].get() else None
                vert_drop = float(self.entries['Drop (VF):'].get()) if self.entries['Drop (VF):'].get() else None
            except ValueError:
                Messagebox.show_error(
                    "Invalid numeric input in one or more fields. Please check all elevation, length, and diameter values.",
                    "Input Error"
                )
                return
                
            # Get other optional fields
            upstream_structure_id = self.entries['Upstream Structure:'].get() or None
            pipe_type = self.entries['Pipe Type:'].get() or None
            frame_type = self.entries['Frame Type:'].get() or None
            
            # Additional validation
            if not rim_elevation or not invert_out_elevation:
                Messagebox.show_error(
                    "Rim Elevation and Invert Out Elevation are required",
                    "Validation Error"
                )
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
                pipe_type=pipe_type,
                frame_type=frame_type
            )
            
            # Add to database
            success = self.db.add_structure(new_structure, project.id)
            
            if success:
                # Success message with ttkbootstrap styling
                Messagebox.show_info(
                    f"Structure {structure_id} added successfully", 
                    "Success"
                )
                
                # Clear form fields
                self.clear_structure_form()
                
                # Refresh structure list - assuming you're using a treeview now instead of listbox
                self.load_structures()
                
                # Add structure to the treeview
                # self.structure_tree.insert(
                #     "", 
                #     "end", 
                #     values=(structure_id, structure_type, "Active")
                # )
            else:
                # Error message with ttkbootstrap styling
                Messagebox.show_error(
                    f"Failed to add structure. ID '{structure_id}' may already exist in this project.",
                    "Database Error"
                )
                    
        except Exception as e:
            # Exception handler with detailed error message
            Messagebox.show_error(
                f"An error occurred while adding the structure:\n\n{str(e)}",
                "System Error"
            )

    def delete_selected_structure(self):
        """Delete the selected structure"""
        # Get selection from treeview
        selection = self.structure_tree.selection()
        if not selection:
            Messagebox.show_warning("Please select a structure to delete", "No Selection")
            return
            
        # Get structure ID from treeview
        structure_id = self.structure_tree.item(selection[0], "values")[0]
        
        # Confirm deletion with ttkbootstrap's Messagebox
        confirm = Messagebox.yesno(
            f"Are you sure you want to delete structure {structure_id}?", 
            "Confirm Deletion"
        )
        
        if not confirm:
            return
        
        # Get project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            Messagebox.show_error("Could not find current project", "Project Error")
            return
            
        # Delete the structure
        success = self.db.delete_structure(structure_id, project.id)
        
        if success:
            Messagebox.show_info(f"Structure {structure_id} deleted successfully", "Success")
            # Remove from treeview
            self.structure_tree.delete(selection[0])
        else:
            Messagebox.show_error(f"Failed to delete structure {structure_id}", "Error")

    def clear_structure_form(self):
        """Clear all structure form fields"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def show_structure_details(self, event):
        """Show details for selected structure in treeview"""
        # Get selected item
        selection = self.structure_tree.selection()
        if not selection:
            return
            
        # Get structure ID from treeview (first column)
        structure_id = self.structure_tree.item(selection[0], "values")[0]
        
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
        if structure.frame_type:
            self.entries['Frame Type:'].insert(0, structure.frame_type)

    def load_structures(self):
        """Load structures from database into treeview"""
        # Clear existing items in the treeview
        for item in self.structure_tree.get_children():
            self.structure_tree.delete(item)
        
        # Get current project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            return
            
        # Get structures for this project
        structures = self.db.get_all_structures(project.id)
        
        # Add to treeview with improved styling
        for structure in structures:
            # Determine status based on structure properties
            status = "Active"
            
            # Add to treeview with ID, Type, and Status
            self.structure_tree.insert(
                "", 
                "end", 
                values=(
                    structure.structure_id, 
                    structure.structure_type, 
                    status
                )
            )

    def update_structure(self):
        """Update an existing structure with form data"""
        try:
            # Get the current project ID
            project = self.db.get_project_by_name(self.current_project, self.current_user.id)
            if not project:
                Messagebox.show_error("Could not find current project", "Project Error")
                return
                
            # Get structure data from form fields
            structure_id = self.entries['Structure ID:'].get()
            
            # Check if structure exists
            existing_structure = self.db.get_structure(structure_id, project.id)
            if not existing_structure:
                Messagebox.show_error(f"Structure {structure_id} not found", "Not Found")
                return
                
            # Get updated fields
            structure_type = self.entries['Structure Type:'].get()
            
            # Validate required fields
            if not structure_id or not structure_type:
                Messagebox.show_error(
                    "Structure ID and Type are required fields",
                    "Validation Error"
                )
                return
            
            # Get numeric fields with validation
            try:
                rim_elevation = float(self.entries['Rim Elevation: '].get())
                invert_out_elevation = float(self.entries['Invert Out Elevation: '].get())
                pipe_length = float(self.entries['Pipe Length:'].get()) if self.entries['Pipe Length:'].get() else None
                pipe_diameter = float(self.entries['Pipe Diameter:'].get()) if self.entries['Pipe Diameter:'].get() else None
                vert_drop = float(self.entries['Drop (VF):'].get()) if self.entries['Drop (VF):'].get() else None
            except ValueError:
                Messagebox.show_error(
                    "Invalid numeric input in one or more fields. Please check all elevation, length, and diameter values.",
                    "Input Error"
                )
                return
                
            # Get other optional fields
            upstream_structure_id = self.entries['Upstream Structure:'].get() or None
            pipe_type = self.entries['Pipe Type:'].get() or None
            frame_type = self.entries['Frame Type:'].get() or None
            
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
                Messagebox.show_info(f"Structure {structure_id} updated successfully", "Success")
                
                # Update in treeview
                for item in self.structure_tree.get_children():
                    if self.structure_tree.item(item, "values")[0] == structure_id:
                        self.structure_tree.item(item, values=(structure_id, structure_type, "Active"))
                        break
                        
                # Refresh structure list
                self.load_structures()
            else:
                Messagebox.show_error("Failed to update structure", "Database Error")
                
        except Exception as e:
            Messagebox.show_error(f"An error occurred: {str(e)}", "System Error")

    def create_group(self):
        """Create a new structure group and add selected structures to it"""
        # Get selected structures from treeview
        selected_items = self.structure_tree.selection()
        if not selected_items:
            Messagebox.show_warning("Please select structures to add to the group", "No Selection")
            return
            
        # Get structure IDs
        structure_ids = []
        for item in selected_items:
            structure_id = self.structure_tree.item(item, "values")[0]
            structure_ids.append(structure_id)
        
        # Get group name from user with ttkbootstrap dialog
        group_name = dialogs.dialogs.Querybox.get_string(
            "Enter group name:", 
            "New Group"
        )
        
        if not group_name:
            return
            
        # Get project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            Messagebox.show_error("Could not find current project", "Project Error")
            return
            
        # Create group
        success = self.db.create_group(group_name, project.id)
        if not success:
            Messagebox.show_error(
                "Failed to create group. Group name may already exist.", 
                "Database Error"
            )
            return
            
        # Add structures to group
        success = self.db.add_structures_to_group(group_name, structure_ids, project.id)
        if success:
            Messagebox.show_info(
                f"Created group '{group_name}' with {len(structure_ids)} structures",
                "Success"
            )
            
            # Visual feedback - update status in treeview
            for item in selected_items:
                current_values = self.structure_tree.item(item, "values")
                self.structure_tree.item(
                    item, 
                    values=(current_values[0], current_values[1], f"In Group: {group_name}")
                )
        else:
            Messagebox.show_error("Failed to add structures to group", "Database Error")

    def generate_report(self):
        """Generate a summary report of the current project structures"""
        # Get project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            Messagebox.show_error("Could not find current project", "Project Error")
            return
            
        # Get all structures for this project
        structures = self.db.get_all_structures(project.id)
        if not structures:
            Messagebox.show_info("No structures found in this project", "Empty Report")
            return
            
        # Create report window with ttkbootstrap styling
        report_window = ttk.Toplevel(self.root)
        report_window.title(f"Report: {self.current_project}")
        report_window.geometry("800x600")
        
        # Main container with padding
        main_frame = ttk.Frame(report_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Report header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(
            header_frame, 
            text=f"Project Report: {self.current_project}",
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        ).pack(side="left")
        
        # Report date
        from datetime import datetime
        ttk.Label(
            header_frame, 
            text=f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            bootstyle="secondary"
        ).pack(side="right")
        
        # Content frame
        content_frame = ttk.Labelframe(main_frame, text="Structure Summary", padding=10)
        content_frame.pack(fill="both", expand=True)
        
        # Report text widget with scrollbar
        report_text = tk.Text(content_frame, wrap='word', font=("Consolas", 11))
        scrollbar = ttk.Scrollbar(content_frame, orient='vertical', command=report_text.yview)
        report_text.configure(yscrollcommand=scrollbar.set)
        
        report_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Generate report content with better formatting
        report_text.insert(tk.END, f"Total Structures: {len(structures)}\n", "heading")
        report_text.insert(tk.END, f"Project Owner: {self.current_user.username}\n\n", "heading")
        
        # Add tags for styling
        report_text.tag_configure("heading", font=("Helvetica", 12, "bold"))
        report_text.tag_configure("subheading", font=("Helvetica", 11, "bold"))
        report_text.tag_configure("normal", font=("Helvetica", 11))
        report_text.tag_configure("data", font=("Consolas", 11))
        
        # Structure type summary
        structure_types = {}
        for structure in structures:
            structure_types[structure.structure_type] = structure_types.get(structure.structure_type, 0) + 1
        
        report_text.insert(tk.END, "Structure Types:\n", "subheading")
        for type_name, count in structure_types.items():
            report_text.insert(tk.END, f"  {type_name}: {count}\n", "normal")
        
        report_text.insert(tk.END, "\nStructure Details:\n", "subheading")
        
        # Structure details with better formatting
        for i, structure in enumerate(structures):
            if i > 0:
                report_text.insert(tk.END, "\n" + "-"*50 + "\n", "normal")
                
            report_text.insert(tk.END, f"{structure.structure_id} ({structure.structure_type})\n", "subheading")
            report_text.insert(tk.END, f"  Rim Elevation: {structure.rim_elevation}\n", "data")
            report_text.insert(tk.END, f"  Invert Out: {structure.invert_out_elevation}\n", "data")
            report_text.insert(tk.END, f"  Total Drop: {structure.total_drop}\n", "data")
            
            if structure.pipe_length:
                report_text.insert(tk.END, f"  Pipe Length: {structure.pipe_length}\n", "data")
            if structure.pipe_diameter:
                report_text.insert(tk.END, f"  Pipe Diameter: {structure.pipe_diameter}\n", "data")
            if structure.pipe_type:
                report_text.insert(tk.END, f"  Pipe Type: {structure.pipe_type}\n", "data")
            if structure.upstream_structure_id:
                report_text.insert(tk.END, f"  Upstream Structure: {structure.upstream_structure_id}\n", "data")
        
        # Make text readonly
        report_text.configure(state='disabled')
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=15)
        
        # Export button
        ttk.Button(
            button_frame, 
            text="Export as PDF", 
            bootstyle="success",
            # Add PDF export functionality here
            command=lambda: Messagebox.show_info("PDF export functionality not implemented yet", "Feature Coming Soon")
        ).pack(side="left", padx=5)
        
        # Print button
        ttk.Button(
            button_frame, 
            text="Print", 
            bootstyle="info",
            # Add print functionality here
            command=lambda: Messagebox.show_info("Print functionality not implemented yet", "Feature Coming Soon")
        ).pack(side="left", padx=5)
        
        # Close button
        ttk.Button(
            button_frame, 
            text="Close", 
            bootstyle="secondary",
            command=report_window.destroy
        ).pack(side="right", padx=5)

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = StructureManagementApp(root)
    root.mainloop()