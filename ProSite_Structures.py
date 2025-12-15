import tkinter as tk
import ttkbootstrap as ttk
from datetime import datetime
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import ttkbootstrap.dialogs as dialogs
from database_manager import DatabaseManager
from typing import List, Dict, Optional
from models import Structure, StructureGroup, StructureComponent


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
        self.structure_types = ['CB', 'JB', 'DI', 'HW', 'UGDS', 'NYLO', 'DBCB']
        
        # Pipe Sizes (Diameters)
        self.pipe_sizes = ['4', '6', '8', '12', '15', '18', '24', '30', '36', '42', '48', '54', '60', '66', '72']

        # Start with login screen
        self.show_login_screen()

    def center_toplevel(self, toplevel: ttk.Toplevel):
        """Centers a toplevel window relative to the main application window."""
        toplevel.update_idletasks() # Process geometry strings and widget sizes

        # Get Toplevel window size
        width = toplevel.winfo_width()
        height = toplevel.winfo_height()

        # Get main window position and size
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()

        # Calculate position for the center
        x = main_x + (main_width // 2) - (width // 2)
        y = main_y + (main_height // 2) - (height // 2)

        # Set the new position, keeping the original size
        toplevel.geometry(f"{width}x{height}+{int(x)}+{int(y)}")

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
        register_window.geometry("415x415")
        self.center_toplevel(register_window)
        
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

        # Create menu bar
        self.create_menu_bar()

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
        self.notebook.bind("<<NotebookTabChanged>>", self.on_notebook_tab_changed)

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
        columns = ("ID", "TYPE", "RIM ELEVATION", "INV. OUT", "DEPTH", "UPSTREAM", "SLOPE", "DESCRIPTION")
        self.structure_tree = ttk.Treeview(
            treeview_frame, 
            columns=columns,
            show="headings", 
            selectmode="extended"
        )
        
        # Define column headings
        for col in columns:
            self.structure_tree.heading(col, text=col)

        # Set column widths and alignment
        self.structure_tree.column("ID", width=100, anchor="center")
        self.structure_tree.column("TYPE", width=60, anchor="center")
        self.structure_tree.column("RIM ELEVATION", width=100, anchor="center")
        self.structure_tree.column("INV. OUT", width=80, anchor="center")
        self.structure_tree.column("DEPTH", width=70, anchor="center")
        self.structure_tree.column("UPSTREAM", width=100, anchor="center")
        self.structure_tree.column("SLOPE", width=80, anchor="center")
        self.structure_tree.column("DESCRIPTION", width=150, anchor="center") 
        
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

        ttk.Button(
            button_frame, 
            text="Rename", 
            bootstyle="warning-outline",
            command=self.rename_structure_dialog
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
        'Pipe Diameter:', 'Pipe Type:', 'Description:']
        
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
            elif label == 'Pipe Diameter:':
                #Create dropdown for pipe sizes
                self.entries[label] = ttk.Combobox(form_frame, values=self.pipe_sizes, state="readonly")
            elif label == 'Pipe Type:':
                # Create dropdown for pipe types
                self.entries[label] = ttk.Combobox(form_frame, state="readonly")
                # Load pipe types from database
                self.refresh_pipe_types()    
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
        
        # Add right-click context menu for pipe ordering
        self.structure_tree.bind('<Button-3>', self.show_structure_context_menu)
        
        # Load structures for current project
        self.load_structures()

        # Add a new tab for component tracking
        self.components_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.components_frame, text='Component Tracking')
        
        # Configure the components frame
        self.setup_components_tab()

        # Add pipe tracking tab
        self.pipe_tracking_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.pipe_tracking_frame, text='Pipe Tracking')
        
        # Configure the pipe tracking frame
        self.setup_pipe_tracking_tab()

    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Structure", command=self.add_structure)
        file_menu.add_command(label="Import Structures...", command=self.import_structures)
        file_menu.add_command(label="Export Structures...", command=self.export_structures)
        file_menu.add_separator()
        file_menu.add_command(label="Generate Report", command=self.generate_report)
        file_menu.add_separator()
        file_menu.add_command(label="Close Project", command=self.show_project_selection)
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Delete Selected Structure", command=self.delete_selected_structure)
        edit_menu.add_command(label="Rename Structure", command=self.rename_structure_dialog)
        edit_menu.add_separator()
        edit_menu.add_command(label="Create Group", command=self.create_group)
        edit_menu.add_command(label="Manage Groups", command=self.manage_groups)
        edit_menu.add_separator()
        edit_menu.add_command(label="Find Structure...", command=self.find_structure)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        # Theme submenu
        theme_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="Theme", menu=theme_menu)
        themes = ["darkly", "cosmo", "flatly", "litera", "minty", "lumen", "sandstone", "yeti"]
        for theme in themes:
            theme_menu.add_command(label=theme.capitalize(), command=lambda t=theme: self.change_theme(t))
        
        settings_menu.add_separator()
        settings_menu.add_command(label="User Preferences", command=self.show_preferences)
        settings_menu.add_command(label="Project Settings", command=self.show_project_settings)
        
        # Help menu - Complete the label definition
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_separator()
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)

    def setup_components_tab(self):
        """Set up the enhanced component tracking tab"""
        print("Debug: Setting up components tab")

        # Configure components frame for proper expansion
        self.components_frame.columnconfigure(0, weight=1)
        self.components_frame.rowconfigure(0, weight=1)
        
        # Create main container frame
        main_container = ttk.Frame(self.components_frame)
        main_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=2)
        main_container.rowconfigure(0, weight=1)
        
        # === LEFT SIDE: Structure Overview ===
        structure_frame = ttk.Labelframe(main_container, text="Structure Overview", padding=10)
        structure_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        structure_frame.columnconfigure(0, weight=1)
        structure_frame.rowconfigure(1, weight=1)
        
        # Filter controls at the top
        filter_frame = ttk.Frame(structure_frame)
        filter_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        filter_frame.columnconfigure(1, weight=1)
        
        ttk.Label(filter_frame, text="Filter:").grid(row=0, column=0, padx=(0, 5), sticky="w")
        self.component_filter_var = tk.StringVar(value="All Structures")
        
        # Add "Approved" to filter options
        filter_combo = ttk.Combobox(
            filter_frame, 
            textvariable=self.component_filter_var, 
            values=["All Structures", "Installed", "Delivered", "Approved", "Incomplete", "Not Started", "In Progress"],
            state="readonly"
        )
        filter_combo.grid(row=0, column=1, sticky="ew")
        filter_combo.bind('<<ComboboxSelected>>', self.filter_structures_by_status)
        
        # Structure treeview frame
        tree_frame = ttk.Frame(structure_frame)
        tree_frame.grid(row=1, column=0, sticky="nsew")
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Enhanced structure treeview with status information 
        columns = ("ID", "TYPE", "STATUS", "PROGRESS")
        self.component_structure_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )
        
        # Define column headings and widths - CENTERED ALIGNMENT
        self.component_structure_tree.heading("ID", text="Structure ID", anchor="center")
        self.component_structure_tree.heading("TYPE", text="Type", anchor="center")
        self.component_structure_tree.heading("STATUS", text="Status", anchor="center")
        self.component_structure_tree.heading("PROGRESS", text="Progress", anchor="center")
        
        self.component_structure_tree.column("ID", width=120, anchor="center")
        self.component_structure_tree.column("TYPE", width=80, anchor="center")
        self.component_structure_tree.column("STATUS", width=100, anchor="center")
        self.component_structure_tree.column("PROGRESS", width=80, anchor="center")
        
        # Configure status tags for color coding - including new "approved" tag
        self.component_structure_tree.tag_configure("installed", background="#c3e6cb", foreground="#155724")  # Vibrant Green
        self.component_structure_tree.tag_configure("delivered", background="#b8daff", foreground="#004085")  # Vibrant Blue
        self.component_structure_tree.tag_configure("approved", background="#e2d7ff", foreground="#5a2d91")   # NEW: Purple for Approved
        self.component_structure_tree.tag_configure("in_progress", background="#ffeeba", foreground="#856404") # Vibrant Yellow
        self.component_structure_tree.tag_configure("not_started", background="#f5c6cb", foreground="#721c24") # Vibrant Red
        self.component_structure_tree.tag_configure("incomplete", background="#d6d8db", foreground="#383d41")  # Clear Grey
        
        # Add scrollbar
        structure_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.component_structure_tree.yview)
        self.component_structure_tree.configure(yscrollcommand=structure_scrollbar.set)
        
        # Pack treeview and scrollbar
        self.component_structure_tree.grid(row=0, column=0, sticky="nsew")
        structure_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Structure action buttons
        structure_action_frame = ttk.Frame(structure_frame)
        structure_action_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        ttk.Button(
            structure_action_frame,
            text="Refresh",
            bootstyle="secondary-outline",
            command=self.refresh_component_status
        ).pack(side="left", padx=2)
        
        # === RIGHT SIDE: Component Management ===
        component_frame = ttk.Labelframe(main_container, text="Component Management", padding=10)
        component_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        component_frame.columnconfigure(0, weight=1)
        component_frame.rowconfigure(1, weight=1)
        
        # Selected structure info header
        self.selected_structure_frame = ttk.Frame(component_frame)
        self.selected_structure_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.selected_structure_frame.columnconfigure(0, weight=1)
        
        # Create a sub-frame that aligns with the component treeview
        info_align_frame = ttk.Frame(self.selected_structure_frame)
        info_align_frame.grid(row=0, column=0, sticky="ew")
        info_align_frame.columnconfigure(1, weight=1)
        
        ttk.Label(info_align_frame, text="Selected Structure:", font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.selected_structure_label = ttk.Label(info_align_frame, text="None", font=("Helvetica", 10))
        self.selected_structure_label.grid(row=0, column=1, sticky="w", padx=10)
        
        # Component list area
        component_list_frame = ttk.Frame(component_frame)
        component_list_frame.grid(row=1, column=0, sticky="nsew")
        component_list_frame.columnconfigure(0, weight=1)
        component_list_frame.rowconfigure(0, weight=1)
        
        # Enhanced component treeview
        columns = ("COMPONENT", "STATUS", "ORDERED", "EXPECTED", "DELIVERED", "NOTES")
        self.component_tree = ttk.Treeview(
            component_list_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )
        
        # Define column headings and widths - CENTERED ALIGNMENT
        self.component_tree.heading("COMPONENT", text="Component Type", anchor="center")
        self.component_tree.heading("STATUS", text="Status", anchor="center")
        self.component_tree.heading("ORDERED", text="Order Date", anchor="center")
        self.component_tree.heading("EXPECTED", text="Expected", anchor="center")
        self.component_tree.heading("DELIVERED", text="Delivered", anchor="center")
        self.component_tree.heading("NOTES", text="Notes", anchor="center")
        
        self.component_tree.column("COMPONENT", width=120, anchor="center")
        self.component_tree.column("STATUS", width=100, anchor="center")
        self.component_tree.column("ORDERED", width=100, anchor="center")
        self.component_tree.column("EXPECTED", width=100, anchor="center")
        self.component_tree.column("DELIVERED", width=100, anchor="center")
        self.component_tree.column("NOTES", width=200, anchor="center")
        
        # Configure status tags for components
        self.component_tree.tag_configure("pending", background="#fff3cd", foreground="#856404")
        self.component_tree.tag_configure("ordered", background="#cce7ff", foreground="#004085")
        self.component_tree.tag_configure("shipped", background="#e2e3e5", foreground="#383d41")
        self.component_tree.tag_configure("delivered", background="#d1ecf1", foreground="#0c5460")
        self.component_tree.tag_configure("installed", background="#d4edda", foreground="#155724")
        
        # Add scrollbar for components
        component_scrollbar = ttk.Scrollbar(component_list_frame, orient="vertical", command=self.component_tree.yview)
        self.component_tree.configure(yscrollcommand=component_scrollbar.set)
        
        # Place component treeview and scrollbar
        self.component_tree.grid(row=0, column=0, sticky="nsew")
        component_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Component action buttons
        component_action_frame = ttk.Frame(component_frame)
        component_action_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        # Left side buttons - component management
        left_buttons = ttk.Frame(component_action_frame)
        left_buttons.pack(side="left")
        
        ttk.Button(
            left_buttons,
            text="Add Component",
            bootstyle="success-outline",
            command=self.add_component_enhanced
        ).pack(side="left", padx=2)
        
        ttk.Button(
            left_buttons,
            text="Quick Riser",
            bootstyle="info-outline",
            command=self.quick_add_riser
        ).pack(side="left", padx=2)
        
        ttk.Button(
            left_buttons,
            text="Quick Lid",
            bootstyle="info-outline",
            command=self.quick_add_lid
        ).pack(side="left", padx=2)
        
        # Right side buttons - reporting and bulk actions
        right_buttons = ttk.Frame(component_action_frame)
        right_buttons.pack(side="right")
        
        ttk.Button(
            right_buttons,
            text="Generate Report",
            bootstyle="secondary-outline",
            command=self.generate_delivery_report
        ).pack(side="left", padx=2)
        
        # Bind events
        self.component_structure_tree.bind('<<TreeviewSelect>>', self.on_structure_selected)
        self.component_tree.bind('<Button-3>', self.show_component_context_menu)  # Right-click only
        self.component_structure_tree.bind('<Button-3>', self.show_structure_component_context_menu)
        
        # Load initial data
        self.load_structures_for_components()
        
        print("DEBUG: Components tab initialization finished")

    def setup_pipe_tracking_tab(self):
        """Set up the pipe tracking tab with totals summary section"""
        print("Debug: Setting up pipe tracking tab")
        
        # Configure pipe tracking frame for proper expansion
        self.pipe_tracking_frame.columnconfigure(0, weight=1)
        self.pipe_tracking_frame.rowconfigure(1, weight=1)  # Changed to make middle section expandable
        
        # === TOP SECTION: Project Pipe Totals Summary ===
        totals_frame = ttk.Labelframe(self.pipe_tracking_frame, text="Project Pipe Summary", padding=10)
        totals_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 10))
        totals_frame.columnconfigure(1, weight=1)
        
        # Summary stats frame
        stats_frame = ttk.Frame(totals_frame)
        stats_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # Create summary labels
        self.total_pipe_length_label = ttk.Label(stats_frame, text="Total Pipe: 0.00 ft", font=("Helvetica", 12, "bold"))
        self.total_pipe_length_label.grid(row=0, column=0, padx=10, sticky="w")
        
        self.delivered_pipe_length_label = ttk.Label(stats_frame, text="Delivered: 0.00 ft", font=("Helvetica", 12, "bold"), bootstyle="success")
        self.delivered_pipe_length_label.grid(row=0, column=1, padx=10, sticky="w")
        
        self.pending_pipe_length_label = ttk.Label(stats_frame, text="Pending: 0.00 ft", font=("Helvetica", 12, "bold"), bootstyle="warning")
        self.pending_pipe_length_label.grid(row=0, column=2, padx=10, sticky="w")
        
        self.completion_percentage_label = ttk.Label(stats_frame, text="0% Complete", font=("Helvetica", 12, "bold"), bootstyle="info")
        self.completion_percentage_label.grid(row=0, column=3, padx=10, sticky="w")
        
        # Progress bar
        progress_frame = ttk.Frame(totals_frame)
        progress_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        ttk.Label(progress_frame, text="Delivery Progress:", font=("Helvetica", 10)).grid(row=0, column=0, sticky="w")
        self.delivery_progress = ttk.Progressbar(progress_frame, mode="determinate", bootstyle="success-striped")
        self.delivery_progress.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        
        # Pipe type breakdown table
        breakdown_frame = ttk.Labelframe(totals_frame, text="Breakdown by Pipe Type", padding=5)
        breakdown_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        breakdown_frame.columnconfigure(0, weight=1)
        
        # Create treeview for pipe type breakdown
        breakdown_columns = ("PIPE_TYPE", "DIAMETER", "TOTAL_LENGTH", "DELIVERED", "PENDING", "PROGRESS")
        self.pipe_totals_tree = ttk.Treeview(
            breakdown_frame,
            columns=breakdown_columns,
            show="headings",
            height=6
        )
        
        # Configure columns
        self.pipe_totals_tree.heading("PIPE_TYPE", text="Pipe Type", anchor="center")
        self.pipe_totals_tree.heading("DIAMETER", text="Diameter", anchor="center")
        self.pipe_totals_tree.heading("TOTAL_LENGTH", text="Total (ft)", anchor="center")
        self.pipe_totals_tree.heading("DELIVERED", text="Delivered (ft)", anchor="center")
        self.pipe_totals_tree.heading("PENDING", text="Pending (ft)", anchor="center")
        self.pipe_totals_tree.heading("PROGRESS", text="Progress", anchor="center")
        
        self.pipe_totals_tree.column("PIPE_TYPE", width=120, anchor="center")
        self.pipe_totals_tree.column("DIAMETER", width=80, anchor="center")
        self.pipe_totals_tree.column("TOTAL_LENGTH", width=100, anchor="center")
        self.pipe_totals_tree.column("DELIVERED", width=100, anchor="center")
        self.pipe_totals_tree.column("PENDING", width=100, anchor="center")
        self.pipe_totals_tree.column("PROGRESS", width=100, anchor="center")
        
        # Configure progress tags
        self.pipe_totals_tree.tag_configure("complete", background="#d4edda", foreground="#155724")
        self.pipe_totals_tree.tag_configure("in_progress", background="#fff3cd", foreground="#856404")
        self.pipe_totals_tree.tag_configure("not_started", background="#f8d7da", foreground="#721c24")
        
        # Add scrollbar for breakdown
        totals_scrollbar = ttk.Scrollbar(breakdown_frame, orient="vertical", command=self.pipe_totals_tree.yview)
        self.pipe_totals_tree.configure(yscrollcommand=totals_scrollbar.set)
        
        # Pack breakdown treeview and scrollbar
        self.pipe_totals_tree.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        totals_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Refresh button for totals
        refresh_totals_btn = ttk.Button(
            breakdown_frame,
            text="Refresh Totals",
            bootstyle="primary-outline",
            command=self.calculate_project_pipe_totals
        )
        refresh_totals_btn.grid(row=1, column=0, pady=(10, 0), sticky="w")
        
        # === MIDDLE SECTION: Order Management (Modified) ===
        main_container = ttk.Frame(self.pipe_tracking_frame)
        main_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=2)
        main_container.rowconfigure(0, weight=1)
        
        # === LEFT SIDE: Pipe Order Summary ===
        order_summary_frame = ttk.Labelframe(main_container, text="Pipe Orders", padding=10)
        order_summary_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        order_summary_frame.columnconfigure(0, weight=1)
        order_summary_frame.rowconfigure(1, weight=1)
        
        # Filter controls at the top
        filter_frame = ttk.Frame(order_summary_frame)
        filter_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        filter_frame.columnconfigure(1, weight=1)
        
        ttk.Label(filter_frame, text="Filter:").grid(row=0, column=0, padx=(0, 5), sticky="w")
        self.pipe_filter_var = tk.StringVar(value="All Orders")
        filter_combo = ttk.Combobox(
            filter_frame, 
            textvariable=self.pipe_filter_var, 
            values=["All Orders", "Pending", "Ordered", "In Transit", "Delivered", "By Pipe Type"],
            state="readonly"
        )
        filter_combo.grid(row=0, column=1, sticky="ew")
        filter_combo.bind('<<ComboboxSelected>>', self.filter_pipe_orders)
        
        # Pipe orders treeview frame
        orders_tree_frame = ttk.Frame(order_summary_frame)
        orders_tree_frame.grid(row=1, column=0, sticky="nsew")
        orders_tree_frame.columnconfigure(0, weight=1)
        orders_tree_frame.rowconfigure(0, weight=1)
        
        # Pipe orders treeview
        columns = ("ORDER", "PIPE_TYPE", "DIAMETER", "TOTAL_LENGTH", "STATUS", "ORDER_DATE", "DATE_DELIVERED")
        self.pipe_orders_tree = ttk.Treeview(
            orders_tree_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )
        
        # Define column headings and widths
        self.pipe_orders_tree.heading("ORDER", text="Order #", anchor="center")
        self.pipe_orders_tree.heading("PIPE_TYPE", text="Pipe Type", anchor="center")
        self.pipe_orders_tree.heading("DIAMETER", text="Diameter", anchor="center")
        self.pipe_orders_tree.heading("TOTAL_LENGTH", text="Total Length", anchor="center")
        self.pipe_orders_tree.heading("STATUS", text="Status", anchor="center")
        self.pipe_orders_tree.heading("ORDER_DATE", text="Order Date", anchor="center")
        self.pipe_orders_tree.heading("DATE_DELIVERED", text="Date Delivered", anchor="center")
        
        self.pipe_orders_tree.column("ORDER", width=80, anchor="center")
        self.pipe_orders_tree.column("PIPE_TYPE", width=120, anchor="center")
        self.pipe_orders_tree.column("DIAMETER", width=80, anchor="center")
        self.pipe_orders_tree.column("TOTAL_LENGTH", width=100, anchor="center")
        self.pipe_orders_tree.column("STATUS", width=100, anchor="center")
        self.pipe_orders_tree.column("ORDER_DATE", width=100, anchor="center")
        self.pipe_orders_tree.column("DATE_DELIVERED", width=120, anchor="center")
        
        # Configure status tags for color coding
        self.pipe_orders_tree.tag_configure("pending", background="#fff3cd", foreground="#856404")
        self.pipe_orders_tree.tag_configure("ordered", background="#cce7ff", foreground="#004085")
        self.pipe_orders_tree.tag_configure("in_transit", background="#e2e3e5", foreground="#383d41")
        self.pipe_orders_tree.tag_configure("delivered", background="#d4edda", foreground="#155724")
        
        # Add scrollbar
        orders_scrollbar = ttk.Scrollbar(orders_tree_frame, orient="vertical", command=self.pipe_orders_tree.yview)
        self.pipe_orders_tree.configure(yscrollcommand=orders_scrollbar.set)
        
        # Pack orders treeview and scrollbar
        self.pipe_orders_tree.grid(row=0, column=0, sticky="nsew")
        orders_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Orders action buttons
        orders_action_frame = ttk.Frame(order_summary_frame)
        orders_action_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        ttk.Button(
            orders_action_frame,
            text="New Order",
            bootstyle="success-outline",
            command=self.create_new_pipe_order
        ).pack(side="left", padx=2)
        
        ttk.Button(
            orders_action_frame,
            text="Update Status",
            bootstyle="primary-outline",
            command=self.update_pipe_order_status
        ).pack(side="left", padx=2)
        
        ttk.Button(
            orders_action_frame,
            text="Refresh",
            bootstyle="secondary-outline",   
            command=self.refresh_pipe_orders
        ).pack(side="right", padx=2)

        ttk.Button(
            orders_action_frame,
            text="Delete Order",
            bootstyle="danger-outline",
            command=self.delete_pipe_order
        ).pack(side="left", padx=2)
        
        # === RIGHT SIDE: Order Details and Structure Breakdown ===
        details_frame = ttk.Labelframe(main_container, text="Order Details", padding=10)
        details_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(1, weight=1)
        
        # Selected order info header
        self.selected_order_frame = ttk.Frame(details_frame)
        self.selected_order_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.selected_order_frame.columnconfigure(0, weight=1)
        
        info_align_frame = ttk.Frame(self.selected_order_frame)
        info_align_frame.grid(row=0, column=0, sticky="ew")
        info_align_frame.columnconfigure(1, weight=1)
        
        ttk.Label(info_align_frame, text="Selected Order:", font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.selected_order_label = ttk.Label(info_align_frame, text="None", font=("Helvetica", 10))
        self.selected_order_label.grid(row=0, column=1, sticky="w", padx=10)
        
        # Order breakdown area
        breakdown_frame = ttk.Frame(details_frame)
        breakdown_frame.grid(row=1, column=0, sticky="nsew")
        breakdown_frame.columnconfigure(0, weight=1)
        breakdown_frame.rowconfigure(0, weight=1)
        
        # Order breakdown treeview
        columns = ("STRUCTURE", "PIPE_TYPE", "DIAMETER", "LENGTH", "DELIVERED", "NOTES")
        self.order_breakdown_tree = ttk.Treeview(
            breakdown_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )
        
        # Define column headings and widths
        self.order_breakdown_tree.heading("STRUCTURE", text="Structure", anchor="center")
        self.order_breakdown_tree.heading("PIPE_TYPE", text="Pipe Type", anchor="center")
        self.order_breakdown_tree.heading("DIAMETER", text="Diameter", anchor="center")
        self.order_breakdown_tree.heading("LENGTH", text="Length", anchor="center")
        self.order_breakdown_tree.heading("DELIVERED", text="Delivered", anchor="center")
        self.order_breakdown_tree.heading("NOTES", text="Notes", anchor="center")
        
        self.order_breakdown_tree.column("STRUCTURE", width=100, anchor="center")
        self.order_breakdown_tree.column("PIPE_TYPE", width=120, anchor="center")
        self.order_breakdown_tree.column("DIAMETER", width=80, anchor="center")
        self.order_breakdown_tree.column("LENGTH", width=80, anchor="center")
        self.order_breakdown_tree.column("DELIVERED", width=80, anchor="center")
        self.order_breakdown_tree.column("NOTES", width=150, anchor="center")
        
        # Configure delivery status tags
        self.order_breakdown_tree.tag_configure("not_delivered", background="#f8d7da", foreground="#721c24")
        self.order_breakdown_tree.tag_configure("delivered", background="#d4edda", foreground="#155724")
        self.order_breakdown_tree.tag_configure("partial", background="#fff3cd", foreground="#856404")
        
        # Add scrollbar for breakdown
        breakdown_scrollbar = ttk.Scrollbar(breakdown_frame, orient="vertical", command=self.order_breakdown_tree.yview)
        self.order_breakdown_tree.configure(yscrollcommand=breakdown_scrollbar.set)
        
        # Place breakdown treeview and scrollbar
        self.order_breakdown_tree.grid(row=0, column=0, sticky="nsew")
        breakdown_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Breakdown action buttons
        breakdown_action_frame = ttk.Frame(details_frame)
        breakdown_action_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        # Left side buttons
        left_buttons = ttk.Frame(breakdown_action_frame)
        left_buttons.pack(side="left")
        
        ttk.Button(
            left_buttons,
            text="Mark Delivered",
            bootstyle="success-outline",
            command=self.mark_pipe_delivered
        ).pack(side="left", padx=2)
        
        ttk.Button(
            left_buttons,
            text="Add Notes",
            bootstyle="info-outline",
            command=self.add_pipe_notes_enhanced
        ).pack(side="left", padx=2)
        
        # Right side buttons
        right_buttons = ttk.Frame(breakdown_action_frame)
        right_buttons.pack(side="right")
        
        ttk.Button(
            right_buttons,
            text="Generate Report",
            bootstyle="secondary-outline",
            command=self.generate_pipe_delivery_report
        ).pack(side="left", padx=2)
        
        # Bind events
        self.pipe_orders_tree.bind('<<TreeviewSelect>>', self.on_pipe_order_selected)
        self.order_breakdown_tree.bind('<Button-3>', self.show_pipe_breakdown_context_menu_enhanced)
        
        # Load initial data
        self.load_pipe_orders()
        self.calculate_project_pipe_totals()  # Calculate totals on startup
        
        print("DEBUG: Pipe tracking tab initialization finished")

    def calculate_project_pipe_totals(self):
        """Calculate total pipe quantities across the entire project"""
        try:
            # Get project ID
            project = self.db.get_project_by_name(self.current_project, self.current_user.id)
            if not project:
                return
            
            print("DEBUG: Calculating project pipe totals...")
            
            # Get all structures with pipe data
            structures = self.db.get_all_structures(project.id)
            structures_with_pipe = [s for s in structures if s.pipe_length and s.pipe_diameter and s.pipe_type]
            
            if not structures_with_pipe:
                self._update_totals_display(0, 0, {})
                return
            
            # Calculate totals by pipe type and diameter
            pipe_totals = {}
            total_project_length = 0
            
            for structure in structures_with_pipe:
                # Create key for grouping
                key = f"{structure.pipe_type}_{int(structure.pipe_diameter) if structure.pipe_diameter is not None else 'unknown'}"
                
                if key not in pipe_totals:
                    pipe_totals[key] = {
                        'pipe_type': structure.pipe_type,
                        'diameter': structure.pipe_diameter,
                        'total_length': 0,
                        'delivered_length': 0,
                        'structures': []
                    }
                
                pipe_totals[key]['total_length'] += structure.pipe_length
                pipe_totals[key]['structures'].append(structure.structure_id)
                total_project_length += structure.pipe_length
            
            # Get delivery information from pipe orders
            total_delivered_length = self._calculate_delivered_pipe_totals(project.id, pipe_totals)
            
            # Update the display
            self._update_totals_display(total_project_length, total_delivered_length, pipe_totals)
            
            print(f"DEBUG: Calculated totals - Total: {total_project_length:.2f}ft, Delivered: {total_delivered_length:.2f}ft")
            
        except Exception as e:
            self.logger.error(f"Error calculating project pipe totals: {e}", exc_info=True)
            print(f"ERROR calculating pipe totals: {e}")

    def _calculate_delivered_pipe_totals(self, project_id: int, pipe_totals: dict) -> float:
        """Calculate delivered pipe quantities from orders"""
        try:
            total_delivered = 0
            
            # Get all pipe orders for this project
            pipe_orders = self.db.get_pipe_orders(project_id)
            
            for order in pipe_orders:
                # Get order items regardless of order status, as items can be delivered partially
                order_items = self.db.get_pipe_order_items(order.get('id'))
                
                for item in order_items:
                    delivered_length = item.get('delivered_length', 0)
                    pipe_type = item.get('pipe_type', '')
                    diameter = item.get('diameter', 0)
                    
                    # Update delivered amounts in pipe_totals
                    key = f"{pipe_type}_{int(diameter) if diameter is not None else 'unknown'}"
                    if key in pipe_totals:
                        pipe_totals[key]['delivered_length'] += delivered_length
                    
                    total_delivered += delivered_length
            
            return total_delivered
            
        except Exception as e:
            self.logger.error(f"Error calculating delivered pipe totals: {e}", exc_info=True)
            return 0

    def _update_totals_display(self, total_length: float, delivered_length: float, pipe_totals: dict):
        """Update the totals display with calculated values"""
        try:
            pending_length = total_length - delivered_length
            completion_percentage = (delivered_length / total_length * 100) if total_length > 0 else 0
            
            # Update summary labels
            self.total_pipe_length_label.config(text=f"Total Pipe: {total_length:.2f} ft")
            self.delivered_pipe_length_label.config(text=f"Delivered: {delivered_length:.2f} ft")
            self.pending_pipe_length_label.config(text=f"Pending: {pending_length:.2f} ft")
            self.completion_percentage_label.config(text=f"{completion_percentage:.1f}% Complete")
            
            # Update progress bar
            self.delivery_progress['value'] = completion_percentage
            
            # Clear and update breakdown treeview
            for item in self.pipe_totals_tree.get_children():
                self.pipe_totals_tree.delete(item)
            
            # Populate breakdown by pipe type
            for key, data in pipe_totals.items():
                diameter_text = f"{int(data['diameter'])}\"" if data['diameter'] else "Unknown"
                total_length = data['total_length']
                delivered_length = data['delivered_length']
                pending_length = total_length - delivered_length
                progress_pct = (delivered_length / total_length * 100) if total_length > 0 else 0
                
                # Determine status tag
                if progress_pct >= 100:
                    tag = "complete"
                elif progress_pct > 0:
                    tag = "in_progress"
                else:
                    tag = "not_started"
                
                self.pipe_totals_tree.insert(
                    "", "end",
                    values=(
                        data['pipe_type'],
                        diameter_text,
                        f"{total_length:.2f}",
                        f"{delivered_length:.2f}",
                        f"{pending_length:.2f}",
                        f"{progress_pct:.1f}%"
                    ),
                    tags=(tag,)
                )
            
            # Sort by pipe type for consistent display
            children = self.pipe_totals_tree.get_children()
            children_data = [(self.pipe_totals_tree.item(child, "values"), child) for child in children]
            children_data.sort(key=lambda x: x[0][0])  # Sort by pipe type
            
            for i, (values, child) in enumerate(children_data):
                self.pipe_totals_tree.move(child, "", i)
                
        except Exception as e:
            self.logger.error(f"Error updating totals display: {e}", exc_info=True)

    def delete_pipe_order(self):
        """Delete the selected pipe order with confirmation"""
        selection = self.pipe_orders_tree.selection()
        if not selection:
            Messagebox.show_warning("Please select a pipe order to delete", "No Order Selected")
            return
        
        values = self.pipe_orders_tree.item(selection[0], "values")
        order_number = values[0]
        
        # Skip separator rows
        if "──" in order_number:
            Messagebox.show_warning("Please select a valid pipe order", "Invalid Selection")
            return
        
        # Get order details for confirmation
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            return
        
        # Find the order ID
        pipe_orders = self.db.get_pipe_orders(project.id)
        order_id = None
        order_details = None
        
        for order in pipe_orders:
            if order.get('order_number') == order_number:
                order_id = order.get('id')
                order_details = order
                break
        
        if not order_id:
            Messagebox.show_error("Order not found", "Error")
            return
        
        # Get detailed order information
        detailed_order = self.db.get_pipe_order_details(order_id)
        if not detailed_order:
            Messagebox.show_error("Could not retrieve order details", "Error")
            return
        
        # Show detailed confirmation dialog
        self.show_delete_order_confirmation(order_id, detailed_order)

    def show_delete_order_confirmation(self, order_id: int, order_details: dict):
        """Show a detailed confirmation dialog for deleting a pipe order"""
        # Create confirmation window
        confirm_window = ttk.Toplevel(self.root)
        confirm_window.title("Confirm Delete Pipe Order")
        confirm_window.geometry("505x490")
        self.center_toplevel(confirm_window)
        confirm_window.transient(self.root)
        confirm_window.grab_set()
        
        # Main container
        main_frame = ttk.Frame(confirm_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Warning icon and title
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(
            header_frame,
            text="⚠️ Delete Pipe Order",
            font=("Helvetica", 16, "bold"),
            bootstyle="danger"
        ).pack()
        
        ttk.Label(
            header_frame,
            text="This action cannot be undone!",
            font=("Helvetica", 10),
            bootstyle="warning"
        ).pack(pady=(5, 0))
        
        # Order details section
        details_frame = ttk.Labelframe(main_frame, text="Order Information", padding=10)
        details_frame.pack(fill="x", pady=(0, 20))
        
        # Order details
        details_text = f"""Order Number: {order_details['order_number']}
    Supplier: {order_details.get('supplier', 'N/A')}
    Status: {order_details['status'].title()}
    Total Items: {order_details['item_count']}
    Total Length: {order_details['total_length']:.2f} ft"""
        
        if order_details.get('order_date'):
            try:
                order_date = datetime.fromisoformat(order_details['order_date']).strftime("%m/%d/%Y")
                details_text += f"\nOrder Date: {order_date}"
            except:
                pass
        
        if order_details.get('notes'):
            details_text += f"\nNotes: {order_details['notes']}"
        
        ttk.Label(
            details_frame,
            text=details_text,
            justify="left",
            font=("Helvetica", 10)
        ).pack(anchor="w")
        
        # Warning section
        warning_frame = ttk.Labelframe(main_frame, text="Warning", padding=10)
        warning_frame.pack(fill="x", pady=(0, 20))
        
        warning_text = """Deleting this order will:
    • Remove the order and ALL associated pipe items
    • Remove all delivery tracking for these items
    • This action cannot be undone
    • Consider updating the status instead of deleting"""
        
        ttk.Label(
            warning_frame,
            text=warning_text,
            justify="left",
            font=("Helvetica", 9),
            bootstyle="warning"
        ).pack(anchor="w")
        
        # Safety check - prevent deletion of delivered orders
        if order_details['status'].lower() in ['delivered', 'in_transit']:
            safety_frame = ttk.Labelframe(main_frame, text="Safety Check", padding=10)
            safety_frame.pack(fill="x", pady=(0, 20))
            
            ttk.Label(
                safety_frame,
                text="⚠️ This order has a status of 'Delivered' or 'In Transit'.\nDeletion is not recommended for orders with delivery progress.",
                justify="left",
                font=("Helvetica", 9, "bold"),
                bootstyle="danger"
            ).pack(anchor="w")
            
            # Add extra confirmation for delivered orders
            confirm_var = tk.BooleanVar()
            ttk.Checkbutton(
                safety_frame,
                text="I understand this order has delivery progress and still want to delete it",
                variable=confirm_var,
                bootstyle="danger"
            ).pack(anchor="w", pady=(10, 0))
        else:
            confirm_var = tk.BooleanVar(value=True)  # No extra confirmation needed
        
        def confirm_deletion():
            if not confirm_var.get():
                Messagebox.show_warning("Please confirm that you want to delete this delivered/in-transit order", "Confirmation Required")
                return
            
            # Perform the deletion
            success = self.db.delete_pipe_order(order_id)
            
            if success:
                Messagebox.show_info(f"Order '{order_details['order_number']}' deleted successfully", "Order Deleted")
                confirm_window.destroy()
                
                # Refresh the pipe orders view
                self.refresh_pipe_orders()
                
                # Clear order breakdown if this order was selected
                self.selected_order_label.config(text="None")
                self.clear_order_breakdown()
                
            else:
                Messagebox.show_error("Failed to delete the order", "Deletion Failed")
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        # Delete button
        ttk.Button(
            button_frame,
            text="Delete Order",
            bootstyle="danger",
            command=confirm_deletion
        ).pack(side="left", padx=5)
        
        # Cancel button
        ttk.Button(
            button_frame,
            text="Cancel",
            bootstyle="secondary",
            command=confirm_window.destroy
        ).pack(side="right", padx=5)

    def show_pipe_order_context_menu(self, event):
        """Show enhanced right-click context menu for pipe orders with status management"""
        # Get the item under the cursor
        item = self.pipe_orders_tree.identify_row(event.y)
        if not item:
            return
        
        # Select the item
        self.pipe_orders_tree.selection_set(item)
        
        # Get order details
        values = self.pipe_orders_tree.item(item, "values")
        if not values or "──" in values[0]:  # Skip separator rows
            return
        
        order_number = values[0]
        order_status = values[4].lower()
        
        # Create context menu
        context_menu = tk.Menu(self.root, tearoff=0)
        
        context_menu.add_command(
            label="View Details",
            command=lambda: self.on_pipe_order_selected(None)
        )
        
        context_menu.add_separator()
        
        # Quick status updates submenu
        status_menu = tk.Menu(context_menu, tearoff=0)
        context_menu.add_cascade(label="Quick Status Update", menu=status_menu)
        
        statuses = ["pending", "ordered", "delivered"]
        for status in statuses:
            if status != order_status:
                status_menu.add_command(
                    label=status.title(),
                    command=lambda s=status: self.quick_update_pipe_order_status(s)
                )
        
        context_menu.add_separator()
        
        context_menu.add_command(
            label="Edit Order Details",
            command=self.show_pipe_order_edit_dialog
        )
        
        context_menu.add_command(
            label="Mark as Delivered",
            command=self.quick_mark_pipe_order_delivered
        )
        
        context_menu.add_separator()
        
        # Different options based on status
        if order_status in ['pending', 'ordered']:
            context_menu.add_command(
                label="Duplicate Order",
                command=lambda: self.duplicate_pipe_order(order_number)
            )
        
        context_menu.add_separator()
        
        # Delete option with warning color for delivered orders
        if order_status in ['delivered']:
            context_menu.add_command(
                label="⚠️ Delete Order (Delivered)",
                command=self.delete_pipe_order
            )
        else:
            context_menu.add_command(
                label="Delete Order",
                command=self.delete_pipe_order
            )
        
        # Show the menu
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()



    def quick_update_pipe_order_status(self, new_status):
        """Quickly update pipe order status from context menu"""
        selection = self.pipe_orders_tree.selection()
        if not selection:
            return
        
        values = self.pipe_orders_tree.item(selection[0], "values")
        order_number = values[0]
        
        # Skip separator rows
        if "──" in order_number:
            Messagebox.show_warning("Please select a valid pipe order", "Invalid Selection")
            return
        
        # Get order ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            return
        
        pipe_orders = self.db.get_pipe_orders(project.id)
        order_id = None
        
        for order in pipe_orders:
            if order.get('order_number') == order_number:
                order_id = order.get('id')
                break
        
        if not order_id:
            Messagebox.show_error("Order not found", "Error")
            return
        
        # Set delivery date if changing to delivered
        delivery_date = None
        if new_status == "delivered":
            delivery_date = datetime.now()
        
        # Update status
        success = self.db.update_pipe_order_status(
            order_id=order_id,
            status=new_status,
            delivery_date=delivery_date,
            notes=None
        )
        
        if success:
            # Refresh views
            self.refresh_pipe_orders()
            
            # Refresh breakdown if this order is selected
            if self.pipe_orders_tree.selection():
                current_order = self.pipe_orders_tree.item(self.pipe_orders_tree.selection()[0], "values")[0]
                if current_order == order_number:
                    self.load_order_breakdown(order_number)
            
            # Show brief success message
            self.show_status_toast(f"Order status updated to '{new_status.title()}'")
        else:
            Messagebox.show_error("Failed to update order status", "Error")

    def quick_mark_pipe_order_delivered(self):
        """Quickly mark entire pipe order as delivered with today's date"""
        selection = self.pipe_orders_tree.selection()
        if not selection:
            Messagebox.show_warning("Please select a pipe order first", "No Order Selected")
            return
        
        values = self.pipe_orders_tree.item(selection[0], "values")
        order_number = values[0]
        
        # Skip separator rows
        if "──" in order_number:
            Messagebox.show_warning("Please select a valid pipe order", "Invalid Selection")
            return
        
        # Get order ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            return
        
        pipe_orders = self.db.get_pipe_orders(project.id)
        order_id = None
        
        for order in pipe_orders:
            if order.get('order_number') == order_number:
                order_id = order.get('id')
                break
        
        if not order_id:
            Messagebox.show_error("Order not found", "Error")
            return
        
        # Confirm action
        confirm = Messagebox.yesno(
            f"Mark order '{order_number}' as delivered with today's date?\n\nThis will also mark all pipe items in this order as delivered.",
            "Confirm Delivery"
        )
        
        if not confirm:
            return
        
        try:
            delivery_date = datetime.now()
            
            # Update order status
            order_success = self.db.update_pipe_order_status(
                order_id=order_id,
                status="delivered",
                delivery_date=delivery_date,
                notes=f"Marked as delivered on {delivery_date.strftime('%m/%d/%Y')}"
            )
            
            if order_success:
                # Also mark all items in the order as delivered
                order_items = self.db.get_pipe_order_items(order_id)
                items_updated = 0
                
                for item in order_items:
                    item_success = self.db.update_pipe_item_delivery(
                        item_id=item['id'],
                        delivered_length=item['length'],  # Mark full length as delivered
                        status="delivered",
                        notes=f"Auto-delivered with order on {delivery_date.strftime('%m/%d/%Y')}"
                    )
                    if item_success:
                        items_updated += 1
                
                # Show success message
                Messagebox.show_info(
                    f"Order '{order_number}' marked as delivered!\n\nOrder status updated and {items_updated} pipe items marked as delivered.",
                    "Delivery Complete"
                )
                
                # Refresh views
                self.refresh_pipe_orders()
                self.calculate_project_pipe_totals()
                
                # Refresh breakdown if this order is selected
                if self.pipe_orders_tree.selection():
                    current_order = self.pipe_orders_tree.item(self.pipe_orders_tree.selection()[0], "values")[0]
                    if current_order == order_number:
                        self.load_order_breakdown(order_number)
            else:
                Messagebox.show_error("Failed to mark order as delivered", "Error")
                
        except Exception as e:
            self.logger.error(f"Error marking order as delivered: {e}", exc_info=True)
            Messagebox.show_error(f"An error occurred: {str(e)}", "Error")

    def show_pipe_order_edit_dialog(self):
        """Show enhanced edit dialog for pipe order with delivery date tracking"""
        selection = self.pipe_orders_tree.selection()
        if not selection:
            Messagebox.show_warning("Please select a pipe order first", "No Order Selected")
            return
        
        values = self.pipe_orders_tree.item(selection[0], "values")
        order_number = values[0]
        current_status = values[4].lower()
        
        # Skip separator rows
        if "──" in order_number:
            Messagebox.show_warning("Please select a valid pipe order", "Invalid Selection")
            return
        
        # Get order details
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            return
        
        pipe_orders = self.db.get_pipe_orders(project.id)
        order_id = None
        order_data = None
        
        for order in pipe_orders:
            if order.get('order_number') == order_number:
                order_id = order.get('id')
                order_data = order
                break
        
        if not order_id:
            Messagebox.show_error("Order not found", "Error")
            return
        
        # Create edit dialog
        edit_window = ttk.Toplevel(self.root)
        edit_window.title("Edit Pipe Order")
        edit_window.geometry("520x650")
        self.center_toplevel(edit_window)
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Main container
        main_frame = ttk.Frame(edit_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(
            main_frame, 
            text="Edit Pipe Order", 
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        ).pack(pady=(0, 20))
        
        # Order info
        info_frame = ttk.Labelframe(main_frame, text="Order Information", padding=10)
        info_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(info_frame, text=f"Order Number: {order_number}", font=("Helvetica", 12, "bold")).pack(anchor="w")
        ttk.Label(info_frame, text=f"Current Status: {current_status.title()}", font=("Helvetica", 10)).pack(anchor="w")
        
        # Status update section
        status_frame = ttk.Labelframe(main_frame, text="Update Status", padding=10)
        status_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(status_frame, text="New Status:").pack(anchor="w", pady=(0, 5))
        
        status_var = tk.StringVar(value=current_status)
        status_options = ["pending", "ordered", "delivered"]
        status_combo = ttk.Combobox(status_frame, textvariable=status_var, values=status_options, state="readonly")
        status_combo.pack(fill="x", pady=(0, 10))
        
        # Date fields with calendar buttons
        date_frame = ttk.Frame(status_frame)
        date_frame.pack(fill="x", pady=(10, 0))
        
        # Order date
        order_frame = ttk.Frame(date_frame)
        ttk.Label(order_frame, text="Order Date:").pack(anchor="w")
        order_date_frame = ttk.Frame(order_frame)
        order_date_frame.pack(fill="x", pady=(2, 10))
        order_entry = ttk.Entry(order_date_frame)
        order_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        order_cal_btn = ttk.Button(order_date_frame, text="📅", width=3,
                                command=lambda: self.open_date_picker(order_entry))
        order_cal_btn.pack(side="right")
        
        # Pre-fill order date
        if order_data.get('order_date'):
            try:
                order_date_obj = datetime.fromisoformat(order_data['order_date'])
                order_entry.insert(0, order_date_obj.strftime("%m/%d/%Y"))
            except:
                pass
        
        # Expected delivery date
        expected_frame = ttk.Frame(date_frame)
        ttk.Label(expected_frame, text="Expected Delivery:").pack(anchor="w")
        expected_date_frame = ttk.Frame(expected_frame)
        expected_date_frame.pack(fill="x", pady=(2, 10))
        expected_entry = ttk.Entry(expected_date_frame)
        expected_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        expected_cal_btn = ttk.Button(expected_date_frame, text="📅", width=3,
                                    command=lambda: self.open_date_picker(expected_entry))
        expected_cal_btn.pack(side="right")
        
        # Pre-fill expected date
        if order_data.get('expected_delivery_date'):
            try:
                expected_date_obj = datetime.fromisoformat(order_data['expected_delivery_date'])
                expected_entry.insert(0, expected_date_obj.strftime("%m/%d/%Y"))
            except:
                pass
        
        # Actual delivery date
        delivery_frame = ttk.Frame(date_frame)
        ttk.Label(delivery_frame, text="Actual Delivery:").pack(anchor="w")
        actual_date_frame = ttk.Frame(delivery_frame)
        actual_date_frame.pack(fill="x", pady=(2, 10))
        actual_entry = ttk.Entry(actual_date_frame)
        actual_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        actual_cal_btn = ttk.Button(actual_date_frame, text="📅", width=3,
                                command=lambda: self.open_date_picker(actual_entry))
        actual_cal_btn.pack(side="right")
        
        # Pre-fill actual delivery date
        if order_data.get('actual_delivery_date'):
            try:
                actual_date_obj = datetime.fromisoformat(order_data['actual_delivery_date'])
                actual_entry.insert(0, actual_date_obj.strftime("%m/%d/%Y"))
            except:
                pass
        
        # Show/hide date fields based on status
        def update_date_visibility(*args):
            # Clear all frames first
            order_frame.pack_forget()
            expected_frame.pack_forget()
            delivery_frame.pack_forget()
            
            status = status_var.get()
            if status in ["ordered", "delivered"]:
                order_frame.pack(fill="x")
                expected_frame.pack(fill="x")
            
            if status == "delivered":
                delivery_frame.pack(fill="x")
                if not actual_entry.get():
                    actual_entry.delete(0, tk.END)
                    actual_entry.insert(0, datetime.now().strftime("%m/%d/%Y"))
        
        status_var.trace("w", update_date_visibility)
        update_date_visibility()  # Initial setup
        
        # Supplier section
        supplier_frame = ttk.Labelframe(main_frame, text="Supplier Information", padding=10)
        supplier_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(supplier_frame, text="Supplier:").pack(anchor="w", pady=(0, 5))
        supplier_entry = ttk.Entry(supplier_frame)
        supplier_entry.pack(fill="x", pady=(0, 10))
        
        # Pre-fill supplier
        if order_data.get('supplier'):
            supplier_entry.insert(0, order_data['supplier'])
        
        # Notes section
        notes_frame = ttk.Labelframe(main_frame, text="Notes", padding=10)
        notes_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        notes_text = tk.Text(notes_frame, height=4, wrap="word")
        notes_text.pack(fill="both", expand=True)
        
        # Pre-fill notes
        if order_data.get('notes'):
            notes_text.insert("1.0", order_data['notes'])
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        def save_changes(): 
            try:
                # Parse dates
                order_date = None
                expected_date = None
                actual_date = None
                
                if order_entry.get().strip():
                    order_date = datetime.strptime(order_entry.get().strip(), "%m/%d/%Y")
                
                if expected_entry.get().strip():
                    expected_date = datetime.strptime(expected_entry.get().strip(), "%m/%d/%Y")
                
                if actual_entry.get().strip():
                    actual_date = datetime.strptime(actual_entry.get().strip(), "%m/%d/%Y")
                
                # Get notes and convert empty string to None for clearing
                notes_content = notes_text.get("1.0", tk.END).strip()
                notes_value = notes_content if notes_content else None
                
                # Update order with enhanced method
                success = self.db.update_pipe_order_enhanced(
                    order_id=order_id,
                    status=status_var.get(),
                    supplier=supplier_entry.get().strip(),
                    order_date=order_date,
                    expected_delivery_date=expected_date,
                    actual_delivery_date=actual_date,
                    notes=notes_value  # Changed from .strip() to notes_value
                )
                
                if success:
                    edit_window.destroy()
                    self.refresh_pipe_orders()
                    self.calculate_project_pipe_totals()
                    
                    # Refresh breakdown if this order is selected
                    if self.pipe_orders_tree.selection():
                        current_order = self.pipe_orders_tree.item(self.pipe_orders_tree.selection()[0], "values")[0]
                        if current_order == order_number:
                            self.load_order_breakdown(order_number)
                    
                    self.show_status_toast("Order updated successfully")
                else:
                    Messagebox.show_error("Failed to update order", "Error")
            
            except ValueError as e:
                Messagebox.show_error("Invalid date format. Please use MM/DD/YYYY", "Date Error")

    def show_status_toast(self, message, duration=2000):
        """Show a brief status toast notification"""
        try:
            # Create toast window
            toast = ttk.Toplevel(self.root)
            toast.overrideredirect(True)  # No window decorations
            toast.attributes('-topmost', True)  # Stay on top
            
            # Calculation that accounts for window borders and taskbar
            # Get the actual visible area of the main window
            main_x = self.root.winfo_x()
            main_y = self.root.winfo_y()
            main_width = self.root.winfo_width()
            main_height = self.root.winfo_height()
            
            # Toast dimensions and positioning
            toast_width = 320
            toast_height = 80
            
            # Position at bottom right with proper margins
            x = main_x + main_width - toast_width - 20  # 20px margin from right edge
            y = main_y + main_height - toast_height - 60  # 60px margin from bottom (accounts for taskbar)
            
            toast.geometry(f"{toast_width}x{toast_height}+{x}+{y}")
            
            # Styling and layout for the toast content
            toast_frame = ttk.Frame(toast, padding=10, bootstyle="success")
            toast_frame.pack(fill="both", expand=True)
            
            # Text wrapping and sizing
            message_label = ttk.Label(
                toast_frame,
                text=message,
                font=("Helvetica", 10),
                bootstyle="success-inverse",  # White text on success background
                wraplength=280,  # Proper wrap length for the toast width
                justify="center"
            )
            message_label.pack(expand=True)
            
            # Ensure the toast updates and displays properly
            toast.update_idletasks()
            
            # Add fade-in effect
            toast.attributes('-alpha', 0.0)
            toast.update()
            
            def fade_in():
                current_alpha = toast.attributes('-alpha')
                if current_alpha < 0.9:
                    toast.attributes('-alpha', current_alpha + 0.1)
                    toast.after(50, fade_in)
            
            fade_in()
            
            # Auto-close with fade-out
            def fade_out_and_destroy():
                try:
                    def fade_out():
                        current_alpha = toast.attributes('-alpha')
                        if current_alpha > 0.1:
                            toast.attributes('-alpha', current_alpha - 0.1)
                            toast.after(50, fade_out)
                        else:
                            toast.destroy()
                    fade_out()
                except:
                    # If toast is already destroyed, ignore the error
                    pass
            
            # Auto-close after specified duration
            toast.after(duration, fade_out_and_destroy)
            
        except Exception as e:
            # Fallback logging
            self.logger.info(f"Status: {message}")
            print(f"Status: {message}")

    def check_and_update_order_status(self, order_id: int):
        """Check and update the parent order status based on its items' delivery statuses."""
        try:
            # Get all items for the order
            order_items = self.db.get_pipe_order_items(order_id)
            if not order_items:
                return  # No items, nothing to do

            # Get order details to check current status
            order_details = self.db.get_pipe_order_details(order_id)
            if not order_details:
                return

            order_number = order_details.get('order_number', f"ID {order_id}")

            # Check if all items are delivered
            all_delivered = all(item.get('status', '').lower() == 'delivered' for item in order_items)

            if all_delivered:
                # If all items are delivered and order is not already marked as delivered
                if order_details and order_details.get('status') != 'delivered':
                    self.logger.info(f"All items for order {order_number} are delivered. Updating order status.")
                    
                    # Update the order status to 'delivered'
                    success = self.db.update_pipe_order_status(
                        order_id,
                        status='delivered',
                        delivery_date=datetime.now(),
                        notes=f"Auto-updated: all items delivered as of {datetime.now().strftime('%Y-%m-%d')}"
                    )
                    if success:
                        self.refresh_pipe_orders()
                        self.show_status_toast(f"Order '{order_number}' completed!")
            else:
                # If not all items are delivered, but the order is marked as 'delivered'
                if order_details.get('status') == 'delivered':
                    self.logger.info(f"Order {order_number} is no longer fully delivered. Reverting status.")
                    
                    # Revert status to 'ordered' and clear delivery date
                    success = self.db.update_pipe_order_status(
                        order_id,
                        status='ordered',
                        delivery_date=None,
                        notes=f"Auto-updated: status reverted from 'delivered' on {datetime.now().strftime('%Y-%m-%d')}"
                    )
                    if success:
                        self.refresh_pipe_orders()
                        self.show_status_toast(f"Order '{order_number}' status reverted.")

        except Exception as e:
            self.logger.error(f"Error checking and updating order status for order ID {order_id}: {e}", exc_info=True)

    def quick_mark_pipe_item_delivered(self, item_id: int, structure_id: str):
        """Quickly mark a pipe item as fully delivered"""
        try:
            # Get item details to determine full length
            project = self.db.get_project_by_name(self.current_project, self.current_user.id)
            if not project:
                return
            
            # Get current order
            if not self.pipe_orders_tree.selection():
                return
            
            order_number = self.pipe_orders_tree.item(self.pipe_orders_tree.selection()[0], "values")[0]
            pipe_orders = self.db.get_pipe_orders(project.id)
            order_id = None
            
            for order in pipe_orders:
                if order.get('order_number') == order_number:
                    order_id = order.get('id')
                    break
            
            if not order_id:
                return
            
            # Get item details
            order_items = self.db.get_pipe_order_items(order_id)
            item_data = None
            
            for item in order_items:
                if item['id'] == item_id:
                    item_data = item
                    break
            
            if not item_data:
                Messagebox.show_error("Could not find pipe item details", "Error")
                return
            
            total_length = item_data.get('length', 0)
            
            # Update pipe item as fully delivered
            success = self.db.update_pipe_item_delivery(
                item_id=item_id,
                delivered_length=total_length,
                status="delivered",
                notes=f"Quick delivery - {total_length:.2f} ft delivered"
            )
            
            if success:
                self.show_status_toast(f"Marked {total_length:.2f} ft as delivered for structure {structure_id}")
                # Refresh breakdown view
                if self.pipe_orders_tree.selection():
                    order_number = self.pipe_orders_tree.item(self.pipe_orders_tree.selection()[0], "values")[0]
                    self.load_order_breakdown(order_number)
                
                # Refresh project totals
                self.calculate_project_pipe_totals()
                
                # Check if this completes the order
                if order_id:
                    self.check_and_update_order_status(order_id)
            else:
                Messagebox.show_error("Failed to update delivery", "Error")
                
        except Exception as e:
            self.logger.error(f"Error quick marking pipe as delivered: {e}", exc_info=True)
            Messagebox.show_error(f"An error occurred: {str(e)}", "Error")

    def mark_pipe_item_not_delivered(self, item_id: int, structure_id: str):
        """Mark a pipe item as not delivered"""
        try:
            # Confirm action
            confirm = Messagebox.yesno(
                f"Mark pipe for structure {structure_id} as NOT delivered?\n\nThis will reset the delivery status.",
                "Confirm Status Change"
            )
            
            if not confirm:
                return
            
            # Mark as not delivered
            success = self.db.update_pipe_item_delivery(
                item_id=item_id,
                delivered_length=0,
                status="pending",
                notes=None
            )
            
            if success:
                # Get current order for refresh
                if self.pipe_orders_tree.selection():
                    order_number = self.pipe_orders_tree.item(self.pipe_orders_tree.selection()[0], "values")[0]
                    self.load_order_breakdown(order_number)
                
                self.calculate_project_pipe_totals()
                self.show_status_toast(f"Pipe for {structure_id} marked as not delivered")
            else:
                Messagebox.show_error("Failed to update delivery status", "Error")
                
        except Exception as e:
            self.logger.error(f"Error marking pipe item not delivered: {e}", exc_info=True)
            Messagebox.show_error(f"An error occurred: {str(e)}", "Error")

    def complete_partial_delivery(self, item_id: int, structure_id: str):
        """Complete a partial delivery (mark remaining as delivered)"""
        try:
            # Get item details
            project = self.db.get_project_by_name(self.current_project, self.current_user.id)
            if not project:
                return
            
            # Get current order
            if not self.pipe_orders_tree.selection():
                return
            
            order_number = self.pipe_orders_tree.item(self.pipe_orders_tree.selection()[0], "values")[0]
            pipe_orders = self.db.get_pipe_orders(project.id)
            order_id = None
            
            for order in pipe_orders:
                if order.get('order_number') == order_number:
                    order_id = order.get('id')
                    break
            
            if not order_id:
                return
            
            # Get item details
            order_items = self.db.get_pipe_order_items(order_id)
            item_data = None
            
            for item in order_items:
                if item['id'] == item_id:
                    item_data = item
                    break
            
            if not item_data:
                return
            
            current_delivered = item_data.get('delivered_length', 0)
            total_length = item_data['length']
            remaining = total_length - current_delivered
            
            if remaining <= 0:
                self.show_status_toast("No remaining pipe to deliver")
                return
            
            # Confirm completion
            confirm = Messagebox.yesno(
                f"Complete delivery for structure {structure_id}?\n\n"
                f"Total Length: {total_length:.2f} ft\n"
                f"Already Delivered: {current_delivered:.2f} ft\n"
                f"Remaining: {remaining:.2f} ft\n\n"
                f"This will mark the remaining {remaining:.2f} ft as delivered.",
                "Confirm Completion"
            )
            
            if confirm == "Yes":
                # Update the delivery to complete
                success = self.db.update_pipe_item_delivery(
                    item_id=item_id,
                    delivered_length=total_length,  # Mark as fully delivered
                    status="delivered",
                    notes=f"Completed delivery - {remaining:.2f} ft remaining marked as delivered"
                )
                
                if success:
                    self.show_status_toast(f"Completed delivery for structure {structure_id}")
                    # Refresh the breakdown view
                    if self.pipe_orders_tree.selection():
                        order_number = self.pipe_orders_tree.item(self.pipe_orders_tree.selection()[0], "values")[0]
                        self.load_order_breakdown(order_number)

                    # Refresh project totals
                    self.calculate_project_pipe_totals()
                    
                    # Check if this completes the order
                    self.check_and_update_order_status(order_id)
                else:
                    Messagebox.show_error("Failed to update delivery", "Error")
                    
        except Exception as e:
            self.logger.error(f"Error completing partial delivery: {e}", exc_info=True)
            Messagebox.show_error(f"An error occurred: {str(e)}", "Error")

    def show_partial_delivery_dialog(self, item_id: int, structure_id: str):
        """Show dialog for partial delivery entry"""
        try:
            # Get item details
            project = self.db.get_project_by_name(self.current_project, self.current_user.id)
            if not project:
                return
            
            # Get current order and item data
            if not self.pipe_orders_tree.selection():
                return
            
            order_number = self.pipe_orders_tree.item(self.pipe_orders_tree.selection()[0], "values")[0]
            pipe_orders = self.db.get_pipe_orders(project.id)
            order_id = None
            
            for order in pipe_orders:
                if order.get('order_number') == order_number:
                    order_id = order.get('id')
                    break
            
            if not order_id:
                return
            
            # Get item details
            order_items = self.db.get_pipe_order_items(order_id)
            item_data = None
            
            for item in order_items:
                if item['id'] == item_id:
                    item_data = item
                    break
            
            if not item_data:
                return
            
            total_length = item_data['length']
            current_delivered = item_data.get('delivered_length', 0)
            pipe_type = item_data['pipe_type']
            
            # Create partial delivery dialog
            delivery_window = ttk.Toplevel(self.root)
            delivery_window.title("Partial Delivery")
            delivery_window.geometry("450x500")
            self.center_toplevel(delivery_window)
            delivery_window.transient(self.root)
            delivery_window.grab_set()
            
            # Main container
            main_frame = ttk.Frame(delivery_window, padding=20)
            main_frame.pack(fill="both", expand=True)
            
            # Title
            ttk.Label(
                main_frame,
                text="Record Partial Delivery",
                font=("Helvetica", 14, "bold"),
                bootstyle="primary"
            ).pack(pady=(0, 20))
            
            # Item info
            info_frame = ttk.Labelframe(main_frame, text="Pipe Item Details", padding=10)
            info_frame.pack(fill="x", pady=(0, 20))
            
            ttk.Label(info_frame, text=f"Structure: {structure_id}", font=("Helvetica", 10, "bold")).pack(anchor="w")
            ttk.Label(info_frame, text=f"Pipe Type: {pipe_type}").pack(anchor="w")
            ttk.Label(info_frame, text=f"Total Ordered: {total_length:.2f} ft").pack(anchor="w")
            ttk.Label(info_frame, text=f"Already Delivered: {current_delivered:.2f} ft").pack(anchor="w")
            ttk.Label(info_frame, text=f"Remaining: {total_length - current_delivered:.2f} ft").pack(anchor="w")
            
            # Delivery input section
            delivery_frame = ttk.Labelframe(main_frame, text="New Delivery", padding=10)
            delivery_frame.pack(fill="x", pady=(0, 20))
            delivery_frame.columnconfigure(1, weight=1)
            
            # Delivered length
            ttk.Label(delivery_frame, text="Length Delivered (ft):").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
            delivered_length_entry = ttk.Entry(delivery_frame)
            delivered_length_entry.grid(row=0, column=1, sticky="ew", pady=5)
            
            # Quick buttons for common amounts
            quick_frame = ttk.Frame(delivery_frame)
            quick_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
            
            ttk.Label(quick_frame, text="Quick Fill:", font=("Helvetica", 9)).pack(anchor="w")
            
            quick_buttons_frame = ttk.Frame(quick_frame)
            quick_buttons_frame.pack(fill="x", pady=(5, 0))
            
            remaining = total_length - current_delivered
            
            def set_remaining():
                delivered_length_entry.delete(0, tk.END)
                delivered_length_entry.insert(0, str(remaining))
            
            def set_half():
                delivered_length_entry.delete(0, tk.END)
                delivered_length_entry.insert(0, str(remaining / 2))
            
            ttk.Button(
                quick_buttons_frame,
                text="All Remaining",
                bootstyle="info-outline",
                command=set_remaining
            ).pack(side="left", padx=2)
            
            ttk.Button(
                quick_buttons_frame,
                text="Half Remaining",
                bootstyle="info-outline",
                command=set_half
            ).pack(side="left", padx=2)
            
            # Delivery date
            ttk.Label(delivery_frame, text="Delivery Date:").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=(15, 5))
            date_frame = ttk.Frame(delivery_frame)
            date_frame.grid(row=2, column=1, sticky="ew", pady=(15, 5))
            date_frame.columnconfigure(0, weight=1)
            
            delivery_date_entry = ttk.Entry(date_frame)
            delivery_date_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
            delivery_date_entry.insert(0, datetime.now().strftime("%m/%d/%Y"))
            
            ttk.Button(
                date_frame,
                text="📅",
                width=3,
                command=lambda: self.open_date_picker(delivery_date_entry)
            ).pack(side="right")
            
            # Notes
            ttk.Label(delivery_frame, text="Delivery Notes:").grid(row=3, column=0, sticky="nw", padx=(0, 10), pady=(15, 5))
            notes_text = tk.Text(delivery_frame, height=3, wrap="word")
            notes_text.grid(row=3, column=1, sticky="ew", pady=(15, 5))
            
            def save_partial_delivery():
                try:
                    delivered_length_str = delivered_length_entry.get().strip()
                    delivery_date_str = delivery_date_entry.get().strip()
                    notes = notes_text.get("1.0", tk.END).strip()
                    
                    # Validation
                    if not delivered_length_str:
                        Messagebox.show_error("Please enter delivered length", "Validation Error")
                        return
                    
                    try:
                        new_delivered = float(delivered_length_str)
                    except ValueError:
                        Messagebox.show_error("Invalid length value", "Validation Error")
                        return
                    
                    if new_delivered <= 0:
                        Messagebox.show_error("Delivered length must be greater than 0", "Validation Error")
                        return
                    
                    # Calculate total delivered
                    total_delivered = current_delivered + new_delivered
                    
                    if total_delivered > total_length:
                        Messagebox.show_error(
                            f"Total delivered ({total_delivered:.2f} ft) cannot exceed ordered length ({total_length:.2f} ft)",
                            "Validation Error"
                        )
                        return
                    
                    # Parse delivery date
                    try:
                        delivery_date = datetime.strptime(delivery_date_str, "%m/%d/%Y") if delivery_date_str else datetime.now()
                    except ValueError:
                        Messagebox.show_error("Invalid date format. Please use MM/DD/YYYY", "Date Error")
                        return
                    
                    # Determine status
                    if total_delivered >= total_length:
                        status = "delivered"
                    else:
                        status = "partial"
                    
                    # Add delivery date and amount to notes
                    enhanced_notes = f"Partial delivery on {delivery_date.strftime('%m/%d/%Y')}: {new_delivered:.2f} ft"
                    if notes:
                        enhanced_notes += f"\nNotes: {notes}"
                    
                    # Update pipe item
                    success = self.db.update_pipe_item_delivery(
                        item_id=item_id,
                        delivered_length=total_delivered,
                        status=status,
                        notes=enhanced_notes
                    )
                    
                    if success:
                        delivery_window.destroy()
                        self.load_order_breakdown(order_number)
                        self.calculate_project_pipe_totals()
                        self.show_status_toast(f"Partial delivery recorded for {structure_id}")
                    else:
                        Messagebox.show_error("Failed to record partial delivery", "Error")
                        
                except Exception as e:
                    self.logger.error(f"Error recording partial delivery: {e}", exc_info=True)
                    Messagebox.show_error(f"An error occurred: {str(e)}", "Error")
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill="x")
            
            ttk.Button(
                button_frame,
                text="Record Delivery",
                bootstyle="primary",
                command=save_partial_delivery
            ).pack(side="left", padx=5)
            
            ttk.Button(
                button_frame,
                text="Cancel",
                bootstyle="secondary",
                command=delivery_window.destroy
            ).pack(side="right", padx=5)
            
            # Focus on the length entry
            delivered_length_entry.focus()
            
        except Exception as e:
            self.logger.error(f"Error showing partial delivery dialog: {e}", exc_info=True)
            Messagebox.show_error(f"An error occurred: {str(e)}", "Error")

    def on_notebook_tab_changed(self, event):
        """Handle notebook tab changes to refresh data when switching to component tracking"""
        selected_tab = event.widget.tab('current')['text']
        print(f"DEBUG: Switched to tab: {selected_tab}")
        
        if selected_tab == 'Component Tracking':
            print("DEBUG: Component Tracking tab selected, refreshing data")
            # Small delay to ensure UI is ready
            self.root.after(100, self.load_structures_for_components)

    def load_structures_for_components(self):
        """Load structures into the component tracking tab with status calculation and auto-base addition"""
        
        # Clear existing items
        for item in self.component_structure_tree.get_children():
            self.component_structure_tree.delete(item)
        
        # Get project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            print("DEBUG: No project found")
            return
        
        print(f"DEBUG: Found project {project.name} with ID {project.id}")
        
        # Get structures for this project
        structures = self.db.get_all_structures(project.id)
        
        # Debug: Check if we have structures
        print(f"DEBUG: Found {len(structures)} structures for project {self.current_project}")
        
        if not structures:
            print("DEBUG: No structures found, returning early")
            return
        
        # Pipe Totals Calculation
        pipe_totals = {}
        structures_with_pipe = [s for s in structures if s.pipe_length and s.pipe_diameter and s.pipe_type]
        
        if structures_with_pipe:
            for structure in structures_with_pipe:
                # Create key for grouping by type and diameter
                key = f"{structure.pipe_type}_{int(structure.pipe_diameter) if structure.pipe_diameter is not None else 'unknown'}"
                
                if key not in pipe_totals:
                    pipe_totals[key] = {
                        'pipe_type': structure.pipe_type,
                        'diameter': structure.pipe_diameter,
                        'total_length': 0,
                        'structures': []
                    }
                
                pipe_totals[key]['total_length'] += structure.pipe_length
                pipe_totals[key]['structures'].append(structure.structure_id)

        # Delivered Pipe Calculation
        total_delivered_length = 0
        pipe_orders = self.db.get_pipe_orders(project.id)
        for order in pipe_orders:
            order_items = self.db.get_pipe_order_items(order.get('id'))
            for item in order_items:
                delivered_length = item.get('delivered_length', 0)
                pipe_type = item.get('pipe_type', '')
                diameter = item.get('diameter', 0)
                
                key = f"{pipe_type}_{int(diameter) if diameter is not None else 'unknown'}"
                if key in pipe_totals:
                    # Add delivered length to our totals dictionary
                    pipe_totals[key]['delivered_length'] = pipe_totals[key].get('delivered_length', 0) + delivered_length
                total_delivered_length += delivered_length
        
        # Ensure all structures have base components (safety check)
        if structures:
            missing_bases = self.ensure_all_structures_have_bases(project.id, structures)
            if missing_bases > 0:
                self.logger.info(f"Auto-added {missing_bases} missing base components during component view load")
        
        # Add structures with status calculation
        for structure in structures:
            try:
                status_info = self.calculate_structure_component_status(structure.structure_id, project.id)
                
                # Determine status tag with new approved logic
                if status_info['total'] == 0:
                    tag = "not_started"
                    status_text = "Not Started"
                elif status_info['installed'] == status_info['total']:
                    tag = "installed"
                    status_text = "Installed"
                elif status_info['delivered'] == status_info['total']:
                    tag = "delivered"
                    status_text = "Delivered"
                elif status_info['approved'] == status_info['total']:
                    tag = "approved"
                    status_text = "Approved"
                elif status_info['delivered'] + status_info['installed'] > 0:
                    tag = "in_progress"
                    status_text = "In Progress"
                else:
                    tag = "incomplete"
                    status_text = "Incomplete"
                
                progress_text = f"{status_info['delivered'] + status_info['installed']}/{status_info['total']}"
                
                # Insert into treeview
                item = self.component_structure_tree.insert(
                    "", 
                    "end", 
                    values=(structure.structure_id, structure.structure_type, status_text, progress_text),
                    tags=(tag,)
                )
                
            except Exception as e:
                import traceback
                traceback.print_exc()
        
        # Debug: Check final count
        children = self.component_structure_tree.get_children()
        print(f"DEBUG: Component tree now has {len(children)} items")
        for child in children:
            values = self.component_structure_tree.item(child, "values")
        #    print(f"DEBUG: Tree item: {values}")

    def calculate_structure_component_status(self, structure_id: str, project_id: int) -> dict:
        """Calculate component status for a structure"""
        try:
            components = self.db.get_structure_components(structure_id, project_id)
            
            status_counts = {
                'total': len(components),
                'pending': 0,
                'ordered': 0,
                'approved': 0,
                'delivered': 0,
                'installed': 0
            }
            
            for component in components:
                status = component.status.lower() if component.status else 'pending'
                if status in status_counts:
                    status_counts[status] += 1
                else:
                    # If status is unknown, count as pending
                    status_counts['pending'] += 1
            
            return status_counts
            
        except Exception as e:
            return {
                'total': 0,
                'pending': 0,
                'ordered': 0,
                'approved': 0,
                'delivered': 0,
                'installed': 0
            }

    def on_structure_selected(self, event):
        """Handle structure selection in component tracking"""
        selection = self.component_structure_tree.selection()
        if not selection:
            self.selected_structure_label.config(text="None")
            self.clear_component_view()
            return
        
        structure_id = self.component_structure_tree.item(selection[0], "values")[0]
        structure_type = self.component_structure_tree.item(selection[0], "values")[1]
                
        # Update selected structure label
        self.selected_structure_label.config(text=f"{structure_id} ({structure_type})")
        
        # Load components for this structure
        self.load_structure_components_enhanced(structure_id)

    def load_structure_components_enhanced(self, structure_id: str):
        """Load components for the selected structure with enhanced display and proper date format"""
        
        # Clear existing components
        for item in self.component_tree.get_children():
            self.component_tree.delete(item)
        
        # Get project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            return
        
        # Get components for this structure - USE ENHANCED METHOD
        components = self.db.get_structure_components_with_dates(structure_id, project.id)
        
        if not components:
            # Add a message indicating no components
            self.component_tree.insert(
                "",
                "end",
                values=("No components found", "—", "—", "—", "—", "Click 'Add Component' to add components"),
                tags=("no_components",)
            )
            return
        
        # Add components to treeview with enhanced formatting
        for i, component in enumerate(components):
            
            # Format dates for display 
            order_date = component.order_date.strftime("%m/%d/%Y") if component.order_date else "—"
            expected_date = component.expected_delivery_date.strftime("%m/%d/%Y") if component.expected_delivery_date else "—"
            delivery_date = component.actual_delivery_date.strftime("%m/%d/%Y") if component.actual_delivery_date else "—"
            
            # Get status tag for color coding
            status_tag = component.status.lower() if component.status else "pending"
            
            item_id = self.component_tree.insert(
                "",
                "end",
                values=(
                    component.component_type_name,
                    component.status.title(),
                    order_date,
                    expected_date,
                    delivery_date,
                    component.notes or ""
                ),
                tags=(str(component.id), status_tag)  # Store ID and status as tags
            )

    def clear_component_view(self):
        """Clear the component view when no structure is selected"""
        for item in self.component_tree.get_children():
            self.component_tree.delete(item)

    def auto_add_base_components(self):
        """Manually add base components to structures missing them (backup function)"""
        # Get project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            return
        
        # Get all structures
        structures = self.db.get_all_structures(project.id)
        
        added_count = self.ensure_all_structures_have_bases(project.id, structures)
        
        if added_count > 0:
            Messagebox.show_info(f"Added base components to {added_count} structures", "Success")
            self.refresh_component_status()
        else:
            Messagebox.show_info("All structures already have base components", "No Changes")    

    def ensure_all_structures_have_bases(self, project_id: int, structures: list = None) -> int:
        """Ensure all structures have base components - called automatically when needed"""
        if structures is None:
            structures = self.db.get_all_structures(project_id)
        
        # Get base component type
        component_types = self.db.get_all_component_types()
        base_type = None
        for ct in component_types:
            if ct.name.lower() == "base":
                base_type = ct
                break
        
        if not base_type:
            self.logger.warning("Base component type not found - cannot auto-add base components")
            return 0
        
        added_count = 0
        
        for structure in structures:
            # Check if structure already has a base component
            existing_components = self.db.get_structure_components(structure.structure_id, project_id)
            has_base = any(comp.component_type_name.lower() == "base" for comp in existing_components)
            
            if not has_base:
                # Add base component automatically
                component = StructureComponent(
                    structure_id=structure.structure_id,
                    component_type_id=base_type.id,
                    status="pending",
                    project_id=project_id
                )
                
                if self.db.add_structure_component(component, project_id):
                    added_count += 1
                    self.logger.info(f"Auto-added base component to structure {structure.structure_id}")
        
        return added_count

    def auto_add_base_to_new_structure(self, structure_id: str, project_id: int):
        """Automatically add base component when a new structure is created"""
        # Get base component type
        component_types = self.db.get_all_component_types()
        base_type = None
        for ct in component_types:
            if ct.name.lower() == "base":
                base_type = ct
                break
        
        if not base_type:
            self.logger.warning(f"Base component type not found - cannot auto-add base to structure {structure_id}")
            return False
        
        # Add base component
        component = StructureComponent(
            structure_id=structure_id,
            component_type_id=base_type.id,
            status="pending",
            project_id=project_id
        )
        
        success = self.db.add_structure_component(component, project_id)
        if success:
            self.logger.info(f"Auto-added base component to new structure {structure_id}")
        else:
            self.logger.error(f"Failed to auto-add base component to structure {structure_id}")
        
        return success

    def quick_add_riser(self):
        """Quickly add a riser component to the selected structure without dialog"""
        selection = self.component_structure_tree.selection()
        if not selection:
            Messagebox.show_warning("Please select a structure first", "No Structure Selected")
            return
        
        structure_id = self.component_structure_tree.item(selection[0], "values")[0]
        structure_type = self.component_structure_tree.item(selection[0], "values")[1]
        
        # Get project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            return
        
        # Check if structure already has a riser
        existing_components = self.db.get_structure_components(structure_id, project.id)
        has_riser = any(comp.component_type_name.lower() == "riser" for comp in existing_components)
        
        if has_riser:
            Messagebox.show_info("This structure already has a riser component", "Already Exists")
            return
        
        # Get riser component type
        component_types = self.db.get_all_component_types()
        riser_type = None
        for ct in component_types:
            if ct.name.lower() == "riser":
                riser_type = ct
                break
        
        if not riser_type:
            Messagebox.show_error("Riser component type not found", "Missing Component Type")
            return
        
        # Add riser component with pending status
        component = StructureComponent(
            structure_id=structure_id,
            component_type_id=riser_type.id,
            status="pending",
            project_id=project.id
        )
        
        if self.db.add_structure_component(component, project.id):
            # Silently refresh views without success dialog
            self.load_structure_components_enhanced(structure_id)
            self.refresh_component_status()
        else:
            Messagebox.show_error("Failed to add riser component", "Error")

    def quick_add_lid(self):
        """Quickly add a lid component to the selected structure without dialog"""
        selection = self.component_structure_tree.selection()
        if not selection:
            Messagebox.show_warning("Please select a structure first", "No Structure Selected")
            return
        
        structure_id = self.component_structure_tree.item(selection[0], "values")[0]
        structure_type = self.component_structure_tree.item(selection[0], "values")[1]
        
        # Get project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            return
        
        # Check if structure already has a lid
        existing_components = self.db.get_structure_components(structure_id, project.id)
        has_lid = any(comp.component_type_name.lower() == "lid" for comp in existing_components)
        
        if has_lid:
            Messagebox.show_info("This structure already has a lid component", "Already Exists")
            return
        
        # Get lid component type
        component_types = self.db.get_all_component_types()
        lid_type = None
        for ct in component_types:
            if ct.name.lower() == "lid":
                lid_type = ct
                break
        
        if not lid_type:
            Messagebox.show_error("Lid component type not found", "Missing Component Type")
            return
        
        # Add lid component with pending status
        component = StructureComponent(
            structure_id=structure_id,
            component_type_id=lid_type.id,
            status="pending",
            project_id=project.id
        )
        
        if self.db.add_structure_component(component, project.id):
            # Silently refresh views without success dialog
            self.load_structure_components_enhanced(structure_id)
            self.refresh_component_status()
        else:
            Messagebox.show_error("Failed to add lid component", "Error")

    def show_component_context_menu(self, event):
        """Show right-click context menu for component management"""
        # Get the item under the cursor
        item = self.component_tree.identify_row(event.y)
        if not item:
            return
        
        # Select the item
        self.component_tree.selection_set(item)
        
        # Get component details
        values = self.component_tree.item(item, "values")
        if not values or values[0] == "No components found":
            return
        
        component_type = values[0]
        current_status = values[1].lower()
        
        # Create context menu
        context_menu = tk.Menu(self.root, tearoff=0)
        
        # Update Status submenu
        status_menu = tk.Menu(context_menu, tearoff=0)
        context_menu.add_cascade(label="Update Status", menu=status_menu)
        
        statuses = ["pending", "ordered", "approved", "delivered", "installed"]
        for status in statuses:
            if status != current_status:
                status_menu.add_command(
                    label=status.title(),
                    command=lambda s=status: self.quick_update_component_status(s)
                )
        
        context_menu.add_separator()
        context_menu.add_command(label="Edit Details", command=self.update_component_status)
        context_menu.add_separator()
        context_menu.add_command(label="Delete Component", command=self.delete_component_from_context)
        
        # Show the menu
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def show_structure_component_context_menu(self, event):
        """Show right-click context menu for the structure list in the component tab."""
        # Get the item under the cursor
        item = self.component_structure_tree.identify_row(event.y)
        if not item:
            return

        # Select the item
        self.component_structure_tree.selection_set(item)

        # Get structure details
        values = self.component_structure_tree.item(item, "values")
        if not values:
            return

        structure_id = values[0]
        current_status = values[2].lower()

        # Create context menu
        context_menu = tk.Menu(self.root, tearoff=0)

        # Update Status submenu
        status_menu = tk.Menu(context_menu, tearoff=0)
        context_menu.add_cascade(label="Bulk Update All Components", menu=status_menu)

        statuses = ["pending", "ordered", "approved", "delivered", "installed"]
        for status in statuses:
            status_menu.add_command(
                label=status.title(),
                command=lambda s=status, sid=structure_id: self.bulk_update_structure_components_status(sid, s)
            )

        # Show the menu
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def bulk_update_structure_components_status(self, structure_id: str, new_status: str):
        """Update the status for all components of a given structure."""
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            Messagebox.show_error("Could not find current project.", "Project Error")
            return

        components = self.db.get_structure_components(structure_id, project.id)
        if not components:
            Messagebox.show_info(f"No components found for structure {structure_id} to update.", "No Components")
            return

        # Removed confirmation dialog / Un-Comment if necessary
        #confirm = Messagebox.yesno(
        #    f"Are you sure you want to set all {len(components)} components for structure '{structure_id}' to '{new_status.title()}'?",
        #    "Confirm Bulk Update"
        #)
        #if not confirm:
        #    return

        date_to_set = datetime.now() if new_status in ["ordered", "delivered", "installed"] else None

        for component in components:
            self.db.update_component_status(component.id, new_status, None, date_to_set)

        self.show_status_toast(f"Updated {len(components)} components for {structure_id}.")
        self.refresh_component_status()
        self.load_structure_components_enhanced(structure_id)


    def show_structure_context_menu(self, event):
        """Show right-click context menu for structure management and pipe ordering"""
        # Get selected structures
        selected_items = self.structure_tree.selection()
        if not selected_items:
            return
        
        # Filter out separator rows and get valid structure IDs
        valid_structures = []
        for item in selected_items:
            values = self.structure_tree.item(item, "values")
            if values and values[0] and "─── Run" not in values[0] and values[0].strip():
                valid_structures.append(item)
        
        if not valid_structures:
            return
        
        # Create context menu
        context_menu = tk.Menu(self.root, tearoff=0)
        
        if len(valid_structures) == 1:
            context_menu.add_command(
                label="View Details",
                command=lambda: self.show_structure_details(None)
            )
            context_menu.add_separator()
        
        # Pipe ordering options
        pipe_menu = tk.Menu(context_menu, tearoff=0)
        context_menu.add_cascade(label="Pipe Management", menu=pipe_menu)
        
        pipe_menu.add_command(
            label="Calculate Pipe Totals",
            command=lambda: self.calculate_pipe_totals_for_selection(valid_structures)
        )
        
        pipe_menu.add_command(
            label="Order Pipe",
            command=lambda: self.order_pipe_for_selection(valid_structures)
        )
        
        pipe_menu.add_command(
            label="View Pipe Details",
            command=lambda: self.view_pipe_details_for_selection(valid_structures)
        )
        
        context_menu.add_separator()
        
        # NEW: Structure ordering option
        context_menu.add_command(
            label=f"Order Structures ({len(valid_structures)} selected)",
            command=lambda: self.order_structures_for_selection(valid_structures)
        )
        
        context_menu.add_separator()
        
        # Group operations
        if len(valid_structures) > 1:
            context_menu.add_command(
                label=f"Create Group ({len(valid_structures)} structures)",
                command=self.create_group
            )
        
        # Show the menu
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def order_structures_for_selection(self, selected_items):
        """Create structure orders for selected structures - marks all components as ordered"""
        # Get project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            return
        
        # Extract structure data from selected items and get their components
        structures_data = []
        total_components = 0
        
        for item in selected_items:
            values = self.structure_tree.item(item, "values")
            if values and values[0] and "─── Run" not in values[0]:
                structure_id = values[0]
                # Get full structure details from database
                structure = self.db.get_structure(structure_id, project.id)
                if structure:
                    # Get components for this structure using your existing method
                    components = self.db.get_structure_components(structure_id, project.id)
                    # Filter for components that can be ordered (pending or approved)
                    orderable_components = [c for c in components if c.status in ['pending', 'approved']]
                    
                    if orderable_components:
                        structures_data.append({
                            'structure': structure,
                            'components': orderable_components
                        })
                        total_components += len(orderable_components)
        
        if not structures_data:
            Messagebox.show_info("No structures with pending or approved components found in selection", "No Components to Order")
            return
        
        # Create order dialog
        order_window = ttk.Toplevel(self.root)
        order_window.title("Order Structures")
        order_window.geometry("700x800")
        self.center_toplevel(order_window)
        order_window.transient(self.root)
        order_window.grab_set()
        
        # Main container
        main_frame = ttk.Frame(order_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(
            main_frame, 
            text="Order Structures", 
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        ).pack(pady=(0, 20))
        
        # Summary
        summary_text = f"Ordering {len(structures_data)} structures with {total_components} total components"
        ttk.Label(
            main_frame,
            text=summary_text,
            font=("Helvetica", 11),
            bootstyle="info"
        ).pack(pady=(0, 20))
        
        # Order information section
        order_info_frame = ttk.Labelframe(main_frame, text="Order Information", padding=15)
        order_info_frame.pack(fill="x", pady=(0, 20))
        
        # Order number
        ttk.Label(order_info_frame, text="Order Number:").grid(row=0, column=0, sticky="w", pady=5)
        order_number_var = tk.StringVar()
        order_number_entry = ttk.Entry(order_info_frame, textvariable=order_number_var, width=30)
        order_number_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Supplier
        ttk.Label(order_info_frame, text="Supplier:").grid(row=1, column=0, sticky="w", pady=5)
        supplier_var = tk.StringVar()
        supplier_entry = ttk.Entry(order_info_frame, textvariable=supplier_var, width=30)
        supplier_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Order date
        ttk.Label(order_info_frame, text="Order Date (MM/DD/YYYY):").grid(row=2, column=0, sticky="w", pady=5)
        order_date_var = tk.StringVar(value=datetime.now().strftime("%m/%d/%Y"))
        order_date_entry = ttk.Entry(order_info_frame, textvariable=order_date_var, width=30)
        order_date_entry.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Expected delivery date
        ttk.Label(order_info_frame, text="Expected Delivery (MM/DD/YYYY):").grid(row=3, column=0, sticky="w", pady=5)
        expected_date_var = tk.StringVar()
        expected_date_entry = ttk.Entry(order_info_frame, textvariable=expected_date_var, width=30)
        expected_date_entry.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Notes
        ttk.Label(order_info_frame, text="Order Notes:").grid(row=4, column=0, sticky="nw", pady=5)
        notes_text = tk.Text(order_info_frame, height=3, width=30)
        notes_text.grid(row=4, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Configure grid weights
        order_info_frame.columnconfigure(1, weight=1)
        
        # Structure and component details section
        details_frame = ttk.Labelframe(main_frame, text="Structures and Components to Order", padding=15)
        details_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Create scrollable frame for structure details
        canvas = tk.Canvas(details_frame)
        scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add structure details
        for i, struct_data in enumerate(structures_data):
            structure = struct_data['structure']
            components = struct_data['components']
            
            # Structure header
            struct_frame = ttk.Frame(scrollable_frame)
            struct_frame.pack(fill="x", pady=(10 if i > 0 else 0, 5))
            
            ttk.Label(
                struct_frame,
                text=f"Structure: {structure.structure_id}",
                font=("Helvetica", 10, "bold"),
                bootstyle="primary"
            ).pack(anchor="w")
            
            # Component list
            for component in components:
                comp_frame = ttk.Frame(scrollable_frame)
                comp_frame.pack(fill="x", padx=20, pady=1)
                
                ttk.Label(
                    comp_frame,
                    text=f"• {component.component_type_name} (Status: {component.status.title()})",
                    font=("Helvetica", 9)
                ).pack(anchor="w")
        
        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind("<Enter>", _bind_mousewheel)
        canvas.bind("<Leave>", _unbind_mousewheel)
        
        # Create order function
        def create_structure_order():
            # Validate inputs
            if not order_number_var.get().strip():
                Messagebox.show_error("Please enter an order number", "Missing Order Number")
                order_number_entry.focus()
                return
            
            if not supplier_var.get().strip():
                Messagebox.show_error("Please enter a supplier", "Missing Supplier")
                supplier_entry.focus()
                return
            
            # Parse dates
            try:
                order_date = datetime.strptime(order_date_var.get().strip(), "%m/%d/%Y") if order_date_var.get().strip() else datetime.now()
            except ValueError:
                Messagebox.show_error("Invalid order date format. Please use MM/DD/YYYY", "Date Error")
                order_date_entry.focus()
                return
            
            expected_delivery = None
            if expected_date_var.get().strip():
                try:
                    expected_delivery = datetime.strptime(expected_date_var.get().strip(), "%m/%d/%Y")
                except ValueError:
                    Messagebox.show_error("Invalid expected delivery date format. Please use MM/DD/YYYY", "Date Error")
                    expected_date_entry.focus()
                    return
            
            # Get notes
            notes = notes_text.get("1.0", tk.END).strip() or None
            
            # Update all components to ordered status using your existing enhanced method
            updated_count = 0
            failed_count = 0
            
            for struct_data in structures_data:
                for component in struct_data['components']:
                    # Create order notes that include structure and order info
                    component_notes = f"Order #{order_number_var.get().strip()}"
                    if supplier_var.get().strip():
                        component_notes += f" - {supplier_var.get().strip()}"
                    if notes:
                        component_notes += f" - {notes}"
                    
                    # Use your existing enhanced method
                    success = self.db.update_component_status_enhanced(
                        component.id,
                        "ordered",
                        component_notes,
                        order_date,  # order_date
                        expected_delivery,  # expected_delivery_date
                        None  # actual_delivery_date (not delivered yet)
                    )
                    
                    if success:
                        updated_count += 1
                    else:
                        failed_count += 1
            
            # Show results
            if updated_count > 0:
                message = f"Successfully ordered {updated_count} components across {len(structures_data)} structures"
                if failed_count > 0:
                    message += f"\n{failed_count} components failed to update"
                
                Messagebox.show_info(message, "Order Created")
                order_window.destroy()
                
                # Refresh views using your existing methods
                self.load_structures()
                self.refresh_component_status()
                
                # Switch to component tracking tab to see results
                if hasattr(self, 'notebook'):
                    for i in range(self.notebook.index("end")):
                        if self.notebook.tab(i, "text") == "Component Tracking":
                            self.notebook.select(i)
                            break
            else:
                Messagebox.show_error("Failed to update any components", "Order Failed")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(
            button_frame,
            text="Create Order",
            bootstyle="primary",
            command=create_structure_order
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            bootstyle="secondary",
            command=order_window.destroy
        ).pack(side="right", padx=5)
        
        # Focus on order number field
        order_number_entry.focus()

    def calculate_pipe_totals_for_selection(self, selected_items):
        """Calculate pipe totals for selected structures and show in a dialog"""
        # Get project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            return
        
        # Extract structure data from selected items
        structures_data = []
        for item in selected_items:
            values = self.structure_tree.item(item, "values")
            if values and values[0] and "─── Run" not in values[0]:
                structure_id = values[0]
                # Get full structure details from database
                structure = self.db.get_structure(structure_id, project.id)
                if structure and structure.pipe_length and structure.pipe_diameter and structure.pipe_type:
                    structures_data.append(structure)
        
        if not structures_data:
            Messagebox.show_info("No structures with pipe data found in selection", "No Pipe Data")
            return
        
        # Calculate totals by pipe type and diameter
        pipe_totals = {}
        
        for structure in structures_data:
            # Create key for grouping
            key = f"{structure.pipe_type} - {int(structure.pipe_diameter)}\"" if structure.pipe_diameter else f"{structure.pipe_type} - Unknown Size"
            
            if key not in pipe_totals:
                pipe_totals[key] = {
                    'pipe_type': structure.pipe_type,
                    'diameter': structure.pipe_diameter,
                    'total_length': 0,
                    'structures': []
                }
            
            pipe_totals[key]['total_length'] += structure.pipe_length
            pipe_totals[key]['structures'].append({
                'id': structure.structure_id,
                'length': structure.pipe_length
            })
        
        # Create results dialog
        results_window = ttk.Toplevel(self.root)
        results_window.title("Pipe Totals Calculation")
        results_window.geometry("700x500")
        self.center_toplevel(results_window)
        results_window.transient(self.root)
        results_window.grab_set()
        
        # Main container
        main_frame = ttk.Frame(results_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(
            main_frame, 
            text="Pipe Totals for Selected Structures", 
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        ).pack(pady=(0, 20))
        
        # Summary info
        summary_frame = ttk.Labelframe(main_frame, text="Selection Summary", padding=10)
        summary_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(
            summary_frame,
            text=f"Structures analyzed: {len(structures_data)}",
            font=("Helvetica", 12)
        ).pack(anchor="w")
        
        ttk.Label(
            summary_frame,
            text=f"Pipe types found: {len(pipe_totals)}",
            font=("Helvetica", 12)
        ).pack(anchor="w")
        
        # Totals table
        totals_frame = ttk.Labelframe(main_frame, text="Pipe Totals by Type", padding=10)
        totals_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Create treeview for totals
        columns = ("PIPE_TYPE", "DIAMETER", "TOTAL_LENGTH", "STRUCTURE_COUNT")
        totals_tree = ttk.Treeview(
            totals_frame,
            columns=columns,
            show="headings",
            height=8
        )
        
        # Configure columns
        totals_tree.heading("PIPE_TYPE", text="Pipe Type", anchor="center")
        totals_tree.heading("DIAMETER", text="Diameter", anchor="center")
        totals_tree.heading("TOTAL_LENGTH", text="Total Length (ft)", anchor="center")
        totals_tree.heading("STRUCTURE_COUNT", text="# Structures", anchor="center")
        
        totals_tree.column("PIPE_TYPE", width=150, anchor="center")
        totals_tree.column("DIAMETER", width=100, anchor="center")
        totals_tree.column("TOTAL_LENGTH", width=150, anchor="center")
        totals_tree.column("STRUCTURE_COUNT", width=120, anchor="center")
        
        # Add scrollbar
        totals_scrollbar = ttk.Scrollbar(totals_frame, orient="vertical", command=totals_tree.yview)
        totals_tree.configure(yscrollcommand=totals_scrollbar.set)
        
        # Pack treeview and scrollbar
        totals_tree.pack(side="left", fill="both", expand=True)
        totals_scrollbar.pack(side="right", fill="y")
        
        # Populate totals
        grand_total_length = 0
        for key, data in pipe_totals.items():
            diameter_text = f"{int(data['diameter'])}\"" if data['diameter'] else "Unknown"
            total_length = data['total_length']
            grand_total_length += total_length
            
            totals_tree.insert(
                "", "end",
                values=(
                    data['pipe_type'],
                    diameter_text,
                    f"{total_length:.2f}",
                    len(data['structures'])
                )
            )
        
        # Grand total
        grand_total_frame = ttk.Frame(main_frame)
        grand_total_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(
            grand_total_frame,
            text=f"Grand Total Length: {grand_total_length:.2f} feet",
            font=("Helvetica", 14, "bold"),
            bootstyle="success"
        ).pack()
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(
            button_frame,
            text="Create Order",
            bootstyle="primary",
            command=lambda: self.create_pipe_order_from_totals(pipe_totals, results_window)
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="Export to CSV",
            bootstyle="info",
            command=lambda: self.export_pipe_totals_csv(pipe_totals)
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="Close",
            bootstyle="secondary",
            command=results_window.destroy
        ).pack(side="right", padx=5)

    def order_pipe_for_selection(self, selected_items):
        """Create a pipe order for selected structures"""
        # Get project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            return
        
        # Extract structure data from selected items
        structures_data = []
        for item in selected_items:
            values = self.structure_tree.item(item, "values")
            if values and values[0] and "─── Run" not in values[0]:
                structure_id = values[0]
                # Get full structure details from database
                structure = self.db.get_structure(structure_id, project.id)
                if structure and structure.pipe_length and structure.pipe_diameter and structure.pipe_type:
                    structures_data.append(structure)
        
        if not structures_data:
            Messagebox.show_info("No structures with pipe data found in selection", "No Pipe Data")
            return
        
        # Group by pipe type and diameter for ordering
        pipe_groups = {}
        for structure in structures_data:
            key = f"{structure.pipe_type}_{int(structure.pipe_diameter) if structure.pipe_diameter else 'unknown'}"
            
            if key not in pipe_groups:
                pipe_groups[key] = {
                    'pipe_type': structure.pipe_type,
                    'diameter': structure.pipe_diameter,
                    'total_length': 0,
                    'structures': []
                }
            
            pipe_groups[key]['total_length'] += structure.pipe_length
            pipe_groups[key]['structures'].append(structure)
        
        # Create order dialog
        order_window = ttk.Toplevel(self.root)
        order_window.title("Create Pipe Order")
        order_window.geometry("600x700")
        self.center_toplevel(order_window)
        order_window.transient(self.root)
        order_window.grab_set()
        
        # Main container
        main_frame = ttk.Frame(order_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(
            main_frame, 
            text="Create Pipe Order", 
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        ).pack(pady=(0, 20))
        
        # Order information section
        order_info_frame = ttk.Labelframe(main_frame, text="Order Information", padding=10)
        order_info_frame.pack(fill="x", pady=(0, 20))
        
        # Order details form
        form_frame = ttk.Frame(order_info_frame)
        form_frame.pack(fill="x")
        form_frame.columnconfigure(1, weight=1)
        
        # Order number
        ttk.Label(form_frame, text="Order Number:").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
        order_number_entry = ttk.Entry(form_frame)
        order_number_entry.grid(row=0, column=1, sticky="ew", pady=5)
        
        # Generate default order number
        from datetime import datetime
        default_order_num = f"PO-{datetime.now().strftime('%Y%m%d')}-{len(structures_data):03d}"
        order_number_entry.insert(0, default_order_num)
        
        # Supplier
        ttk.Label(form_frame, text="Supplier:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=5)
        supplier_entry = ttk.Entry(form_frame)
        supplier_entry.grid(row=1, column=1, sticky="ew", pady=5)
        
        # Expected delivery date
        ttk.Label(form_frame, text="Expected Delivery:").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=5)
        delivery_date_frame = ttk.Frame(form_frame)
        delivery_date_frame.grid(row=2, column=1, sticky="ew", pady=5)
        delivery_date_frame.columnconfigure(0, weight=1)
        
        delivery_date_entry = ttk.Entry(delivery_date_frame)
        delivery_date_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ttk.Button(
            delivery_date_frame,
            text="📅",
            width=3,
            command=lambda: self.open_date_picker(delivery_date_entry)
        ).pack(side="right")
        
        # Notes
        ttk.Label(form_frame, text="Notes:").grid(row=3, column=0, sticky="nw", padx=(0, 10), pady=5)
        notes_text = tk.Text(form_frame, height=3, wrap="word")
        notes_text.grid(row=3, column=1, sticky="ew", pady=5)
        
        # Pipe breakdown section
        breakdown_frame = ttk.Labelframe(main_frame, text="Pipe Breakdown", padding=10)
        breakdown_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Create treeview for pipe breakdown
        columns = ("PIPE_TYPE", "DIAMETER", "TOTAL_LENGTH", "STRUCTURES")
        breakdown_tree = ttk.Treeview(
            breakdown_frame,
            columns=columns,
            show="headings",
            height=8
        )
        
        # Configure columns
        breakdown_tree.heading("PIPE_TYPE", text="Pipe Type", anchor="center")
        breakdown_tree.heading("DIAMETER", text="Diameter", anchor="center")
        breakdown_tree.heading("TOTAL_LENGTH", text="Length (ft)", anchor="center")
        breakdown_tree.heading("STRUCTURES", text="Structures", anchor="center")
        
        breakdown_tree.column("PIPE_TYPE", width=120, anchor="center")
        breakdown_tree.column("DIAMETER", width=80, anchor="center")
        breakdown_tree.column("TOTAL_LENGTH", width=100, anchor="center")
        breakdown_tree.column("STRUCTURES", width=200, anchor="center")
        
        # Add scrollbar
        breakdown_scrollbar = ttk.Scrollbar(breakdown_frame, orient="vertical", command=breakdown_tree.yview)
        breakdown_tree.configure(yscrollcommand=breakdown_scrollbar.set)
        
        # Pack treeview and scrollbar
        breakdown_tree.pack(side="left", fill="both", expand=True)
        breakdown_scrollbar.pack(side="right", fill="y")
        
        # Populate breakdown
        for key, data in pipe_groups.items():
            diameter_text = f"{int(data['diameter'])}\"" if data['diameter'] else "Unknown"
            structure_list = ", ".join([s.structure_id for s in data['structures']])
            
            breakdown_tree.insert(
                "", "end",
                values=(
                    data['pipe_type'],
                    diameter_text,
                    f"{data['total_length']:.2f}",
                    structure_list
                )
            )
        
        # Summary
        total_length = sum(data['total_length'] for data in pipe_groups.values())
        summary_frame = ttk.Frame(main_frame)
        summary_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(
            summary_frame,
            text=f"Total Length: {total_length:.2f} feet | Structures: {len(structures_data)} | Pipe Types: {len(pipe_groups)}",
            font=("Helvetica", 12, "bold"),
            bootstyle="info"
        ).pack()
        
        def create_order():
            try:
                order_number = order_number_entry.get().strip()
                supplier = supplier_entry.get().strip()
                delivery_date_str = delivery_date_entry.get().strip()
                notes = notes_text.get("1.0", tk.END).strip()
                
                # Validation
                if not order_number:
                    Messagebox.show_error("Please enter an order number", "Validation Error")
                    return
                
                # Parse delivery date
                delivery_date = None
                if delivery_date_str:
                    try:
                        delivery_date = datetime.strptime(delivery_date_str, "%m/%d/%Y")
                    except ValueError:
                        Messagebox.show_error("Invalid date format. Please use MM/DD/YYYY", "Date Error")
                        return
                
                # Create the pipe order in database
                success = self.db.create_pipe_order(
                    order_number=order_number,
                    supplier=supplier,
                    expected_delivery_date=delivery_date,
                    notes=notes,
                    pipe_groups=pipe_groups,
                    project_id=project.id
                )
                
                if success:
                    Messagebox.show_info(f"Pipe order '{order_number}' created successfully", "Success")
                    order_window.destroy()
                    # Refresh pipe orders if we're on that tab
                    if hasattr(self, 'pipe_orders_tree'):
                        self.refresh_pipe_orders()
                else:
                    Messagebox.show_error("Failed to create pipe order", "Error")
                    
            except Exception as e:
                self.logger.error(f"Error creating pipe order: {e}", exc_info=True)
                Messagebox.show_error(f"An error occurred: {str(e)}", "Error")
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(
            button_frame,
            text="Create Order",
            bootstyle="primary",
            command=create_order
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            bootstyle="secondary",
            command=order_window.destroy
        ).pack(side="right", padx=5)

    def view_pipe_details_for_selection(self, selected_items):
        """View detailed pipe information for selected structures"""
        # Get project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            return
        
        # Extract structure data from selected items
        structures_data = []
        for item in selected_items:
            values = self.structure_tree.item(item, "values")
            if values and values[0] and "─── Run" not in values[0]:
                structure_id = values[0]
                # Get full structure details from database
                structure = self.db.get_structure(structure_id, project.id)
                if structure:
                    structures_data.append(structure)
        
        if not structures_data:
            Messagebox.show_info("No structures found in selection", "No Data")
            return
        
        # Create details window
        details_window = ttk.Toplevel(self.root)
        details_window.title("Pipe Details for Selected Structures")
        details_window.geometry("900x600")
        self.center_toplevel(details_window)
        details_window.transient(self.root)
        
        # Main container
        main_frame = ttk.Frame(details_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(
            main_frame, 
            text="Pipe Details", 
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        ).pack(pady=(0, 20))
        
        # Summary info
        summary_frame = ttk.Labelframe(main_frame, text="Summary", padding=10)
        summary_frame.pack(fill="x", pady=(0, 20))
        
        # Calculate summary statistics
        total_structures = len(structures_data)
        structures_with_pipe = [s for s in structures_data if s.pipe_length and s.pipe_diameter and s.pipe_type]
        structures_without_pipe = total_structures - len(structures_with_pipe)
        
        summary_text = f"Total Structures: {total_structures} | With Pipe Data: {len(structures_with_pipe)} | Missing Pipe Data: {structures_without_pipe}"
        ttk.Label(summary_frame, text=summary_text, font=("Helvetica", 12)).pack()
        
        # Details table
        details_frame = ttk.Labelframe(main_frame, text="Structure Pipe Details", padding=10)
        details_frame.pack(fill="both", expand=True)
        
        # Create treeview for details
        columns = ("STRUCTURE", "TYPE", "PIPE_TYPE", "DIAMETER", "LENGTH", "UPSTREAM", "STATUS")
        details_tree = ttk.Treeview(
            details_frame,
            columns=columns,
            show="headings",
            height=15
        )
        
        # Configure columns
        details_tree.heading("STRUCTURE", text="Structure ID", anchor="center")
        details_tree.heading("TYPE", text="Type", anchor="center")
        details_tree.heading("PIPE_TYPE", text="Pipe Type", anchor="center")
        details_tree.heading("DIAMETER", text="Diameter", anchor="center")
        details_tree.heading("LENGTH", text="Length (ft)", anchor="center")
        details_tree.heading("UPSTREAM", text="Upstream", anchor="center")
        details_tree.heading("STATUS", text="Status", anchor="center")
        
        details_tree.column("STRUCTURE", width=100, anchor="center")
        details_tree.column("TYPE", width=80, anchor="center")
        details_tree.column("PIPE_TYPE", width=120, anchor="center")
        details_tree.column("DIAMETER", width=80, anchor="center")
        details_tree.column("LENGTH", width=100, anchor="center")
        details_tree.column("UPSTREAM", width=100, anchor="center")
        details_tree.column("STATUS", width=100, anchor="center")
        
        # Configure status tags
        details_tree.tag_configure("complete", background="#d4edda", foreground="#155724")
        details_tree.tag_configure("incomplete", background="#f8d7da", foreground="#721c24")
        details_tree.tag_configure("partial", background="#fff3cd", foreground="#856404")
        
        # Add scrollbar
        details_scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=details_tree.yview)
        details_tree.configure(yscrollcommand=details_scrollbar.set)
        
        # Pack treeview and scrollbar
        details_tree.pack(side="left", fill="both", expand=True)
        details_scrollbar.pack(side="right", fill="y")
        
        # Populate details
        for structure in structures_data:
            # Determine status
            if structure.pipe_length and structure.pipe_diameter and structure.pipe_type:
                status = "Complete"
                tag = "complete"
            elif structure.pipe_type or structure.pipe_diameter or structure.pipe_length:
                status = "Partial"
                tag = "partial"
            else:
                status = "No Pipe Data"
                tag = "incomplete"
            
            # Format values
            pipe_type = structure.pipe_type or "—"
            diameter = f"{int(structure.pipe_diameter)}\"" if structure.pipe_diameter else "—"
            length = f"{structure.pipe_length:.2f}" if structure.pipe_length else "—"
            upstream = structure.upstream_structure_id or "—"
            
            details_tree.insert(
                "", "end",
                values=(
                    structure.structure_id,
                    structure.structure_type,
                    pipe_type,
                    diameter,
                    length,
                    upstream,
                    status
                ),
                tags=(tag,)
            )
        
        # Action buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        # Filter buttons
        filter_frame = ttk.Frame(button_frame)
        filter_frame.pack(side="left")
        
        def filter_complete():
            # Clear and show only complete structures
            for item in details_tree.get_children():
                details_tree.delete(item)
            
            for structure in structures_with_pipe:
                pipe_type = structure.pipe_type or "—"
                diameter = f"{int(structure.pipe_diameter)}\"" if structure.pipe_diameter else "—"
                length = f"{structure.pipe_length:.2f}" if structure.pipe_length else "—"
                upstream = structure.upstream_structure_id or "—"
                
                details_tree.insert(
                    "", "end",
                    values=(
                        structure.structure_id,
                        structure.structure_type,
                        pipe_type,
                        diameter,
                        length,
                        upstream,
                        "Complete"
                    ),
                    tags=("complete",)
                )
        
        def filter_incomplete():
            # Clear and show only incomplete structures
            for item in details_tree.get_children():
                details_tree.delete(item)
            
            incomplete_structures = [s for s in structures_data if not (s.pipe_length and s.pipe_diameter and s.pipe_type)]
            
            for structure in incomplete_structures:
                # Determine status
                if structure.pipe_type or structure.pipe_diameter or structure.pipe_length:
                    status = "Partial"
                    tag = "partial"
                else:
                    status = "No Pipe Data"
                    tag = "incomplete"
                
                pipe_type = structure.pipe_type or "—"
                diameter = f"{int(structure.pipe_diameter)}\"" if structure.pipe_diameter else "—"
                length = f"{structure.pipe_length:.2f}" if structure.pipe_length else "—"
                upstream = structure.upstream_structure_id or "—"
                
                details_tree.insert(
                    "", "end",
                    values=(
                        structure.structure_id,
                        structure.structure_type,
                        pipe_type,
                        diameter,
                        length,
                        upstream,
                        status
                    ),
                    tags=(tag,)
                )
        
        def show_all():
            # Repopulate with all structures
            for item in details_tree.get_children():
                details_tree.delete(item)
            
            for structure in structures_data:
                # Determine status
                if structure.pipe_length and structure.pipe_diameter and structure.pipe_type:
                    status = "Complete"
                    tag = "complete"
                elif structure.pipe_type or structure.pipe_diameter or structure.pipe_length:
                    status = "Partial"
                    tag = "partial"
                else:
                    status = "No Pipe Data"
                    tag = "incomplete"
                
                pipe_type = structure.pipe_type or "—"
                diameter = f"{int(structure.pipe_diameter)}\"" if structure.pipe_diameter else "—"
                length = f"{structure.pipe_length:.2f}" if structure.pipe_length else "—"
                upstream = structure.upstream_structure_id or "—"
                
                details_tree.insert(
                    "", "end",
                    values=(
                        structure.structure_id,
                        structure.structure_type,
                        pipe_type,
                        diameter,
                        length,
                        upstream,
                        status
                    ),
                    tags=(tag,)
                )
        
        ttk.Button(
            filter_frame,
            text="Show Complete",
            bootstyle="success-outline",
            command=filter_complete
        ).pack(side="left", padx=2)
        
        ttk.Button(
            filter_frame,
            text="Show Incomplete",
            bootstyle="warning-outline",
            command=filter_incomplete
        ).pack(side="left", padx=2)
        
        ttk.Button(
            filter_frame,
            text="Show All",
            bootstyle="secondary-outline",
            command=show_all
        ).pack(side="left", padx=2)
        
        # Export and close buttons
        action_frame = ttk.Frame(button_frame)
        action_frame.pack(side="right")
        
        ttk.Button(
            action_frame,
            text="Export CSV",
            bootstyle="info",
            command=lambda: self.export_pipe_details_csv(structures_data)
        ).pack(side="left", padx=5)
        
        ttk.Button(
            action_frame,
            text="Close",
            bootstyle="secondary",
            command=details_window.destroy
        ).pack(side="left", padx=5)

    def load_pipe_orders(self):
        """Load pipe orders into the tracking tab"""
        # Clear existing items
        if hasattr(self, 'pipe_orders_tree'):
            for item in self.pipe_orders_tree.get_children():
                self.pipe_orders_tree.delete(item)
        
        # Get project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            return
        
        # Get pipe orders from database
        try:
            pipe_orders = self.db.get_pipe_orders(project.id)
            
            for order in pipe_orders:
                # Format order date
                order_date = order.get('order_date', '')
                if order_date:
                    try:
                        order_date = datetime.fromisoformat(order_date).strftime("%m/%d/%Y")
                    except:
                        order_date = str(order_date)
                
                # Format delivery date (NEW)
                delivery_date = order.get('actual_delivery_date', '')
                if delivery_date:
                    try:
                        if isinstance(delivery_date, str):
                            delivery_date = datetime.fromisoformat(delivery_date).strftime("%m/%d/%Y")
                        else:
                            delivery_date = delivery_date.strftime("%m/%d/%Y")
                    except:
                        delivery_date = str(delivery_date) if delivery_date else ''
                else:
                    delivery_date = ''
                
                # Determine status tag
                status = order.get('status', 'pending').lower()
                tag = status if status in ['pending', 'ordered', 'in_transit', 'delivered'] else 'pending'
                
                delivery_date = order.get('actual_delivery_date', '')
                if delivery_date:
                    try:
                        if isinstance(delivery_date, str):
                            delivery_date = datetime.fromisoformat(delivery_date).strftime("%m/%d/%Y")
                        else:
                            delivery_date = delivery_date.strftime("%m/%d/%Y")
                    except:
                        delivery_date = str(delivery_date) if delivery_date else ''
                else:
                    delivery_date = ''

                self.pipe_orders_tree.insert(
                    "", "end",
                    values=(
                        order.get('order_number', ''),
                        order.get('pipe_type', ''),
                        order.get('diameter', ''),
                        f"{order.get('total_length', 0):.2f}",
                        order.get('status', '').title(),
                        order_date,
                        delivery_date  # NEW: Add delivery date
                    ),
                    tags=(tag,)
                )
        
        except Exception as e:
            # If pipe orders table doesn't exist yet, show placeholder
            self.logger.info(f"Pipe orders not available yet: {e}")
            self.pipe_orders_tree.insert(
                "", "end",
                values=("No orders", "—", "—", "—", "No pipe orders found", "—", "—"),
                tags=("pending",)
            )

    def quick_update_component_status(self, new_status):
        """Quickly update component status from context menu"""
        selection = self.component_tree.selection()
        if not selection:
            return
        
        # Get component ID from tags
        component_id = int([tag for tag in self.component_tree.item(selection[0], "tags") if tag.isdigit()][0])
        
        # Set delivery date if changing to delivered/installed
        delivery_date = None
        if new_status in ["delivered", "installed"]:
            delivery_date = datetime.now()
        
        success = self.db.update_component_status(component_id, new_status, None, delivery_date)
        
        if success:
            # Refresh current view
            if self.component_structure_tree.selection():
                structure_id = self.component_structure_tree.item(
                    self.component_structure_tree.selection()[0], "values")[0]
                self.load_structure_components_enhanced(structure_id)
                self.refresh_component_status()
        else:
            Messagebox.show_error("Failed to update component status", "Error")

    def delete_component_from_context(self):
        """Delete component from right-click context menu"""
        selection = self.component_tree.selection()
        if not selection:
            return
        
        # Get component ID from tags
        component_id = int([tag for tag in self.component_tree.item(selection[0], "tags") if tag.isdigit()][0])
        
        success = self.db.delete_structure_component(component_id)
        
        if success:
            # Refresh current view
            if self.component_structure_tree.selection():
                structure_id = self.component_structure_tree.item(
                    self.component_structure_tree.selection()[0], "values")[0]
                self.load_structure_components_enhanced(structure_id)
                self.refresh_component_status()
        else:
            Messagebox.show_error("Failed to delete component", "Error")

    def open_date_picker(self, entry_widget):
        """Open a properly formatted custom calendar date picker"""
        from datetime import datetime, timedelta
        import calendar
        from ttkbootstrap.dialogs import Messagebox
        
        try:
            # Create date picker window
            date_window = ttk.Toplevel(self.root)
            date_window.title("Select Date")
            date_window.geometry("350x370")
            date_window.transient(self.root)
            date_window.grab_set()
            date_window.resizable(False, False)
            date_window.minsize(350, 370)

            self.center_toplevel(date_window)            
            # Main frame
            main_frame = ttk.Frame(date_window, padding=10)
            main_frame.pack(fill="both", expand=True)
            
            # Current date for default
            today = datetime.now()
            current_year = today.year
            current_month = today.month
            current_day = today.day
            
            # Variables to track selected date
            selected_date = [current_year, current_month, current_day]
            
            # Title
            ttk.Label(main_frame, text="Select Date", 
                    font=("Helvetica", 12, "bold"), 
                    bootstyle="primary").pack(pady=(0, 10))
            
            # Month/Year navigation frame
            nav_frame = ttk.Frame(main_frame)
            nav_frame.pack(fill="x", pady=(0, 10))
            
            # Month/Year display and controls
            month_year_var = tk.StringVar()
            
            def update_month_year_display():
                month_name = calendar.month_name[selected_date[1]]
                month_year_var.set(f"{month_name} {selected_date[0]}")
            
            def prev_month():
                if selected_date[1] == 1:
                    selected_date[1] = 12
                    selected_date[0] -= 1
                else:
                    selected_date[1] -= 1
                update_calendar()
            
            def next_month():
                if selected_date[1] == 12:
                    selected_date[1] = 1
                    selected_date[0] += 1
                else:
                    selected_date[1] += 1
                update_calendar()
            
            # Navigation layout: < Month Year >
            ttk.Button(nav_frame, text="◀", command=prev_month, width=3).pack(side="left")
            
            month_year_label = ttk.Label(nav_frame, textvariable=month_year_var, 
                                        font=("Helvetica", 12, "bold"))
            month_year_label.pack(side="left", expand=True)
            
            ttk.Button(nav_frame, text="▶", command=next_month, width=3).pack(side="right")
            
            # Calendar container frame
            calendar_container = ttk.Frame(main_frame)
            calendar_container.pack(pady=(0, 10))
            
            # Complete calendar grid (headers + dates in one frame)
            cal_grid = ttk.Frame(calendar_container)
            cal_grid.pack()
            
            # Day of week headers - row 0
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            for i, day in enumerate(days):
                header_label = ttk.Label(cal_grid, text=day, font=("Helvetica", 8, "bold"),
                                    bootstyle="secondary", width=4, anchor="center")
                header_label.grid(row=0, column=i, padx=1, pady=(0, 3), sticky="ew")
            
            # Configure all columns to be equal width
            for i in range(7):
                cal_grid.columnconfigure(i, weight=1, minsize=35)
            
            # Calendar day buttons
            day_buttons = {}
            
            def select_day(day):
                selected_date[2] = day
                update_calendar()
            
            def update_calendar():
                # Clear existing day buttons
                for button in day_buttons.values():
                    button.destroy()
                day_buttons.clear()
                
                # Update month/year display
                update_month_year_display()
                
                # Get calendar for current month
                cal = calendar.monthcalendar(selected_date[0], selected_date[1])
                
                # Create day buttons - start from row 1 (row 0 has headers)
                for week_num, week in enumerate(cal, 1):
                    for day_num, day in enumerate(week):
                        if day == 0:
                            # Empty cell - create invisible spacer
                            spacer = ttk.Label(cal_grid, text="", width=4)
                            spacer.grid(row=week_num, column=day_num, padx=1, pady=1)
                            continue
                        
                        # Determine button style
                        is_today = (day == today.day and 
                                selected_date[1] == today.month and 
                                selected_date[0] == today.year)
                        is_selected = day == selected_date[2]
                        
                        if is_selected:
                            style = "primary"  # Blue for selected date
                        elif is_today:
                            style = "secondary"  # Grey for today's date
                        else:
                            style = "secondary-outline"
                        
                        btn = ttk.Button(cal_grid, text=str(day), 
                                    command=lambda d=day: select_day(d),
                                    bootstyle=style, width=4)
                        btn.grid(row=week_num, column=day_num, padx=1, pady=1, sticky="ew")
                        day_buttons[day] = btn
            
            # Selected date display
            selected_display = ttk.Label(main_frame, text="", 
                                    font=("Helvetica", 9, "bold"), 
                                    bootstyle="success")
            selected_display.pack(pady=(0, 10))
            
            def update_selected_display():
                date_str = f"{selected_date[1]:02d}/{selected_date[2]:02d}/{selected_date[0]}"
                selected_display.config(text=f"Selected: {date_str}")
            
            # Override update_calendar to also update display
            original_update_calendar = update_calendar
            def update_calendar():
                original_update_calendar()
                update_selected_display()
            
            # Button frame
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill="x")
            
            def confirm_selection():
                date_str = f"{selected_date[1]:02d}/{selected_date[2]:02d}/{selected_date[0]}"
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, date_str)
                date_window.destroy()
            
            def cancel_selection():
                date_window.destroy()
            
            # Action buttons
            ttk.Button(button_frame, text="OK", bootstyle="primary", 
                    command=confirm_selection, width=10).pack(side="left", padx=(0, 5))
            ttk.Button(button_frame, text="Cancel", bootstyle="secondary", 
                    command=cancel_selection, width=10).pack(side="right")
            
            # Initialize calendar
            update_calendar()
            
            # Bind Escape key to cancel
            date_window.bind('<Escape>', lambda e: cancel_selection())
            
            # Bind Enter key to confirm
            date_window.bind('<Return>', lambda e: confirm_selection())
            
        except Exception as e:
            self.logger.error(f"Error opening custom date picker: {e}", exc_info=True)
            
            # Fallback to simple dialog
            try:
                from tkinter import simpledialog
                date_str = simpledialog.askstring(
                    "Date Input", 
                    "Enter date (MM/DD/YYYY):",
                    initialvalue=datetime.now().strftime("%m/%d/%Y")
                )
                if date_str:
                    try:
                        datetime.strptime(date_str, "%m/%d/%Y")
                        entry_widget.delete(0, tk.END)
                        entry_widget.insert(0, date_str)
                    except ValueError:
                        Messagebox.show_error("Invalid date format. Please use MM/DD/YYYY", "Date Error")
            except Exception as fallback_error:
                self.logger.error(f"Fallback date picker failed: {fallback_error}")
                Messagebox.show_error("Date picker unavailable. Please enter date manually.", "Error")

    def update_component_status(self):
        """Enhanced component status update with better UX"""
        selection = self.component_tree.selection()
        if not selection:
            Messagebox.show_warning("Please select a component first", "No Component Selected")
            return
        
        # Get component details
        component_id = int([tag for tag in self.component_tree.item(selection[0], "tags") if tag.isdigit()][0])
        values = self.component_tree.item(selection[0], "values")
        current_type = values[0]
        current_status = values[1].lower()
        current_notes = values[5]
        
        # Create enhanced update dialog
        self.show_component_update_dialog(component_id, current_type, current_status, current_notes)

    def show_component_update_dialog(self, component_id: int, component_type: str, current_status: str, current_notes: str):
        """Show enhanced component update dialog with calendar buttons and correct size"""
        update_window = ttk.Toplevel(self.root)
        update_window.title("Update Component Status")
        update_window.geometry("505x725")
        self.center_toplevel(update_window)
        update_window.transient(self.root)
        update_window.grab_set()
        
        # Main container
        main_frame = ttk.Frame(update_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(
            main_frame, 
            text="Update Component Status", 
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        ).pack(pady=(0, 20))
        
        # Component info
        info_frame = ttk.Labelframe(main_frame, text="Component Information", padding=10)
        info_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(info_frame, text=f"Type: {component_type}", font=("Helvetica", 12, "bold")).pack(anchor="w")
        ttk.Label(info_frame, text=f"Current Status: {current_status.title()}", font=("Helvetica", 10)).pack(anchor="w")
        
        # Status update section
        status_frame = ttk.Labelframe(main_frame, text="Update Status", padding=10)
        status_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(status_frame, text="New Status:").pack(anchor="w", pady=(0, 5))
        
        status_var = tk.StringVar(value=current_status)
        status_options = ["pending", "ordered", "approved", "delivered", "installed"]
        status_combo = ttk.Combobox(status_frame, textvariable=status_var, values=status_options, state="readonly")
        status_combo.pack(fill="x", pady=(0, 10))
        
        # Date fields with calendar buttons
        date_frame = ttk.Frame(status_frame)
        date_frame.pack(fill="x", pady=(10, 0))
        
        # Order date
        order_frame = ttk.Frame(date_frame)
        ttk.Label(order_frame, text="Order Date:").pack(anchor="w")
        order_date_frame = ttk.Frame(order_frame)
        order_date_frame.pack(fill="x", pady=(2, 10))
        order_entry = ttk.Entry(order_date_frame)
        order_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        order_cal_btn = ttk.Button(order_date_frame, text="📅", width=3,
                                command=lambda: self.open_date_picker(order_entry))
        order_cal_btn.pack(side="right")
        
        # Expected delivery date
        expected_frame = ttk.Frame(date_frame)
        ttk.Label(expected_frame, text="Expected Delivery:").pack(anchor="w")
        expected_date_frame = ttk.Frame(expected_frame)
        expected_date_frame.pack(fill="x", pady=(2, 10))
        expected_entry = ttk.Entry(expected_date_frame)
        expected_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        expected_cal_btn = ttk.Button(expected_date_frame, text="📅", width=3,
                                    command=lambda: self.open_date_picker(expected_entry))
        expected_cal_btn.pack(side="right")
        
        # Actual delivery date
        delivery_frame = ttk.Frame(date_frame)
        ttk.Label(delivery_frame, text="Actual Delivery:").pack(anchor="w")
        actual_date_frame = ttk.Frame(delivery_frame)
        actual_date_frame.pack(fill="x", pady=(2, 10))
        actual_entry = ttk.Entry(actual_date_frame)
        actual_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        actual_cal_btn = ttk.Button(actual_date_frame, text="📅", width=3,
                                command=lambda: self.open_date_picker(actual_entry))
        actual_cal_btn.pack(side="right")
        
        # Show/hide date fields based on status
        def update_date_visibility(*args):
            # Clear all frames first
            order_frame.pack_forget()
            expected_frame.pack_forget()
            delivery_frame.pack_forget()
            
            status = status_var.get()
            if status in ["ordered", "approved", "delivered", "installed"]:
                order_frame.pack(fill="x")
                expected_frame.pack(fill="x")
            
            if status in ["delivered", "installed"]:
                delivery_frame.pack(fill="x")
        
        status_var.trace("w", update_date_visibility)
        update_date_visibility()  # Initial setup
        
        # Notes section
        notes_frame = ttk.Labelframe(main_frame, text="Notes", padding=10)
        notes_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        notes_text = tk.Text(notes_frame, height=6, wrap="word")
        notes_text.pack(fill="both", expand=True)
        notes_text.insert("1.0", current_notes)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        def save_update():
            try:
                # Parse dates
                order_date = None
                expected_date = None
                actual_date = None
                
                if order_entry.get().strip():
                    order_date = datetime.strptime(order_entry.get().strip(), "%m/%d/%Y")
                
                if expected_entry.get().strip():
                    expected_date = datetime.strptime(expected_entry.get().strip(), "%m/%d/%Y")
                
                if actual_entry.get().strip():
                    actual_date = datetime.strptime(actual_entry.get().strip(), "%m/%d/%Y")
                
                # Update component with enhanced method
                success = self.db.update_component_status_enhanced(
                    component_id,
                    status_var.get(),
                    notes_text.get("1.0", tk.END).strip(),
                    order_date,
                    expected_date,
                    actual_date
                )
                
                if success:
                    update_window.destroy()
                    # Refresh views
                    self.refresh_component_status()
                    # Reload components for current structure
                    if self.component_structure_tree.selection():
                        structure_id = self.component_structure_tree.item(
                            self.component_structure_tree.selection()[0], "values")[0]
                        self.load_structure_components_enhanced(structure_id)
                else:
                    Messagebox.show_error("Failed to update component", "Error")
            
            except ValueError as e:
                Messagebox.show_error("Invalid date format. Please use MM/DD/YYYY", "Date Error")
            except Exception as e:
                Messagebox.show_error(f"An error occurred: {str(e)}", "Error")
        
        ttk.Button(button_frame, text="Save", bootstyle="primary", command=save_update).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", bootstyle="secondary", command=update_window.destroy).pack(side="right", padx=5)

    def refresh_component_status(self):
        """Refresh the component status overview"""
        # Store current selection
        current_selection = None
        if self.component_structure_tree.selection():
            current_selection = self.component_structure_tree.item(
                self.component_structure_tree.selection()[0], "values")[0]
        
        # Reload structures
        self.load_structures_for_components()
        
        # Restore selection if possible
        if current_selection:
            for item in self.component_structure_tree.get_children():
                if self.component_structure_tree.item(item, "values")[0] == current_selection:
                    self.component_structure_tree.selection_set(item)
                    self.component_structure_tree.see(item)
                    break

    def filter_structures_by_status(self, event=None):
        """Filter structures based on their component status"""
        filter_value = self.component_filter_var.get()
        
        # Clear current items
        for item in self.component_structure_tree.get_children():
            self.component_structure_tree.delete(item)
        
        # Get project and structures
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            return
        
        structures = self.db.get_all_structures(project.id)
        
        # Filter and add structures
        for structure in structures:
            status_info = self.calculate_structure_component_status(structure.structure_id, project.id)
            
            # Determine if structure matches filter
            show_structure = False
            
            if filter_value == "All Structures":
                show_structure = True
            elif filter_value == "Installed" and status_info['total'] > 0:
                show_structure = (status_info['installed'] == status_info['total'])
            elif filter_value == "Delivered" and status_info['total'] > 0:
                show_structure = (status_info['delivered'] == status_info['total'] and status_info['installed'] < status_info['total'])
            elif filter_value == "Approved" and status_info['total'] > 0:  # NEW: Handle Approved filter
                show_structure = (status_info['approved'] == status_info['total'])
            elif filter_value == "Not Started":
                show_structure = (status_info['total'] == 0)
            elif filter_value == "In Progress" and status_info['total'] > 0:
                show_structure = (0 < status_info['delivered'] + status_info['installed'] < status_info['total'])
            elif filter_value == "Incomplete" and status_info['total'] > 0:
                show_structure = (status_info['delivered'] + status_info['installed'] < status_info['total'])
            
            if show_structure:
                # Determine status and tag with new approved logic
                if status_info['total'] == 0:
                    tag = "not_started"
                    status_text = "Not Started"
                elif status_info['installed'] == status_info['total']:
                    tag = "installed"
                    status_text = "Installed"
                elif status_info['delivered'] == status_info['total']:
                    tag = "delivered"
                    status_text = "Delivered"
                elif status_info['approved'] == status_info['total']:  
                    tag = "approved"
                    status_text = "Approved"
                elif status_info['delivered'] + status_info['installed'] > 0:
                    tag = "in_progress"
                    status_text = "In Progress"
                else:
                    tag = "incomplete"
                    status_text = "Incomplete"
                
                progress_text = f"{status_info['delivered'] + status_info['installed']}/{status_info['total']}"
                
                self.component_structure_tree.insert(
                    "", 
                    "end", 
                    values=(structure.structure_id, structure.structure_type, status_text, progress_text),
                    tags=(tag,)
                )

    def add_component_enhanced(self):
        """Enhanced add component dialog - UPDATED WITHOUT SUCCESS DIALOG"""
        # Get selected structure
        selection = self.component_structure_tree.selection()
        if not selection:
            Messagebox.show_warning("Please select a structure first", "No Structure Selected")
            return
        
        structure_id = self.component_structure_tree.item(selection[0], "values")[0]
        structure_type = self.component_structure_tree.item(selection[0], "values")[1]
        
        # Get project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            return
        
        # Create enhanced dialog with specified size
        component_window = ttk.Toplevel(self.root)
        component_window.title("Add Component")
        component_window.geometry("470x760")
        self.center_toplevel(component_window)
        component_window.transient(self.root)
        component_window.grab_set()
        
        # Main container
        main_frame = ttk.Frame(component_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(
            main_frame, 
            text="Add Component", 
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        ).pack(pady=(0, 20))
        
        # Structure info
        info_frame = ttk.Labelframe(main_frame, text="Structure Information", padding=10)
        info_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(
            info_frame,
            text=f"Structure: {structure_id}",
            font=("Helvetica", 12, "bold")
        ).pack(anchor="w")
        ttk.Label(
            info_frame,
            text=f"Type: {structure_type}",
            font=("Helvetica", 10)
        ).pack(anchor="w")
        
        # Component selection
        component_frame = ttk.Labelframe(main_frame, text="Component Details", padding=10)
        component_frame.pack(fill="x", pady=(0, 20))
        
        # Component type with smart suggestions
        ttk.Label(component_frame, text="Component Type:").pack(anchor="w", pady=(0, 5))
        
        component_types = self.db.get_all_component_types()
        type_names = [ct.name for ct in component_types]
        
        type_var = tk.StringVar()
        type_combo = ttk.Combobox(component_frame, textvariable=type_var, values=type_names, state="readonly")
        type_combo.pack(fill="x", pady=(0, 10))
        
        # Smart suggestions based on existing components
        existing_components = self.db.get_structure_components(structure_id, project.id)
        existing_types = [comp.component_type_name.lower() for comp in existing_components]
        
        # Suggest missing components
        suggestions = []
        if structure_type in ["CB", "JB"] and "riser" not in existing_types:
            suggestions.append("Riser (Recommended for CB/JB)")
        if "lid" not in existing_types and ("riser" in existing_types or structure_type in ["CB", "JB"]):
            suggestions.append("Lid (Recommended with Riser)")
        if "frame" not in existing_types:
            suggestions.append("Frame (Optional)")
        
        if suggestions:
            suggest_frame = ttk.Frame(component_frame)
            suggest_frame.pack(fill="x", pady=(0, 10))
            
            ttk.Label(suggest_frame, text="Suggestions:", font=("Helvetica", 9, "bold")).pack(anchor="w")
            for suggestion in suggestions[:3]:
                ttk.Label(suggest_frame, text=f"• {suggestion}", font=("Helvetica", 9)).pack(anchor="w", padx=10)
        
        if type_names:
            # Auto-select based on suggestions
            if structure_type in ["CB", "JB"] and "riser" not in existing_types and "Riser" in type_names:
                type_combo.set("Riser")
            elif "riser" in existing_types and "lid" not in existing_types and "Lid" in type_names:
                type_combo.set("Lid")
            else:
                type_combo.current(0)
        
        # Initial status
        ttk.Label(component_frame, text="Initial Status:").pack(anchor="w", pady=(10, 5))
        
        status_var = tk.StringVar(value="pending")
        status_options = ["pending", "ordered", "approved", "delivered", "installed"]
        status_combo = ttk.Combobox(component_frame, textvariable=status_var, values=status_options, state="readonly")
        status_combo.pack(fill="x", pady=(0, 10))
        
        # Date fields with calendar buttons
        date_frame = ttk.Frame(component_frame)
        date_frame.pack(fill="x", pady=(10, 0))
        
        # Order date
        order_frame = ttk.Frame(date_frame)
        ttk.Label(order_frame, text="Order Date:").pack(anchor="w")
        order_date_frame = ttk.Frame(order_frame)
        order_date_frame.pack(fill="x", pady=(2, 10))
        order_entry = ttk.Entry(order_date_frame)
        order_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        order_cal_btn = ttk.Button(order_date_frame, text="📅", width=3,
                                command=lambda: self.open_date_picker(order_entry))
        order_cal_btn.pack(side="right")
        
        # Expected delivery
        expected_frame = ttk.Frame(date_frame)
        ttk.Label(expected_frame, text="Expected Delivery:").pack(anchor="w")
        expected_date_frame = ttk.Frame(expected_frame)
        expected_date_frame.pack(fill="x", pady=(2, 10))
        expected_entry = ttk.Entry(expected_date_frame)
        expected_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        expected_cal_btn = ttk.Button(expected_date_frame, text="📅", width=3,
                                    command=lambda: self.open_date_picker(expected_entry))
        expected_cal_btn.pack(side="right")
        
        # Actual delivery
        actual_frame = ttk.Frame(date_frame)
        ttk.Label(actual_frame, text="Actual Delivery:").pack(anchor="w")
        actual_date_frame = ttk.Frame(actual_frame)
        actual_date_frame.pack(fill="x", pady=(2, 10))
        actual_entry = ttk.Entry(actual_date_frame)
        actual_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        actual_cal_btn = ttk.Button(actual_date_frame, text="📅", width=3,
                                command=lambda: self.open_date_picker(actual_entry))
        actual_cal_btn.pack(side="right")
        
        # Show/hide date fields based on status
        def update_date_fields(*args):
            order_frame.pack_forget()
            expected_frame.pack_forget()
            actual_frame.pack_forget()
            
            status = status_var.get()
            if status in ["ordered", "approved", "delivered", "installed"]:
                order_frame.pack(fill="x")
                expected_frame.pack(fill="x")
                if not order_entry.get():
                    order_entry.insert(0, datetime.now().strftime("%m/%d/%Y"))
            
            if status in ["delivered", "installed"]:
                actual_frame.pack(fill="x")
                if not actual_entry.get():
                    actual_entry.insert(0, datetime.now().strftime("%m/%d/%Y"))
        
        status_var.trace("w", update_date_fields)
        update_date_fields()
        
        # Notes
        notes_frame = ttk.Labelframe(main_frame, text="Notes (Optional)", padding=10)
        notes_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        notes_text = tk.Text(notes_frame, height=4, wrap="word")
        notes_text.pack(fill="both", expand=True)
        
        # Quick actions
        quick_frame = ttk.Frame(main_frame)
        quick_frame.pack(fill="x", pady=(0, 20))
        
        def quick_riser():
            if "Riser" in type_names:
                type_var.set("Riser")
                status_var.set("pending")
        
        def quick_lid():
            if "Lid" in type_names:
                type_var.set("Lid")
                status_var.set("pending")
        
        def quick_complete_component():
            current_type = type_var.get()
            if current_type:
                status_var.set("installed")
                actual_entry.delete(0, tk.END)
                actual_entry.insert(0, datetime.now().strftime("%m/%d/%Y"))
                notes_text.insert("1.0", f"{current_type} installed during construction")
        
        ttk.Button(quick_frame, text="Quick: Riser", bootstyle="info-outline", command=quick_riser).pack(side="left", padx=5)
        ttk.Button(quick_frame, text="Quick: Lid", bootstyle="info-outline", command=quick_lid).pack(side="left", padx=5)
        ttk.Button(quick_frame, text="Mark as Installed", bootstyle="success-outline", command=quick_complete_component).pack(side="right", padx=5)
        
        def save_component():
            try:
                # Validate component type
                if not type_var.get():
                    Messagebox.show_error("Please select a component type", "Validation Error")
                    return
                
                # Get component type ID
                component_type_id = None
                for ct in component_types:
                    if ct.name == type_var.get():
                        component_type_id = ct.id
                        break
                
                if not component_type_id:
                    Messagebox.show_error("Invalid component type", "Validation Error")
                    return
                
                # Parse dates 
                order_date = None
                expected_date = None
                actual_date = None
                
                try:
                    if order_entry.get().strip():
                        order_date = datetime.strptime(order_entry.get().strip(), "%m/%d/%Y")
                    
                    if expected_entry.get().strip():
                        expected_date = datetime.strptime(expected_entry.get().strip(), "%m/%d/%Y")
                    
                    if actual_entry.get().strip():
                        actual_date = datetime.strptime(actual_entry.get().strip(), "%m/%d/%Y")
                
                except ValueError:
                    Messagebox.show_error("Invalid date format. Please use MM/DD/YYYY", "Date Error")
                    return
                
                # Create component
                component = StructureComponent(
                    structure_id=structure_id,
                    component_type_id=component_type_id,
                    status=status_var.get(),
                    order_date=order_date,
                    expected_delivery_date=expected_date,
                    actual_delivery_date=actual_date,
                    notes=notes_text.get("1.0", tk.END).strip() or None,
                    project_id=project.id
                )
                
                # Add to database
                success = self.db.add_structure_component(component, project.id)
                
                if success:
                    # Clear form and refresh without success dialog
                    type_var.set("")
                    status_var.set("pending")
                    order_entry.delete(0, tk.END)
                    expected_entry.delete(0, tk.END)
                    actual_entry.delete(0, tk.END)
                    notes_text.delete("1.0", tk.END)
                    
                    # Refresh views
                    self.load_structure_components_enhanced(structure_id)
                    self.refresh_component_status()
                    
                    # Focus back to component type for quick next entry
                    type_combo.focus()
                else:
                    Messagebox.show_error("Failed to add component", "Database Error")
            
            except Exception as e:
                Messagebox.show_error(f"An error occurred: {str(e)}", "Error")

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Add Component", bootstyle="primary", command=save_component).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Close", bootstyle="secondary", command=component_window.destroy).pack(side="right", padx=5)

    def bulk_update_components(self):
        """Bulk update multiple components"""
        # Get selected structure
        selection = self.component_structure_tree.selection()
        if not selection:
            Messagebox.show_warning("Please select a structure first", "No Structure Selected")
            return
        
        structure_id = self.component_structure_tree.item(selection[0], "values")[0]
        
        # Get project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            return
        
        # Get all components for this structure
        components = self.db.get_structure_components(structure_id, project.id)
        
        if not components:
            Messagebox.show_info("No components found for this structure", "No Components")
            return
        
        # Create bulk update dialog
        bulk_window = ttk.Toplevel(self.root)
        bulk_window.title("Bulk Update Components")
        bulk_window.geometry("600x500")
        self.center_toplevel(bulk_window)
        bulk_window.transient(self.root)
        bulk_window.grab_set()
        
        # Main container
        main_frame = ttk.Frame(bulk_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(
            main_frame, 
            text=f"Bulk Update: {structure_id}", 
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        ).pack(pady=(0, 20))
        
        # Component selection
        selection_frame = ttk.Labelframe(main_frame, text="Select Components to Update", padding=10)
        selection_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Checkboxes for each component
        component_vars = {}
        for component in components:
            var = tk.BooleanVar(value=True)
            component_vars[component.id] = var
            
            check_frame = ttk.Frame(selection_frame)
            check_frame.pack(fill="x", pady=2)
            
            ttk.Checkbutton(
                check_frame,
                text=f"{component.component_type_name} - Current: {component.status.title()}",
                variable=var
            ).pack(side="left")
        
        # Update options
        update_frame = ttk.Labelframe(main_frame, text="Update Options", padding=10)
        update_frame.pack(fill="x", pady=(0, 20))
        
        # New status
        ttk.Label(update_frame, text="New Status:").pack(anchor="w", pady=(0, 5))
        new_status_var = tk.StringVar()
        status_combo = ttk.Combobox(
            update_frame, 
            textvariable=new_status_var, 
            values=["pending", "ordered", "approved", "delivered", "installed"],
            state="readonly"
        )
        status_combo.pack(fill="x", pady=(0, 10))
        
        # Date for delivery
        ttk.Label(update_frame, text="Delivery Date (MM/DD/YYYY, if applicable):").pack(anchor="w", pady=(0, 5))
        date_entry = ttk.Entry(update_frame)
        date_entry.pack(fill="x", pady=(0, 10))
        
        # Additional notes
        ttk.Label(update_frame, text="Additional Notes:").pack(anchor="w", pady=(0, 5))
        notes_entry = ttk.Entry(update_frame)
        notes_entry.pack(fill="x")
        
        def perform_bulk_update():
            if not new_status_var.get():
                Messagebox.show_error("Please select a new status", "Missing Status")
                return
            
            # Get selected components
            selected_components = [comp_id for comp_id, var in component_vars.items() if var.get()]
            
            if not selected_components:
                Messagebox.show_error("Please select at least one component", "No Selection")
                return
            
            # Parse date if provided
            delivery_date = None
            if date_entry.get().strip():
                try:
                    delivery_date = datetime.strptime(date_entry.get().strip(), "%m/%d/%Y")
                except ValueError:
                    Messagebox.show_error("Invalid date format. Please use MM/DD/YYYY", "Date Error")
                    return
            
            # Update components
            updated_count = 0
            for comp_id in selected_components:
                success = self.db.update_component_status(
                    comp_id,
                    new_status_var.get(),
                    notes_entry.get().strip() or None,
                    delivery_date
                )
                if success:
                    updated_count += 1
            
            if updated_count > 0:
                Messagebox.show_info(f"Updated {updated_count} components", "Success")
                bulk_window.destroy()
                # Refresh views
                self.load_structure_components_enhanced(structure_id)
                self.refresh_component_status()
            else:
                Messagebox.show_error("Failed to update components", "Error")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Update Selected", bootstyle="primary", command=perform_bulk_update).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", bootstyle="secondary", command=bulk_window.destroy).pack(side="right", padx=5)

    def refresh_pipe_orders(self):
        """Enhanced refresh with better status handling"""
        self.load_pipe_orders()
        self.calculate_project_pipe_totals()
        
        # Update any status-related UI elements
        if hasattr(self, 'pipe_filter_var'):
            # Refresh the current filter
            self.filter_pipe_orders()


    def show_pipe_breakdown_context_menu_enhanced(self, event):
        """Show enhanced right-click context menu for pipe breakdown items with quick status updates"""
        # Get the item under the cursor
        item = self.order_breakdown_tree.identify_row(event.y)
        if not item:
            return
        
        # Select the item
        self.order_breakdown_tree.selection_set(item)
        
        # Get item details
        values = self.order_breakdown_tree.item(item, "values")
        if not values or values[0] == "Error" or values[0] == "No items":
            return
        
        structure_id = values[0]
        pipe_type = values[1]
        delivered_status = values[4]  # "Yes", "No", or "Partial"
        
        # Get item ID from tags
        tags = self.order_breakdown_tree.item(item, "tags")
        item_id = None
        for tag in tags:
            if tag.isdigit():
                item_id = int(tag)
                break
        
        if not item_id:
            return
        
        # Create context menu
        context_menu = tk.Menu(self.root, tearoff=0)
        
        # Quick delivery status updates
        if delivered_status.lower() == "no":
            context_menu.add_command(
                label="✓ Mark as Delivered",
                command=lambda: self.quick_mark_pipe_item_delivered(item_id, structure_id)
            )
            
            context_menu.add_command(
                label="◐ Mark as Partial Delivery",
                command=lambda: self.show_partial_delivery_dialog(item_id, structure_id)
            )
        elif "partial" in delivered_status.lower():
            context_menu.add_command(
                label="✓ Complete Delivery",
                command=lambda: self.complete_partial_delivery(item_id, structure_id)
            )
            
            context_menu.add_command(
                label="✗ Mark as Not Delivered",
                command=lambda: self.mark_pipe_item_not_delivered(item_id, structure_id)
            )
        else:  # Already delivered
            context_menu.add_command(
                label="✗ Mark as Not Delivered",
                command=lambda: self.mark_pipe_item_not_delivered(item_id, structure_id)
            )
        
        context_menu.add_separator()
        
        context_menu.add_command(
            label="Add/Edit Notes",
            command=lambda: self.add_pipe_notes_enhanced(item_id, structure_id, pipe_type)
        )
        
        context_menu.add_command(
            label="Edit Delivery Details",
            command=lambda: self.show_pipe_item_edit_dialog(item_id, structure_id, pipe_type)
        )
        
        context_menu.add_separator()
        
        context_menu.add_command(
            label=f"View Structure {structure_id}",
            command=lambda: self.view_structure_from_pipe_item_enhanced(structure_id)
        )
        
        # Show the menu
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def show_pipe_item_edit_dialog(self, item_id: int, structure_id: str, pipe_type: str):
        """Show comprehensive edit dialog for pipe item with delivery tracking"""
        try:
            # Get current item details
            item_details = self.db.get_pipe_item_details(item_id)
            if not item_details:
                Messagebox.show_error("Could not find pipe item details", "Error")
                return
            
            # Create edit dialog
            edit_window = ttk.Toplevel(self.root)
            edit_window.title("Edit Pipe Item")
            edit_window.geometry("500x600")
            self.center_toplevel(edit_window)
            edit_window.transient(self.root)
            edit_window.grab_set()
            
            # Main container
            main_frame = ttk.Frame(edit_window, padding=20)
            main_frame.pack(fill="both", expand=True)
            
            # Title
            ttk.Label(
                main_frame,
                text="Edit Pipe Item Details",
                font=("Helvetica", 14, "bold"),
                bootstyle="primary"
            ).pack(pady=(0, 20))
            
            # Item info (read-only)
            info_frame = ttk.Labelframe(main_frame, text="Item Information", padding=10)
            info_frame.pack(fill="x", pady=(0, 20))
            
            ttk.Label(info_frame, text=f"Structure: {structure_id}", font=("Helvetica", 10, "bold")).pack(anchor="w")
            ttk.Label(info_frame, text=f"Pipe Type: {pipe_type}").pack(anchor="w")
            ttk.Label(info_frame, text=f"Order: {item_details.get('order_number', 'Unknown')}").pack(anchor="w")
            ttk.Label(info_frame, text=f"Total Length: {item_details.get('length', 0):.2f} ft").pack(anchor="w")
            
            # Delivery details section
            delivery_frame = ttk.Labelframe(main_frame, text="Delivery Details", padding=10)
            delivery_frame.pack(fill="x", pady=(0, 20))
            delivery_frame.columnconfigure(1, weight=1)
            
            # Status
            ttk.Label(delivery_frame, text="Status:").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
            status_var = tk.StringVar(value=item_details.get('status', 'pending'))
            status_combo = ttk.Combobox(
                delivery_frame, 
                textvariable=status_var, 
                values=["pending", "ordered", "delivered"],
                state="readonly"
            )
            status_combo.grid(row=0, column=1, sticky="ew", pady=5)
            
            # Delivered length
            ttk.Label(delivery_frame, text="Delivered Length (ft):").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=5)
            delivered_entry = ttk.Entry(delivery_frame)
            delivered_entry.grid(row=1, column=1, sticky="ew", pady=5)
            delivered_entry.insert(0, str(item_details.get('delivered_length', 0)))
            
            # Delivery date
            ttk.Label(delivery_frame, text="Delivery Date:").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=5)
            date_frame = ttk.Frame(delivery_frame)
            date_frame.grid(row=2, column=1, sticky="ew", pady=5)
            date_frame.columnconfigure(0, weight=1)
            
            delivery_date_entry = ttk.Entry(date_frame)
            delivery_date_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
            
            ttk.Button(
                date_frame,
                text="📅",
                width=3,
                command=lambda: self.open_date_picker(delivery_date_entry)
            ).pack(side="right")
            
            # Status change triggers
            def on_status_change(*args):
                if status_var.get() == "delivered":
                    if not delivery_date_entry.get():
                        delivery_date_entry.delete(0, tk.END)
                        delivery_date_entry.insert(0, datetime.now().strftime("%m/%d/%Y"))
                    if not delivered_entry.get() or float(delivered_entry.get() or 0) == 0:
                        delivered_entry.delete(0, tk.END)
                        delivered_entry.insert(0, str(item_details.get('length', 0)))
            
            status_var.trace("w", on_status_change)
            
            # Notes section
            notes_frame = ttk.Labelframe(main_frame, text="Notes", padding=10)
            notes_frame.pack(fill="both", expand=True, pady=(0, 20))
            
            notes_text = tk.Text(notes_frame, height=6, wrap="word")
            notes_text.pack(fill="both", expand=True)
            
            # Pre-fill notes
            if item_details.get('notes'):
                notes_text.insert("1.0", item_details['notes'])
            
            def save_changes():
                try:
                    # Validate delivered length
                    delivered_length_str = delivered_entry.get().strip()
                    if delivered_length_str:
                        try:
                            delivered_length = float(delivered_length_str)
                            if delivered_length < 0:
                                Messagebox.show_error("Delivered length cannot be negative", "Validation Error")
                                return
                            if delivered_length > item_details.get('length', 0):
                                Messagebox.show_error("Delivered length cannot exceed total length", "Validation Error")
                                return
                        except ValueError:
                            Messagebox.show_error("Invalid delivered length value", "Validation Error")
                            return
                    else:
                        delivered_length = 0
                    
                    # Parse delivery date
                    delivery_date = None
                    if delivery_date_entry.get().strip():
                        try:
                            delivery_date = datetime.strptime(delivery_date_entry.get().strip(), "%m/%d/%Y")
                        except ValueError:
                            Messagebox.show_error("Invalid date format. Please use MM/DD/YYYY", "Date Error")
                            return
                    
                    # Get notes
                    notes_content = notes_text.get("1.0", tk.END).strip()
                    notes_value = notes_content if notes_content else None
                    
                    # Update the item
                    success = self.db.update_pipe_item_delivery_enhanced(
                        item_id=item_id,
                        delivered_length=delivered_length,
                        status=status_var.get(),
                        notes=notes_value,  
                        delivery_date=delivery_date,
                        update_notes=True  
                    )
                    
                    if success:
                        edit_window.destroy()
                        
                        # Refresh breakdown view
                        if self.pipe_orders_tree.selection():
                            order_number = self.pipe_orders_tree.item(self.pipe_orders_tree.selection()[0], "values")[0]
                            self.load_order_breakdown(order_number)
                        
                        self.calculate_project_pipe_totals()
                        self.show_status_toast("Pipe item updated successfully")
                    else:
                        Messagebox.show_error("Failed to update pipe item", "Error")
                        
                except Exception as e:
                    self.logger.error(f"Error saving pipe item changes: {e}", exc_info=True)
                    Messagebox.show_error(f"An error occurred: {str(e)}", "Error")
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill="x")
            
            ttk.Button(
                button_frame,
                text="Save Changes",
                bootstyle="primary",
                command=save_changes
            ).pack(side="left", padx=5)
            
            ttk.Button(
                button_frame,
                text="Cancel",
                bootstyle="secondary",
                command=edit_window.destroy
            ).pack(side="right", padx=5)
            
            # Focus on status combo
            status_combo.focus()
            
        except Exception as e:
            self.logger.error(f"Error showing pipe item edit dialog: {e}", exc_info=True)
            Messagebox.show_error(f"An error occurred: {str(e)}", "Error")

    def load_structure_components(self, event):
        """Load components for the selected structure"""
        # Clear existing components
        for item in self.component_tree.get_children():
            self.component_tree.delete(item)
        
        # Get selected structure
        selection = self.component_structure_tree.selection()
        if not selection:
            return
        
        structure_id = self.component_structure_tree.item(selection[0], "values")[0]
        
        # Get project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            return
        
        # Get components for this structure
        components = self.db.get_structure_components(structure_id, project.id)
        
        # Add to treeview
        for component in components:
            # Format dates for display
            order_date = component.order_date.strftime("%Y-%m-%d") if component.order_date else ""
            expected_date = component.expected_delivery_date.strftime("%Y-%m-%d") if component.expected_delivery_date else ""
            delivery_date = component.actual_delivery_date.strftime("%Y-%m-%d") if component.actual_delivery_date else ""
            
            self.component_tree.insert(
                "",
                "end",
                values=(
                    component.component_type_name,
                    component.status,
                    order_date,
                    expected_date,
                    delivery_date,
                    component.notes or ""
                ),
                tags=(str(component.id),)  # Store the component ID as a tag
            )

    def generate_delivery_report(self):
        """Generate a comprehensive delivery report"""
        # Get project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            return
        
        # Get all structures and their components
        structures = self.db.get_all_structures(project.id)
        
        # Create report window
        report_window = ttk.Toplevel(self.root)
        report_window.title(f"Delivery Report: {self.current_project}")
        report_window.geometry("900x700")
        self.cente_toplevel(report_window)
        
        # Main container
        main_frame = ttk.Frame(report_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Report header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(
            header_frame, 
            text=f"Component Delivery Report: {self.current_project}",
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        ).pack(side="left")
        
        ttk.Label(
            header_frame, 
            text=f"Generated: {datetime.now().strftime('%m/%d/%Y %H:%M')}",
            bootstyle="secondary"
        ).pack(side="right")
        
        # Summary section
        summary_frame = ttk.Labelframe(main_frame, text="Project Summary", padding=10)
        summary_frame.pack(fill="x", pady=(0, 20))
        
        # Calculate overall statistics
        total_structures = len(structures)
        total_components = 0
        status_counts = {"pending": 0, "ordered": 0, "approved": 0, "delivered": 0, "installed": 0}
        
        for structure in structures:
            components = self.db.get_structure_components(structure.structure_id, project.id)
            total_components += len(components)
            for component in components:
                if component.status in status_counts:
                    status_counts[component.status] += 1
        
        # Display summary
        summary_text = f"Total Structures: {total_structures}  |  Total Components: {total_components}  |  "
        summary_text += f"Pending: {status_counts['pending']}  |  Ordered: {status_counts['ordered']}  |  "
        summary_text += f"Approved: {status_counts['approved']}  |  Delivered: {status_counts['delivered']}  |  "
        summary_text += f"Installed: {status_counts['installed']}"
        
        ttk.Label(summary_frame, text=summary_text, font=("Helvetica", 10)).pack()
        
        # Detailed report
        detail_frame = ttk.Labelframe(main_frame, text="Detailed Component Status", padding=10)
        detail_frame.pack(fill="both", expand=True)
        
        # Create treeview for detailed report
        columns = ("STRUCTURE", "TYPE", "COMPONENT", "STATUS", "ORDERED", "EXPECTED", "DELIVERED")
        report_tree = ttk.Treeview(detail_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        report_tree.heading("STRUCTURE", text="Structure")
        report_tree.heading("TYPE", text="Type")
        report_tree.heading("COMPONENT", text="Component")
        report_tree.heading("STATUS", text="Status")
        report_tree.heading("ORDERED", text="Order Date")
        report_tree.heading("EXPECTED", text="Expected")
        report_tree.heading("DELIVERED", text="Delivered")
        
        report_tree.column("STRUCTURE", width=100)
        report_tree.column("TYPE", width=80)
        report_tree.column("COMPONENT", width=100)
        report_tree.column("STATUS", width=80)
        report_tree.column("ORDERED", width=100)
        report_tree.column("EXPECTED", width=100)
        report_tree.column("DELIVERED", width=100)
        
        # Configure status tags
        report_tree.tag_configure("pending", background="#fff3cd")
        report_tree.tag_configure("ordered", background="#cce7ff")
        report_tree.tag_configure("approved", background="#e2e3e5")
        report_tree.tag_configure("delivered", background="#d1ecf1")
        report_tree.tag_configure("installed", background="#d4edda")
        
        # Add scrollbar
        report_scrollbar = ttk.Scrollbar(detail_frame, orient="vertical", command=report_tree.yview)
        report_tree.configure(yscrollcommand=report_scrollbar.set)
        
        # Populate report
        for structure in structures:
            components = self.db.get_structure_components(structure.structure_id, project.id)
            
            if not components:
                # Show structures with no components
                report_tree.insert(
                    "", "end",
                    values=(structure.structure_id, structure.structure_type, "No Components", "—", "—", "—", "—"),
                    tags=("pending",)
                )
            else:
                for component in components:
                    order_date = component.order_date.strftime("%m/%d/%Y") if component.order_date else "—"
                    expected_date = component.expected_delivery_date.strftime("%m/%d/%Y") if component.expected_delivery_date else "—"
                    delivery_date = component.actual_delivery_date.strftime("%m/%d/%Y") if component.actual_delivery_date else "—"
                    
                    report_tree.insert(
                        "", "end",
                        values=(
                            structure.structure_id,
                            structure.structure_type,
                            component.component_type_name,
                            component.status.title(),
                            order_date,
                            expected_date,
                            delivery_date
                        ),
                        tags=(component.status,)
                    )
        
        # Pack report tree and scrollbar
        report_tree.pack(side="left", fill="both", expand=True)
        report_scrollbar.pack(side="right", fill="y")
        
        # Export buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        ttk.Button(
            button_frame, 
            text="Export to CSV", 
            bootstyle="success",
            command=lambda: self.export_component_status_csv(components, report_tree)
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame, 
            text="Print Report", 
            bootstyle="info",
            command=lambda: Messagebox.show_info("Print functionality coming soon", "Feature Coming Soon")
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame, 
            text="Close", 
            bootstyle="secondary",
            command=report_window.destroy
        ).pack(side="right", padx=5)

    def on_component_double_click(self, event):
        """Handle double-click on component for quick status update"""
        selection = self.component_tree.selection()
        if not selection:
            return
        
        # Quick status progression
        values = self.component_tree.item(selection[0], "values")
        current_status = values[1].lower()
        
        # Define status progression
        status_progression = {
            "pending": "ordered",
            "ordered": "approved", 
            "approved": "delivered",
            "delivered": "installed"
        }
        
        if current_status in status_progression:
            next_status = status_progression[current_status]
            
            # Quick confirmation
            confirm = Messagebox.yesno(
                f"Change status from '{current_status.title()}' to '{next_status.title()}'?",
                "Quick Status Update"
            )
            
            if confirm:
                component_id = int([tag for tag in self.component_tree.item(selection[0], "tags") if tag.isdigit()][0])
                
                # Set delivery date if changing to delivered/installed
                delivery_date = None
                if next_status in ["delivered", "installed"]:
                    delivery_date = datetime.now()
                
                success = self.db.update_component_status(component_id, next_status, None, delivery_date)
                
                if success:
                    # Refresh current view
                    if self.component_structure_tree.selection():
                        structure_id = self.component_structure_tree.item(
                            self.component_structure_tree.selection()[0], "values")[0]
                        self.load_structure_components_enhanced(structure_id)
                        self.refresh_component_status()
                else:
                    Messagebox.show_error("Failed to update component status", "Error")

    def filter_pipe_orders(self, event=None):
        """Filter pipe orders based on selected criteria"""
        filter_value = self.pipe_filter_var.get()
        
        # Clear existing items
        for item in self.pipe_orders_tree.get_children():
            self.pipe_orders_tree.delete(item)
        
        # Get project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            return
        
        # Get all pipe orders
        all_orders = self.db.get_pipe_orders(project.id)
        
        # Filter based on selected criteria
        filtered_orders = []
        
        if filter_value == "All Orders":
            filtered_orders = all_orders
        elif filter_value == "Pending":
            filtered_orders = [order for order in all_orders if order.get('status', '').lower() == 'pending']
        elif filter_value == "Ordered":
            filtered_orders = [order for order in all_orders if order.get('status', '').lower() == 'ordered']
        elif filter_value == "In Transit":
            filtered_orders = [order for order in all_orders if order.get('status', '').lower() == 'in_transit']
        elif filter_value == "Delivered":
            filtered_orders = [order for order in all_orders if order.get('status', '').lower() == 'delivered']
        elif filter_value == "By Pipe Type":
            # Group by pipe type - show unique pipe types
            pipe_type_groups = {}
            for order in all_orders:
                pipe_types = order.get('pipe_types', '').split(',')
                for pipe_type in pipe_types:
                    pipe_type = pipe_type.strip()
                    if pipe_type and pipe_type not in pipe_type_groups:
                        pipe_type_groups[pipe_type] = []
                    if pipe_type:
                        pipe_type_groups[pipe_type].append(order)
            
            # Show grouped results
            for pipe_type, orders in pipe_type_groups.items():
                if pipe_type:
                    # Add a separator for each pipe type
                    self.pipe_orders_tree.insert(
                        "", "end",
                        values=(f"── {pipe_type} ──", "", "", "", f"{len(orders)} orders", ""),
                        tags=("separator",)
                    )
                    filtered_orders.extend(orders)
        
        # Add filtered orders to treeview
        for order in filtered_orders:
            # Format order date
            order_date = order.get('order_date', '')
            if order_date:
                try:
                    if isinstance(order_date, str):
                        order_date = datetime.fromisoformat(order_date).strftime("%m/%d/%Y")
                    else:
                        order_date = order_date.strftime("%m/%d/%Y")
                except:
                    order_date = str(order_date)
            
            # Determine status tag
            status = order.get('status', 'pending').lower()
            tag = status if status in ['pending', 'ordered', 'in_transit', 'delivered'] else 'pending'
            
            self.pipe_orders_tree.insert(
                "", "end",
                values=(
                    order.get('order_number', ''),
                    order.get('pipe_type', ''),
                    order.get('diameter', ''),
                    f"{order.get('total_length', 0):.2f}",
                    order.get('status', '').title(),
                    order_date
                ),
                tags=(tag,)
            )

    def on_pipe_order_selected(self, event):
        """Handle pipe order selection to show details"""
        selection = self.pipe_orders_tree.selection()
        if not selection:
            self.selected_order_label.config(text="None")
            self.clear_order_breakdown()
            return
        
        values = self.pipe_orders_tree.item(selection[0], "values")
        order_number = values[0]
        
        # Skip separator rows
        if "──" in order_number:
            self.selected_order_label.config(text="None")
            self.clear_order_breakdown()
            return
        
        self.selected_order_label.config(text=order_number)
        
        # Load order breakdown
        self.load_order_breakdown(order_number)

    def load_order_breakdown(self, order_number):
        """Load breakdown details for selected order"""
        # Clear existing items
        self.clear_order_breakdown()
        
        try:
            # Get project ID
            project = self.db.get_project_by_name(self.current_project, self.current_user.id)
            if not project:
                return
            
            # Get all pipe orders to find the order ID
            pipe_orders = self.db.get_pipe_orders(project.id)
            order_id = None
            
            for order in pipe_orders:
                if order.get('order_number') == order_number:
                    order_id = order.get('id')
                    break
            
            if not order_id:
                self.order_breakdown_tree.insert(
                    "", "end",
                    values=("Error", "—", "—", "—", "—", "Order not found"),
                    tags=("not_delivered",)
                )
                return
            
            # Get order items
            order_items = self.db.get_pipe_order_items(order_id)
            
            if not order_items:
                self.order_breakdown_tree.insert(
                    "", "end",
                    values=("No items", "—", "—", "—", "—", "No pipe items found for this order"),
                    tags=("not_delivered",)
                )
                return
            
            # Add items to breakdown tree
            for item in order_items:
                # Determine delivery status
                delivered_length = item.get('delivered_length', 0)
                total_length = item.get('length', 0)
                
                if delivered_length >= total_length:
                    delivered_text = "Yes"
                    tag = "delivered"
                elif delivered_length > 0:
                    delivered_text = f"Partial ({delivered_length:.1f}ft)"
                    tag = "partial"
                else:
                    delivered_text = "No"
                    tag = "not_delivered"
                
                # Format diameter
                diameter = item.get('diameter')
                diameter_text = f"{int(diameter)}\"" if diameter else "Unknown"
                
                self.order_breakdown_tree.insert(
                    "", "end",
                    values=(
                        item.get('structure_id', ''),
                        item.get('pipe_type', ''),
                        diameter_text,
                        f"{total_length:.2f}",
                        delivered_text,
                        item.get('notes', '') or ""
                    ),
                    tags=(str(item.get('id', '')), tag)  # Store item ID as tag for context menu
                )
        
        except Exception as e:
            self.logger.error(f"Error loading order breakdown: {e}", exc_info=True)
            self.order_breakdown_tree.insert(
                "", "end",
                values=("Error", "—", "—", "—", "—", f"Error loading breakdown: {str(e)}"),
                tags=("not_delivered",)
            )

    def clear_order_breakdown(self):
        """Clear the order breakdown view"""
        if hasattr(self, 'order_breakdown_tree'):
            for item in self.order_breakdown_tree.get_children():
                self.order_breakdown_tree.delete(item)

    def create_new_pipe_order(self):
        """Create a new pipe order from scratch"""
        # Create order dialog
        order_window = ttk.Toplevel(self.root)
        order_window.title("Create New Pipe Order")
        order_window.geometry("500x400")
        self.center_toplevel(order_window)
        order_window.transient(self.root)
        order_window.grab_set()
        
        # Main container
        main_frame = ttk.Frame(order_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(
            main_frame, 
            text="Create New Pipe Order", 
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        ).pack(pady=(0, 20))
        
        # Order information form
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill="x", pady=(0, 20))
        form_frame.columnconfigure(1, weight=1)
        
        # Order number
        ttk.Label(form_frame, text="Order Number:").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=8)
        order_number_entry = ttk.Entry(form_frame)
        order_number_entry.grid(row=0, column=1, sticky="ew", pady=8)
        
        # Generate default order number
        from datetime import datetime
        default_order_num = f"PO-{datetime.now().strftime('%Y%m%d')}-NEW"
        order_number_entry.insert(0, default_order_num)
        
        # Supplier
        ttk.Label(form_frame, text="Supplier:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=8)
        supplier_entry = ttk.Entry(form_frame)
        supplier_entry.grid(row=1, column=1, sticky="ew", pady=8)
        
        # Expected delivery date
        ttk.Label(form_frame, text="Expected Delivery:").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=8)
        delivery_date_frame = ttk.Frame(form_frame)
        delivery_date_frame.grid(row=2, column=1, sticky="ew", pady=8)
        delivery_date_frame.columnconfigure(0, weight=1)
        
        delivery_date_entry = ttk.Entry(delivery_date_frame)
        delivery_date_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ttk.Button(
            delivery_date_frame,
            text="📅",
            width=3,
            command=lambda: self.open_date_picker(delivery_date_entry)
        ).pack(side="right")
        
        # Notes
        ttk.Label(form_frame, text="Notes:").grid(row=3, column=0, sticky="nw", padx=(0, 10), pady=8)
        notes_text = tk.Text(form_frame, height=4, wrap="word")
        notes_text.grid(row=3, column=1, sticky="ew", pady=8)
        
        # Instructions
        instructions_frame = ttk.Labelframe(main_frame, text="Instructions", padding=10)
        instructions_frame.pack(fill="x", pady=(0, 20))
        
        instructions_text = """1. Enter basic order information above
    2. After creating the order, you can add pipe items by:
    - Selecting structures in the Structures tab
    - Right-clicking and choosing "Order Pipe"
    - Or manually adding items in the Pipe Tracking tab"""
        
        ttk.Label(
            instructions_frame,
            text=instructions_text,
            justify="left",
            wraplength=450
        ).pack(anchor="w")
        
        def create_order():
            try:
                order_number = order_number_entry.get().strip()
                supplier = supplier_entry.get().strip()
                delivery_date_str = delivery_date_entry.get().strip()
                notes_content = notes_text.get("1.0", tk.END).strip()
                notes_value = notes_content if notes_content else None

                # Validation
                if not order_number:
                    Messagebox.show_error("Please enter an order number", "Validation Error")
                    return
                
                # Parse delivery date
                delivery_date = None
                if delivery_date_str:
                    try:
                        delivery_date = datetime.strptime(delivery_date_str, "%m/%d/%Y")
                    except ValueError:
                        Messagebox.show_error("Invalid date format. Please use MM/DD/YYYY", "Date Error")
                        return
                
                # Get project ID
                project = self.db.get_project_by_name(self.current_project, self.current_user.id)
                if not project:
                    Messagebox.show_error("Could not find current project", "Project Error")
                    return
                
                # Create the pipe order in database (without pipe groups for manual order)
                success = self.db.create_pipe_order(
                    order_number=order_number,
                    supplier=supplier,
                    expected_delivery_date=delivery_date,
                    notes=notes_value,
                    pipe_groups=None,
                    project_id=project.id
                )
                
                if success:
                    Messagebox.show_info(f"Pipe order '{order_number}' created successfully", "Success")
                    order_window.destroy()
                    # Refresh pipe orders
                    self.refresh_pipe_orders()
                else:
                    Messagebox.show_error("Failed to create pipe order. Order number may already exist.", "Error")
                    
            except Exception as e:
                self.logger.error(f"Error creating new pipe order: {e}", exc_info=True)
                Messagebox.show_error(f"An error occurred: {str(e)}", "Error")
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(
            button_frame,
            text="Create Order",
            bootstyle="primary",
            command=create_order
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            bootstyle="secondary",
            command=order_window.destroy
        ).pack(side="right", padx=5)

    def update_pipe_order_status(self):
        """Update the status of selected pipe order"""
        selection = self.pipe_orders_tree.selection()
        if not selection:
            Messagebox.show_warning("Please select a pipe order first", "No Order Selected")
            return
        
        values = self.pipe_orders_tree.item(selection[0], "values")
        order_number = values[0]
        
        # Skip separator rows
        if "──" in order_number:
            Messagebox.show_warning("Please select a valid pipe order", "Invalid Selection")
            return
        
        # Get order ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            return
        
        pipe_orders = self.db.get_pipe_orders(project.id)
        order_id = None
        current_status = None
        
        for order in pipe_orders:
            if order.get('order_number') == order_number:
                order_id = order.get('id')
                current_status = order.get('status', 'pending')
                break
        
        if not order_id:
            Messagebox.show_error("Order not found", "Error")
            return
        
        # Create status update dialog
        status_window = ttk.Toplevel(self.root)
        status_window.title("Update Order Status")
        status_window.geometry("450x350")
        self.center_toplevel(status_window)
        status_window.transient(self.root)
        status_window.grab_set()
        
        # Main container
        main_frame = ttk.Frame(status_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        ttk.Label(
            main_frame,
            text=f"Update Status for Order: {order_number}",
            font=("Helvetica", 14, "bold"),
            bootstyle="primary"
        ).pack(pady=(0, 20))
        
        # Current status display
        current_frame = ttk.Frame(main_frame)
        current_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(current_frame, text="Current Status:", font=("Helvetica", 10, "bold")).pack(side="left")
        ttk.Label(current_frame, text=current_status.title(), bootstyle="info").pack(side="left", padx=(10, 0))
        
        # Status selection
        ttk.Label(main_frame, text="New Status:").pack(anchor="w", pady=(0, 5))
        status_var = tk.StringVar(value=current_status)
        status_combo = ttk.Combobox(
            main_frame,
            textvariable=status_var,
            values=["pending", "ordered", "in_transit", "delivered"],
            state="readonly"
        )
        status_combo.pack(fill="x", pady=(0, 15))
        
        # Delivery date
        ttk.Label(main_frame, text="Delivery Date (if delivered):").pack(anchor="w", pady=(0, 5))
        delivery_date_frame = ttk.Frame(main_frame)
        delivery_date_frame.pack(fill="x", pady=(0, 15))
        
        delivery_date_entry = ttk.Entry(delivery_date_frame)
        delivery_date_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ttk.Button(
            delivery_date_frame,
            text="📅",
            width=3,
            command=lambda: self.open_date_picker(delivery_date_entry)
        ).pack(side="right")
        
        # Auto-fill today's date if status is delivered
        def on_status_change(*args):
            if status_var.get() == "delivered" and not delivery_date_entry.get():
                from datetime import datetime
                delivery_date_entry.delete(0, tk.END)
                delivery_date_entry.insert(0, datetime.now().strftime("%m/%d/%Y"))
        
        status_var.trace("w", on_status_change)
        
        # Notes
        ttk.Label(main_frame, text="Notes:").pack(anchor="w", pady=(0, 5))
        notes_text = tk.Text(main_frame, height=4, wrap="word")
        notes_text.pack(fill="both", expand=True, pady=(0, 20))
        
        def save_status():
            try:
                new_status = status_var.get()
                delivery_date_str = delivery_date_entry.get().strip()
                notes = notes_text.get("1.0", tk.END).strip()
                
                # Parse delivery date
                delivery_date = None
                if delivery_date_str:
                    try:
                        delivery_date = datetime.strptime(delivery_date_str, "%m/%d/%Y")
                    except ValueError:
                        Messagebox.show_error("Invalid date format. Please use MM/DD/YYYY", "Date Error")
                        return
                
                # Update order status
                success = self.db.update_pipe_order_status(
                    order_id=order_id,
                    status=new_status,
                    delivery_date=delivery_date,
                    notes=notes if notes else None
                )
                
                if success:
                    Messagebox.show_info(f"Status updated to '{new_status.title()}'", "Success")
                    status_window.destroy()
                    self.refresh_pipe_orders()
                    
                    # Refresh breakdown if this order is selected
                    if self.pipe_orders_tree.selection():
                        current_order = self.pipe_orders_tree.item(self.pipe_orders_tree.selection()[0], "values")[0]
                        if current_order == order_number:
                            self.load_order_breakdown(order_number)
                else:
                    Messagebox.show_error("Failed to update status", "Error")
            
            except Exception as e:
                self.logger.error(f"Error updating pipe order status: {e}", exc_info=True)
                Messagebox.show_error(f"An error occurred: {str(e)}", "Error")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(
            button_frame,
            text="Save",
            bootstyle="primary",
            command=save_status
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            bootstyle="secondary",
            command=status_window.destroy
        ).pack(side="right", padx=5)

    def mark_pipe_delivered(self):
        """Mark selected pipe as delivered"""
        selection = self.order_breakdown_tree.selection()
        if not selection:
            Messagebox.show_warning("Please select a pipe item first", "No Item Selected")
            return
        
        values = self.order_breakdown_tree.item(selection[0], "values")
        structure_id = values[0]
        pipe_type = values[1] 
        total_length_str = values[3]
        
        # Get item ID from tags
        tags = self.order_breakdown_tree.item(selection[0], "tags")
        item_id = None
        for tag in tags:
            if tag.isdigit():
                item_id = int(tag)
                break
        
        if not item_id:
            Messagebox.show_error("Could not identify pipe item", "Error")
            return
        
        try:
            total_length = float(total_length_str)
        except ValueError:
            Messagebox.show_error("Invalid length value", "Error")
            return
        
        # Get the order_id to check for completion later
        order_id = None
        if self.pipe_orders_tree.selection():
            order_number = self.pipe_orders_tree.item(self.pipe_orders_tree.selection()[0], "values")[0]
            project = self.db.get_project_by_name(self.current_project, self.current_user.id)
            if project:
                pipe_orders = self.db.get_pipe_orders(project.id)
                for order in pipe_orders:
                    if order.get('order_number') == order_number:
                        order_id = order.get('id')
                        break
        
        # Create delivery dialog
        delivery_window = ttk.Toplevel(self.root)
        delivery_window.title("Mark Pipe as Delivered")
        delivery_window.geometry("403x403")
        self.center_toplevel(delivery_window)
        delivery_window.transient(self.root)
        delivery_window.grab_set()
        
        # Main container
        main_frame = ttk.Frame(delivery_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(
            main_frame,
            text="Mark Pipe as Delivered",
            font=("Helvetica", 14, "bold"),
            bootstyle="primary"
        ).pack(pady=(0, 20))
        
        # Item info
        info_frame = ttk.Labelframe(main_frame, text="Pipe Item", padding=10)
        info_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(info_frame, text=f"Structure: {structure_id}", font=("Helvetica", 10, "bold")).pack(anchor="w")
        ttk.Label(info_frame, text=f"Pipe Type: {pipe_type}").pack(anchor="w")
        ttk.Label(info_frame, text=f"Ordered Length: {total_length} ft").pack(anchor="w")
        
        # Delivery details
        details_frame = ttk.Frame(main_frame)
        details_frame.pack(fill="x", pady=(0, 20))
        details_frame.columnconfigure(1, weight=1)
        
        # Delivered length
        ttk.Label(details_frame, text="Delivered Length (ft):").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
        delivered_length_entry = ttk.Entry(details_frame)
        delivered_length_entry.grid(row=0, column=1, sticky="ew", pady=5)
        delivered_length_entry.insert(0, str(total_length))  # Default to full length
        
        # Notes
        ttk.Label(details_frame, text="Delivery Notes:").grid(row=1, column=0, sticky="nw", padx=(0, 10), pady=5)
        notes_text = tk.Text(details_frame, height=3, wrap="word")
        notes_text.grid(row=1, column=1, sticky="ew", pady=5)
        
        def save_delivery():
            try:
                delivered_length_str = delivered_length_entry.get().strip()
                notes = notes_text.get("1.0", tk.END).strip()
                
                # Validation
                if not delivered_length_str:
                    Messagebox.show_error("Please enter delivered length", "Validation Error")
                    return
                
                try:
                    delivered_length = float(delivered_length_str)
                except ValueError:
                    Messagebox.show_error("Invalid length value", "Validation Error")
                    return
                
                if delivered_length < 0:
                    Messagebox.show_error("Delivered length cannot be negative", "Validation Error")
                    return
                
                # Determine status based on delivered vs ordered length
                if delivered_length >= total_length:
                    status = "delivered"
                elif delivered_length > 0:
                    status = "partial"
                else:
                    status = "pending"
                
                # Update pipe item delivery
                success = self.db.update_pipe_item_delivery(
                    item_id=item_id,
                    delivered_length=delivered_length,
                    status=status,
                    notes=notes if notes else None
                )
                
                if success:
                    Messagebox.show_info("Pipe delivery updated successfully", "Success")
                    delivery_window.destroy()
                    
                    # Refresh breakdown view
                    if self.pipe_orders_tree.selection():
                        order_number = self.pipe_orders_tree.item(self.pipe_orders_tree.selection()[0], "values")[0]
                        self.load_order_breakdown(order_number)

                    # Refresh project totals
                    self.calculate_project_pipe_totals()
                    
                    # Check if this completes the order
                    if order_id:
                        self.check_and_update_order_status(order_id)
                else:
                    Messagebox.show_error("Failed to update delivery", "Error")
            
            except Exception as e:
                self.logger.error(f"Error marking pipe as delivered: {e}", exc_info=True)
                Messagebox.show_error(f"An error occurred: {str(e)}", "Error")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(
            button_frame,
            text="Save",
            bootstyle="primary",
            command=save_delivery
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            bootstyle="secondary",
            command=delivery_window.destroy
        ).pack(side="right", padx=5)

    def add_pipe_notes_enhanced(self, item_id: int, structure_id: str, pipe_type: str):
        """Enhanced pipe notes dialog with better UX and history tracking"""
        try:
            # Get current notes
            item_details = self.db.get_pipe_item_details(item_id)
            if not item_details:
                Messagebox.show_error("Could not find pipe item details", "Error")
                return
            
            current_notes = item_details.get('notes', '') or ''
            
            # Create notes dialog
            notes_window = ttk.Toplevel(self.root)
            notes_window.title("Pipe Item Notes")
            notes_window.geometry("500x615")
            self.center_toplevel(notes_window)
            notes_window.transient(self.root)
            notes_window.grab_set()
            
            # Main container
            main_frame = ttk.Frame(notes_window, padding=20)
            main_frame.pack(fill="both", expand=True)
            
            # Title
            ttk.Label(
                main_frame,
                text="Edit Pipe Item Notes",
                font=("Helvetica", 14, "bold"),
                bootstyle="primary"
            ).pack(pady=(0, 20))
            
            # Item info
            info_frame = ttk.Labelframe(main_frame, text="Pipe Item Details", padding=10)
            info_frame.pack(fill="x", pady=(0, 20))
            
            ttk.Label(info_frame, text=f"Structure: {structure_id}", font=("Helvetica", 10, "bold")).pack(anchor="w")
            ttk.Label(info_frame, text=f"Pipe Type: {pipe_type}").pack(anchor="w")
            ttk.Label(info_frame, text=f"Order: {item_details.get('order_number', 'Unknown')}").pack(anchor="w")
            
            # Status info
            status_info = f"Status: {item_details.get('status', 'unknown').title()}"
            delivered = item_details.get('delivered_length', 0)
            total = item_details.get('length', 0)
            if delivered > 0:
                status_info += f" | Delivered: {delivered:.2f}/{total:.2f} ft"
            
            ttk.Label(info_frame, text=status_info, bootstyle="info").pack(anchor="w")
            
            # Notes section
            notes_frame = ttk.Labelframe(main_frame, text="Notes", padding=10)
            notes_frame.pack(fill="x", pady=(0, 15))
            
            # Notes text area with scrollbar
            notes_container = ttk.Frame(notes_frame)
            notes_container.pack(fill="x")
            
            notes_text = tk.Text(notes_container, wrap="word", font=("Helvetica", 11), height=8)
            notes_scrollbar = ttk.Scrollbar(notes_container, orient="vertical", command=notes_text.yview)
            notes_text.configure(yscrollcommand=notes_scrollbar.set)
            
            notes_text.pack(side="left", fill="x", expand=True)
            notes_scrollbar.pack(side="right", fill="y")
            
            # Pre-fill with existing notes
            if current_notes:
                notes_text.insert("1.0", current_notes)
            
            # Quick note templates
            quick_notes_frame = ttk.Frame(main_frame)
            quick_notes_frame.pack(fill="x", pady=(0, 20))
            
            ttk.Label(quick_notes_frame, text="Quick Templates:", font=("Helvetica", 10, "bold")).pack(anchor="w")
            
            templates_frame = ttk.Frame(quick_notes_frame)
            templates_frame.pack(fill="x", pady=(5, 0))
            
            def add_template_note(template_text):
                current = notes_text.get("1.0", tk.END).strip()
                timestamp = datetime.now().strftime("%m/%d/%Y %H:%M")
                new_note = f"[{timestamp}] {template_text}"
                
                if current:
                    notes_text.insert(tk.END, f"\n{new_note}")
                else:
                    notes_text.insert("1.0", new_note)
                
                # Scroll to end
                notes_text.see(tk.END)
            
            # Template buttons in rows
            templates = [
                ("Delivered on time", "On-time delivery completed"),
                ("Delayed delivery", "Delivery delayed"),
                ("Quality issue", "Quality concern noted"),
                ("Partial load", "Partial delivery received"),
                ("Weather delay", "Delayed due to weather"),
                ("Site access issue", "Delivery access problem")
            ]
            
            row_frame = None
            for i, (btn_text, template_text) in enumerate(templates):
                if i % 3 == 0:  # New row every 3 buttons
                    row_frame = ttk.Frame(templates_frame)
                    row_frame.pack(fill="x", pady=2)
                
                ttk.Button(
                    row_frame,
                    text=btn_text,
                    bootstyle="info-outline",
                    command=lambda t=template_text: add_template_note(t)
                ).pack(side="left", padx=2)
            
            # Add timestamp button
            def add_timestamp():
                timestamp = datetime.now().strftime("%m/%d/%Y %H:%M")
                current_pos = notes_text.index(tk.INSERT)
                notes_text.insert(current_pos, f"[{timestamp}] ")
            
            timestamp_frame = ttk.Frame(main_frame)
            timestamp_frame.pack(fill="x", pady=(0, 20))
            
            ttk.Button(
                timestamp_frame,
                text="Insert Timestamp",
                bootstyle="secondary-outline",
                command=add_timestamp
            ).pack(side="left")
            
            def save_notes():  
                try:
                    notes = notes_text.get("1.0", tk.END).strip()
                    
                    # Convert empty string to None to properly clear notes in database
                    notes_value = notes if notes else None

                    success = self.db.update_pipe_item_delivery_enhanced(
                        item_id=item_id,
                        notes=notes_value,
                        update_notes=True  
                    )
                    
                    if success:
                        notes_window.destroy()
                        
                        # Refresh breakdown view
                        if self.pipe_orders_tree.selection():
                            order_number = self.pipe_orders_tree.item(self.pipe_orders_tree.selection()[0], "values")[0]
                            self.load_order_breakdown(order_number)
                        
                        self.show_status_toast("Notes updated successfully")
                    else:
                        Messagebox.show_error("Failed to update notes", "Error")
                
                except Exception as e:
                    self.logger.error(f"Error saving pipe notes: {e}", exc_info=True)
                    Messagebox.show_error(f"An error occurred: {str(e)}", "Error")
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill="x")
            
            ttk.Button(
                button_frame,
                text="Save Notes",
                bootstyle="primary",
                command=save_notes
            ).pack(side="left", padx=5)
            
            ttk.Button(
                button_frame,
                text="Cancel",
                bootstyle="secondary",
                command=notes_window.destroy
            ).pack(side="right", padx=5)
            
            # Focus on notes text
            notes_text.focus()
            
        except Exception as e:
            self.logger.error(f"Error showing enhanced pipe notes dialog: {e}", exc_info=True)
            Messagebox.show_error(f"An error occurred: {str(e)}", "Error")

    def generate_pipe_delivery_report(self):
        """Generate a comprehensive pipe delivery report"""
        # Get project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            return
        
        # Get all pipe orders
        pipe_orders = self.db.get_pipe_orders(project.id)
        
        if not pipe_orders:
            Messagebox.show_info("No pipe orders found for this project", "No Data")
            return
        
        # Create report window
        report_window = ttk.Toplevel(self.root)
        report_window.title(f"Pipe Delivery Report: {self.current_project}")
        report_window.geometry("1000x700")
        self.center_toplevel(report_window)
        
        # Main container
        main_frame = ttk.Frame(report_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Report header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(
            header_frame, 
            text=f"Pipe Delivery Report: {self.current_project}",
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        ).pack(side="left")
        
        ttk.Label(
            header_frame, 
            text=f"Generated: {datetime.now().strftime('%m/%d/%Y %H:%M')}",
            bootstyle="secondary"
        ).pack(side="right")
        
        # Summary section
        summary_frame = ttk.Labelframe(main_frame, text="Project Summary", padding=10)
        summary_frame.pack(fill="x", pady=(0, 20))
        
        # Calculate overall statistics
        total_orders = len(pipe_orders)
        total_length = sum(order.get('total_length', 0) for order in pipe_orders)
        
        status_counts = {"pending": 0, "ordered": 0, "in_transit": 0, "delivered": 0}
        for order in pipe_orders:
            status = order.get('status', 'pending').lower()
            if status in status_counts:
                status_counts[status] += 1
        
        # Display summary
        summary_text = f"Total Orders: {total_orders}  |  Total Pipe Length: {total_length:.2f} ft  |  "
        summary_text += f"Pending: {status_counts['pending']}  |  Ordered: {status_counts['ordered']}  |  "
        summary_text += f"In Transit: {status_counts['in_transit']}  |  Delivered: {status_counts['delivered']}"
        
        ttk.Label(summary_frame, text=summary_text, font=("Helvetica", 10)).pack()
        
        # Detailed report
        detail_frame = ttk.Labelframe(main_frame, text="Detailed Order Status", padding=10)
        detail_frame.pack(fill="both", expand=True)
        
        # Create treeview for detailed report
        columns = ("ORDER", "SUPPLIER", "PIPE_TYPE", "DIAMETER", "LENGTH", "STATUS", "ORDER_DATE", "EXPECTED", "DELIVERED")
        report_tree = ttk.Treeview(detail_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        report_tree.heading("ORDER", text="Order #")
        report_tree.heading("SUPPLIER", text="Supplier")
        report_tree.heading("PIPE_TYPE", text="Pipe Type")
        report_tree.heading("DIAMETER", text="Diameter")
        report_tree.heading("LENGTH", text="Length (ft)")
        report_tree.heading("STATUS", text="Status")
        report_tree.heading("ORDER_DATE", text="Order Date")
        report_tree.heading("EXPECTED", text="Expected")
        report_tree.heading("DELIVERED", text="Delivered")
        
        report_tree.column("ORDER", width=100)
        report_tree.column("SUPPLIER", width=120)
        report_tree.column("PIPE_TYPE", width=120)
        report_tree.column("DIAMETER", width=80)
        report_tree.column("LENGTH", width=100)
        report_tree.column("STATUS", width=80)
        report_tree.column("ORDER_DATE", width=100)
        report_tree.column("EXPECTED", width=100)
        report_tree.column("DELIVERED", width=100)
        
        # Configure status tags
        report_tree.tag_configure("pending", background="#fff3cd")
        report_tree.tag_configure("ordered", background="#cce7ff")
        report_tree.tag_configure("in_transit", background="#e2e3e5")
        report_tree.tag_configure("delivered", background="#d4edda")
        
        # Add scrollbar
        report_scrollbar = ttk.Scrollbar(detail_frame, orient="vertical", command=report_tree.yview)
        report_tree.configure(yscrollcommand=report_scrollbar.set)
        
        # Populate report
        for order in pipe_orders:
            # Format dates
            order_date = ""
            if order.get('order_date'):
                try:
                    order_date = datetime.fromisoformat(order['order_date']).strftime("%m/%d/%Y")
                except:
                    order_date = str(order.get('order_date', ''))
            
            expected_date = ""
            if order.get('expected_delivery_date'):
                try:
                    expected_date = datetime.fromisoformat(order['expected_delivery_date']).strftime("%m/%d/%Y")
                except:
                    expected_date = str(order.get('expected_delivery_date', ''))
            
            delivered_date = ""
            if order.get('actual_delivery_date'):
                try:
                    delivered_date = datetime.fromisoformat(order['actual_delivery_date']).strftime("%m/%d/%Y")
                except:
                    delivered_date = str(order.get('actual_delivery_date', ''))
            
            status = order.get('status', 'pending').lower()
            
            report_tree.insert(
                "", "end",
                values=(
                    order.get('order_number', ''),
                    order.get('supplier', ''),
                    order.get('pipe_type', ''),
                    order.get('diameter', ''),
                    f"{order.get('total_length', 0):.2f}",
                    order.get('status', '').title(),
                    order_date,
                    expected_date,
                    delivered_date or "—"
                ),
                tags=(status,)
            )
        
        # Pack report tree and scrollbar
        report_tree.pack(side="left", fill="both", expand=True)
        report_scrollbar.pack(side="right", fill="y")
        
        # Export buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
    def export_component_status_csv(self, components, report_tree):
        """Export component status report to CSV"""
        try:
            import csv
            from tkinter import filedialog
            from datetime import datetime
            
            # Ask user for save location
            file_path = filedialog.asksaveasfilename(
                title="Save Component Status Report",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialvalue=f"component_status_{self.current_project}_{datetime.now().strftime('%Y%m%d')}.csv"
            )
            
            if file_path:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write header with project info
                    writer.writerow([f"Component Status Report - Project: {self.current_project}"])
                    writer.writerow([f"Generated: {datetime.now().strftime('%m/%d/%Y %H:%M')}"])
                    writer.writerow([])  # Empty row
                    
                    # Write column headers
                    writer.writerow([
                        "Structure ID",
                        "Component Type", 
                        "Status",
                        "Order Date",
                        "Expected Delivery",
                        "Actual Delivery",
                        "Notes"
                    ])
                    
                    # Calculate status counts for summary
                    status_counts = {"pending": 0, "ordered": 0, "approved": 0, "delivered": 0, "installed": 0}
                    
                    # Write component data
                    for item in report_tree.get_children():
                        values = report_tree.item(item, "values")
                        if values:  # Ensure we have values
                            writer.writerow(values)
                            
                            # Count status for summary (assuming status is in column 2)
                            if len(values) > 2:
                                status = values[2].lower()
                                if status in status_counts:
                                    status_counts[status] += 1
                    
                    # Write summary section
                    writer.writerow([])  # Empty row
                    writer.writerow(["Summary:"])
                    
                    # Calculate delivery performance
                    on_time_count = 0
                    late_count = 0 
                    pending_count = 0
                    
                    for component in components:
                        if component.status == "delivered" and component.expected_delivery_date and component.actual_delivery_date:
                            if component.actual_delivery_date <= component.expected_delivery_date:
                                on_time_count += 1
                            else:
                                late_count += 1
                        elif component.status in ["pending", "ordered", "approved"]:
                            pending_count += 1
                    
                    writer.writerow(["Delivered On Time:", on_time_count])
                    writer.writerow(["Delivered Late:", late_count])
                    writer.writerow(["Pending Delivery:", pending_count])
                    
                    # Success message
                    Messagebox.show_info(f"Component status report exported to {file_path}", "Export Successful")
            
        except Exception as e:
            self.logger.error(f"Error exporting component status CSV: {e}", exc_info=True)
            Messagebox.show_error(f"Failed to export CSV: {str(e)}", "Export Error")

    def view_structure_from_pipe_item_enhanced(self, structure_id: str):
        """Enhanced structure navigation with better feedback"""
        try:
            # Switch to Structures tab and select the structure
            self.notebook.select(0)  # Select first tab (Structures)
            
            # Find and select the structure in the tree
            found = False
            for item in self.structure_tree.get_children():
                item_values = self.structure_tree.item(item, "values")
                if item_values and len(item_values) > 0 and item_values[0] == structure_id:
                    self.structure_tree.selection_set(item)
                    self.structure_tree.see(item)
                    self.show_structure_details(None)
                    found = True
                    break
            
            if found:
                self.show_status_toast(f"Found and selected structure {structure_id}")
            else:
                self.show_status_toast(f"Structure {structure_id} not found in current view")
                
        except Exception as e:
            self.logger.error(f"Error navigating to structure: {e}", exc_info=True)
            Messagebox.show_error(f"Could not navigate to structure {structure_id}", "Navigation Error")

    def export_pipe_totals_csv(self, pipe_totals):
        """Export pipe totals to CSV"""
        try:
            import csv
            from tkinter import filedialog
            
            # Ask user for save location
            file_path = filedialog.asksaveasfilename(
                title="Save Pipe Totals",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialvalue=f"pipe_totals_{self.current_project}_{datetime.now().strftime('%Y%m%d')}.csv"
            )
            
            if file_path:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write header
                    writer.writerow(["Pipe Type", "Diameter", "Total Length (ft)", "Structure Count", "Structures"])
                    
                    # Write data
                    for key, data in pipe_totals.items():
                        diameter_text = f"{int(data['diameter'])}\"" if data['diameter'] else "Unknown"
                        structure_list = ", ".join([s['id'] for s in data['structures']])
                        
                        writer.writerow([
                            data['pipe_type'],
                            diameter_text,
                            f"{data['total_length']:.2f}",
                            len(data['structures']),
                            structure_list
                        ])
                
                Messagebox.show_info(f"Pipe totals exported to {file_path}", "Export Successful")
        
        except Exception as e:
            self.logger.error(f"Error exporting pipe totals CSV: {e}", exc_info=True)
            Messagebox.show_error(f"Failed to export CSV: {str(e)}", "Export Error")

    def export_pipe_details_csv(self, structures_data):
        """Export pipe details to CSV"""
        try:
            import csv
            from tkinter import filedialog
            
            # Ask user for save location
            file_path = filedialog.asksaveasfilename(
                title="Save Pipe Details",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialvalue=f"pipe_details_{self.current_project}_{datetime.now().strftime('%Y%m%d')}.csv"
            )
            
            if file_path:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write header
                    writer.writerow(["Structure ID", "Type", "Pipe Type", "Diameter", "Length (ft)", "Upstream", "Status"])
                    
                    # Write data
                    for structure in structures_data:
                        # Determine status
                        if structure.pipe_length and structure.pipe_diameter and structure.pipe_type:
                            status = "Complete"
                        elif structure.pipe_type or structure.pipe_diameter or structure.pipe_length:
                            status = "Partial"
                        else:
                            status = "No Pipe Data"
                        
                        # Format values
                        pipe_type = structure.pipe_type or "—"
                        diameter = f"{int(structure.pipe_diameter)}\"" if structure.pipe_diameter else "—"
                        length = f"{structure.pipe_length:.2f}" if structure.pipe_length else "—"
                        upstream = structure.upstream_structure_id or "—"
                        
                        writer.writerow([
                            structure.structure_id,
                            structure.structure_type,
                            pipe_type,
                            diameter,
                            length,
                            upstream,
                            status
                        ])
                
                Messagebox.show_info(f"Pipe details exported to {file_path}", "Export Successful")
        
        except Exception as e:
            self.logger.error(f"Error exporting pipe details CSV: {e}", exc_info=True)
            Messagebox.show_error(f"Failed to export CSV: {str(e)}", "Export Error")

    def create_pipe_order_from_totals(self, pipe_totals, parent_window):
        """Create a pipe order from calculated totals"""
        parent_window.destroy()
        
        # Get project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            return
        
        # Convert pipe_totals format to pipe_groups format expected by order creation
        pipe_groups = {}
        
        for key, data in pipe_totals.items():
            pipe_groups[key] = {
                'pipe_type': data['pipe_type'],
                'diameter': data['diameter'],
                'total_length': data['total_length'],
                'structures': data['structures']  # These should be Structure objects
            }
        
        # Create order dialog
        order_window = ttk.Toplevel(self.root)
        order_window.title("Create Order from Totals")
        order_window.geometry("600x500")
        self.center_toplevel(order_window)
        order_window.transient(self.root)
        order_window.grab_set()
        
        # Main container
        main_frame = ttk.Frame(order_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(
            main_frame, 
            text="Create Pipe Order from Totals", 
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        ).pack(pady=(0, 20))
        
        # Order information section
        order_info_frame = ttk.Labelframe(main_frame, text="Order Information", padding=10)
        order_info_frame.pack(fill="x", pady=(0, 20))
        
        # Order details form
        form_frame = ttk.Frame(order_info_frame)
        form_frame.pack(fill="x")
        form_frame.columnconfigure(1, weight=1)
        
        # Order number
        ttk.Label(form_frame, text="Order Number:").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
        order_number_entry = ttk.Entry(form_frame)
        order_number_entry.grid(row=0, column=1, sticky="ew", pady=5)
        
        # Generate default order number
        total_structures = sum(len(data['structures']) for data in pipe_totals.values())
        default_order_num = f"PO-{datetime.now().strftime('%Y%m%d')}-{total_structures:03d}"
        order_number_entry.insert(0, default_order_num)
        
        # Supplier
        ttk.Label(form_frame, text="Supplier:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=5)
        supplier_entry = ttk.Entry(form_frame)
        supplier_entry.grid(row=1, column=1, sticky="ew", pady=5)
        
        # Expected delivery date
        ttk.Label(form_frame, text="Expected Delivery:").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=5)
        delivery_date_frame = ttk.Frame(form_frame)
        delivery_date_frame.grid(row=2, column=1, sticky="ew", pady=5)
        delivery_date_frame.columnconfigure(0, weight=1)
        
        delivery_date_entry = ttk.Entry(delivery_date_frame)
        delivery_date_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ttk.Button(
            delivery_date_frame,
            text="📅",
            width=3,
            command=lambda: self.open_date_picker(delivery_date_entry)
        ).pack(side="right")
        
        # Notes
        ttk.Label(form_frame, text="Notes:").grid(row=3, column=0, sticky="nw", padx=(0, 10), pady=5)
        notes_text = tk.Text(form_frame, height=3, wrap="word")
        notes_text.grid(row=3, column=1, sticky="ew", pady=5)
        
        # Totals summary
        summary_frame = ttk.Labelframe(main_frame, text="Order Summary", padding=10)
        summary_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        total_length = sum(data['total_length'] for data in pipe_totals.values())
        total_structures = sum(len(data['structures']) for data in pipe_totals.values())
        
        summary_text = f"Total Length: {total_length:.2f} feet\n"
        summary_text += f"Total Structures: {total_structures}\n"
        summary_text += f"Pipe Types: {len(pipe_totals)}\n\n"
        
        for key, data in pipe_totals.items():
            diameter_text = f"{int(data['diameter'])}\"" if data['diameter'] else "Unknown"
            summary_text += f"• {data['pipe_type']} {diameter_text}: {data['total_length']:.2f} ft ({len(data['structures'])} structures)\n"
        
        ttk.Label(summary_frame, text=summary_text, justify="left").pack(anchor="w")
        
        def create_order():
            try:
                order_number = order_number_entry.get().strip()
                supplier = supplier_entry.get().strip()
                delivery_date_str = delivery_date_entry.get().strip()
                notes = notes_text.get("1.0", tk.END).strip()
                
                # Validation
                if not order_number:
                    Messagebox.show_error("Please enter an order number", "Validation Error")
                    return
                
                # Parse delivery date
                delivery_date = None
                if delivery_date_str:
                    try:
                        delivery_date = datetime.strptime(delivery_date_str, "%m/%d/%Y")
                    except ValueError:
                        Messagebox.show_error("Invalid date format. Please use MM/DD/YYYY", "Date Error")
                        return
                
                # Create the pipe order in database
                success = self.db.create_pipe_order(
                    order_number=order_number,
                    supplier=supplier,
                    expected_delivery_date=delivery_date,
                    notes=notes,
                    pipe_groups=pipe_groups,
                    project_id=project.id
                )
                
                if success:
                    Messagebox.show_info(f"Pipe order '{order_number}' created successfully", "Success")
                    order_window.destroy()
                    # Refresh pipe orders if we're on that tab
                    if hasattr(self, 'pipe_orders_tree'):
                        self.refresh_pipe_orders()
                else:
                    Messagebox.show_error("Failed to create pipe order", "Error")
                    
            except Exception as e:
                self.logger.error(f"Error creating pipe order from totals: {e}", exc_info=True)
                Messagebox.show_error(f"An error occurred: {str(e)}", "Error")
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(
            button_frame,
            text="Create Order",
            bootstyle="primary",
            command=create_order
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            bootstyle="secondary",
            command=order_window.destroy
        ).pack(side="right", padx=5)

    def export_pipe_totals_csv(self, pipe_totals):
        """Export pipe totals to CSV"""
        try:
            import csv
            from tkinter import filedialog
            from datetime import datetime
            
            # Ask user for save location
            file_path = filedialog.asksaveasfilename(
                title="Save Pipe Totals",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialvalue=f"pipe_totals_{self.current_project}_{datetime.now().strftime('%Y%m%d')}.csv"
            )
            
            if file_path:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write header with project info
                    writer.writerow([f"Pipe Totals Report - Project: {self.current_project}"])
                    writer.writerow([f"Generated: {datetime.now().strftime('%m/%d/%Y %H:%M')}"])
                    writer.writerow([])  # Empty row
                    
                    # Write data header
                    writer.writerow(["Pipe Type", "Diameter", "Total Length (ft)", "Structure Count", "Structures"])
                    
                    # Calculate grand totals
                    grand_total_length = 0
                    grand_total_structures = 0
                    
                    # Write data
                    for key, data in pipe_totals.items():
                        diameter_text = f"{int(data['diameter'])}\"" if data['diameter'] else "Unknown"
                        structure_list = ", ".join([s['id'] for s in data['structures']])
                        total_length = data['total_length']
                        structure_count = len(data['structures'])
                        
                        grand_total_length += total_length
                        grand_total_structures += structure_count
                        
                        writer.writerow([
                            data['pipe_type'],
                            diameter_text,
                            f"{total_length:.2f}",
                            structure_count,
                            structure_list
                        ])
                    
                    # Write totals
                    writer.writerow([])  # Empty row
                    writer.writerow(["TOTALS", "", f"{grand_total_length:.2f}", grand_total_structures, ""])
                    
                    # Write summary statistics
                    writer.writerow([])  # Empty row
                    writer.writerow(["Summary Statistics"])
                    writer.writerow(["Total Pipe Types:", len(pipe_totals)])
                    writer.writerow(["Total Length (ft):", f"{grand_total_length:.2f}"])
                    writer.writerow(["Total Structures:", grand_total_structures])
                    writer.writerow(["Average Length per Structure:", f"{grand_total_length/grand_total_structures:.2f}" if grand_total_structures > 0 else "0"])
                
                Messagebox.show_info(f"Pipe totals exported to {file_path}", "Export Successful")
        
        except Exception as e:
            self.logger.error(f"Error exporting pipe totals CSV: {e}", exc_info=True)
            Messagebox.show_error(f"Failed to export CSV: {str(e)}", "Export Error")

    def update_structure_status(self, event=None):
        """Update the overall structure status (placeholder for future enhancement)"""
        # This could be used to track overall structure completion status
        # For now, it's calculated based on component status
        pass

    def update_existing_context_menu_bindings(self):
        """Update existing context menu bindings to use enhanced versions"""
        
        # Remove old bindings if they exist
        if hasattr(self, 'pipe_orders_tree'):
            self.pipe_orders_tree.unbind('<Button-3>')
            self.pipe_orders_tree.bind('<Button-3>', self.show_pipe_order_context_menu)
        
        if hasattr(self, 'order_breakdown_tree'):
            self.order_breakdown_tree.unbind('<Button-3>')
            self.order_breakdown_tree.bind('<Button-3>', self.show_pipe_breakdown_context_menu_enhanced)

    def force_structure_tree_refresh(self):
        """Force refresh of the structure tree display"""
        
        try:
            if not hasattr(self, 'component_structure_tree'):
                print("ERROR: component_structure_tree doesn't exist!")
                return
            
            # Clear and reload the structure tree
            for item in self.component_structure_tree.get_children():
                self.component_structure_tree.delete(item)
            
            # Reload structures for components
            self.load_structures_for_components()
            
            # Also refresh the main structure tree if it exists
            if hasattr(self, 'structure_tree'):
                self.load_structures()
            
            
        except Exception as e:
            self.logger.error(f"Error refreshing structure tree: {e}", exc_info=True)
            print(f"ERROR: Failed to refresh structure tree: {e}")

    def add_component(self):

        """Add a new component to the selected structure"""
        # Get selected structure
        selection = self.component_structure_tree.selection()
        if not selection:
            Messagebox.show_warning("Please select a structure first", "No Structure Selected")
            return
        
        structure_id = self.component_structure_tree.item(selection[0], "values")[0]
        
        # Get project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            return
        
        # Create dialog window
        component_window = ttk.Toplevel(self.root)
        component_window.title("Add Component")
        component_window.geometry("400x450")
        self.center_toplevel(component_window)
        
        # Add padding around the entire content
        main_frame = ttk.Frame(component_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(
            main_frame, 
            text="Add Component", 
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        ).pack(pady=(0, 20))
        
        # Structure info
        ttk.Label(
            main_frame,
            text=f"Structure: {structure_id}",
            font=("Helvetica", 12)
        ).pack(anchor="w", pady=(0, 20))
        
        # Component type selection
        ttk.Label(main_frame, text="Component Type:").pack(anchor="w", pady=(10, 5))
        
        # Get component types
        component_types = self.db.get_all_component_types()
        type_names = [ct.name for ct in component_types]
        
        type_var = tk.StringVar()
        type_combo = ttk.Combobox(main_frame, textvariable=type_var, values=type_names, state="readonly")
        type_combo.pack(fill="x", pady=(0, 10))
        if type_names:
            type_combo.current(0)
        
        # Status selection
        ttk.Label(main_frame, text="Status:").pack(anchor="w", pady=(10, 5))
        
        status_var = tk.StringVar()
        status_options = ["pending", "ordered", "approved", "delivered", "installed"]
        status_combo = ttk.Combobox(main_frame, textvariable=status_var, values=status_options, state="readonly")
        status_combo.pack(fill="x", pady=(0, 10))
        status_combo.current(0)  # Default to "pending"
        
        # Order date
        ttk.Label(main_frame, text="Order Date (YYYY-MM-DD):").pack(anchor="w", pady=(10, 5))
        order_entry = ttk.Entry(main_frame)
        order_entry.pack(fill="x", pady=(0, 10))
        
        # Expected delivery date
        ttk.Label(main_frame, text="Expected Delivery (YYYY-MM-DD):").pack(anchor="w", pady=(10, 5))
        expected_entry = ttk.Entry(main_frame)
        expected_entry.pack(fill="x", pady=(0, 10))
        
        # Actual delivery date
        ttk.Label(main_frame, text="Actual Delivery (YYYY-MM-DD):").pack(anchor="w", pady=(10, 5))
        actual_entry = ttk.Entry(main_frame)
        actual_entry.pack(fill="x", pady=(0, 10))
        
        # Notes
        ttk.Label(main_frame, text="Notes:").pack(anchor="w", pady=(10, 5))
        notes_entry = ttk.Entry(main_frame)
        notes_entry.pack(fill="x", pady=(0, 10))
        
        def save_component():
            try:
                # Validate component type
                if not type_var.get():
                    Messagebox.show_error("Please select a component type", "Validation Error")
                    return
                
                # Get component type ID
                component_type_id = None
                for ct in component_types:
                    if ct.name == type_var.get():
                        component_type_id = ct.id
                        break
                
                if not component_type_id:
                    Messagebox.show_error("Invalid component type", "Validation Error")
                    return
                
                # Parse dates
                order_date = None
                expected_date = None
                actual_date = None
                
                if order_entry.get().strip():
                    try:
                        order_date = datetime.strptime(order_entry.get().strip(), "%Y-%m-%d")
                    except ValueError:
                        Messagebox.show_error("Invalid order date format (use YYYY-MM-DD)", "Validation Error")
                        return
                
                if expected_entry.get().strip():
                    try:
                        expected_date = datetime.strptime(expected_entry.get().strip(), "%Y-%m-%d")
                    except ValueError:
                        Messagebox.show_error("Invalid expected delivery date format (use YYYY-MM-DD)", "Validation Error")
                        return
                
                if actual_entry.get().strip():
                    try:
                        actual_date = datetime.strptime(actual_entry.get().strip(), "%Y-%m-%d")
                    except ValueError:
                        Messagebox.show_error("Invalid actual delivery date format (use YYYY-MM-DD)", "Validation Error")
                        return
                
                # Create component object
                component = StructureComponent(
                    structure_id=structure_id,
                    component_type_id=component_type_id,
                    status=status_var.get(),
                    order_date=order_date,
                    expected_delivery_date=expected_date,
                    actual_delivery_date=actual_date,
                    notes=notes_entry.get().strip() if notes_entry.get().strip() else None
                )
                
                # Add component to database
                success = self.db.add_structure_component(component, project.id)
                
                if success:
                    Messagebox.show_info(f"{type_var.get()} component added successfully", "Success")
                    component_window.destroy()
                    # Refresh component list
                    self.load_structure_components(None)
                else:
                    Messagebox.show_error("Failed to add component", "Database Error")
            
            except Exception as e:
                Messagebox.show_error(f"An error occurred: {str(e)}", "Error")
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        # Save button
        ttk.Button(
            button_frame,
            text="Save",
            bootstyle="primary",
            command=save_component
        ).pack(side="left", padx=5)
        
        # Cancel button
        ttk.Button(
            button_frame,
            text="Cancel",
            bootstyle="secondary",
            command=component_window.destroy
        ).pack(side="right", padx=5)

    def update_component(self):
        """DEPRECATED: Use update_component_status or show_component_update_dialog instead. Update the status of a component"""
        # Get selected component
        selection = self.component_tree.selection()
        if not selection:
            Messagebox.show_warning("Please select a component first", "No Component Selected")
            return
        
        # Get component ID from tags
        component_id = int(self.component_tree.item(selection[0], "tags")[0])
        
        # Get current values
        values = self.component_tree.item(selection[0], "values")
        current_type = values[0]
        current_status = values[1]
        current_notes = values[5]
        
        # Create dialog window
        update_window = ttk.Toplevel(self.root)
        update_window.title("Update Component Status")
        update_window.geometry("400x300")
        self.center_toplevel(update_window)
        
        # Add padding around the entire content
        main_frame = ttk.Frame(update_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(
            main_frame, 
            text="Update Component Status", 
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        ).pack(pady=(0, 20))
        
        # Component info
        ttk.Label(
            main_frame,
            text=f"Component: {current_type}",
            font=("Helvetica", 12)
        ).pack(anchor="w", pady=(0, 20))
        
        # Status selection
        ttk.Label(main_frame, text="Status:").pack(anchor="w", pady=(10, 5))
        
        status_var = tk.StringVar(value=current_status)
        status_options = ["pending", "ordered", "approved", "delivered", "installed"]
        status_combo = ttk.Combobox(main_frame, textvariable=status_var, values=status_options, state="readonly")
        status_combo.pack(fill="x", pady=(0, 10))
        
        # Actual delivery date (only if status is "delivered" or "installed")
        delivery_frame = ttk.Frame(main_frame)
        delivery_frame.pack(fill="x", pady=(10, 5))
        
        ttk.Label(delivery_frame, text="Delivery Date (YYYY-MM-DD):").pack(anchor="w")
        actual_entry = ttk.Entry(delivery_frame)
        actual_entry.pack(fill="x", pady=(5, 0))
        
        # Hide/show delivery date based on status
        def toggle_delivery_date(*args):
            if status_var.get() in ["delivered", "installed"]:
                delivery_frame.pack(fill="x", pady=(10, 5))
            else:
                delivery_frame.pack_forget()
        
        status_var.trace("w", toggle_delivery_date)
        toggle_delivery_date()  # Initial state
        
        # Notes
        ttk.Label(main_frame, text="Notes:").pack(anchor="w", pady=(10, 5))
        notes_entry = ttk.Entry(main_frame)
        notes_entry.insert(0, current_notes)
        notes_entry.pack(fill="x", pady=(0, 10))
        
        def save_update():
            try:
                # Parse delivery date if provided
                actual_date = None
                if status_var.get() in ["delivered", "installed"] and actual_entry.get().strip():
                    try:
                        actual_date = datetime.strptime(actual_entry.get().strip(), "%Y-%m-%d")
                    except ValueError:
                        Messagebox.show_error("Invalid delivery date format (use YYYY-MM-DD)", "Validation Error")
                        return
                
                # Update component status
                success = self.db.update_component_status(
                    component_id,
                    status_var.get(),
                    notes_entry.get().strip() if notes_entry.get().strip() else None,
                    actual_date
                )
                
                if success:
                    Messagebox.show_info("Component status updated successfully", "Success")
                    update_window.destroy()
                    # Refresh component list
                    self.load_structure_components()
                else:
                    Messagebox.show_error("Failed to update component status", "Database Error")
            
            except Exception as e:
                Messagebox.show_error(f"An error occurred: {str(e)}", "Error")

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))

        # Save button
        ttk.Button(
            button_frame,
            text="Save",
            bootstyle="primary",
            command=save_update
        ).pack(side="left", padx=5)

        # Cancel button
        ttk.Button(
            button_frame,
            text="Cancel",
            bootstyle="secondary",
            command=update_window.destroy
        ).pack(side="right", padx=5)

    def refresh_pipe_types(self):
        """Refresh the pipe types dropdown with current values from database"""
        pipe_types = self.db.get_all_pipe_types()
        self.entries['Pipe Type:']['values'] = pipe_types

    def delete_component(self):
        """Delete the selected component"""
        # Get selected component
        selection = self.component_tree.selection()
        if not selection:
            Messagebox.show_warning("Please select a component first", "No Component Selected")
            return
        
        # Get component ID from tags
        component_id = int(self.component_tree.item(selection[0], "tags")[0])
        
        # Get current values for confirmation message
        values = self.component_tree.item(selection[0], "values")
        component_type = values[0]
        
        # Confirm deletion
        confirm = Messagebox.yesno(
            f"Are you sure you want to delete the {component_type} component?",
            "Confirm Deletion"
        )
        
        if not confirm:
            return
        
        # Delete the component
        success = self.db.delete_structure_component(component_id)
        
        if success:
            Messagebox.show_info(f"{component_type} component deleted successfully", "Success")
            # Remove from treeview
            self.component_tree.delete(selection[0])
        else:
            Messagebox.show_error(f"Failed to delete component", "Database Error")

    def generate_component_report(self):
        """Generate a report of components and their statuses"""
        # Get selected structure
        selection = self.component_structure_tree.selection()
        if not selection:
            Messagebox.show_warning("Please select a structure first", "No Structure Selected")
            return
        
        structure_id = self.component_structure_tree.item(selection[0], "values")[0]
        
        # Get project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            return
        
        # Get components for this structure
        components = self.db.get_structure_components(structure_id, project.id)
        
        if not components:
            Messagebox.show_info(f"No components found for structure {structure_id}", "Empty Report")
            return
        
        # Create report window
        report_window = ttk.Toplevel(self.root)
        report_window.title(f"Component Report: {structure_id}")
        report_window.geometry("700x500")
        self.center_toplevel(report_window)
        
        # Main container with padding
        main_frame = ttk.Frame(report_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Report header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(
            header_frame, 
            text=f"Component Report for Structure: {structure_id}",
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        ).pack(side="left")
        
        # Report date
        ttk.Label(
            header_frame, 
            text=f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            bootstyle="secondary"
        ).pack(side="right")
        
        # Content frame
        content_frame = ttk.Labelframe(main_frame, text="Component Summary", padding=10)
        content_frame.pack(fill="both", expand=True)
        
        # Report text widget with scrollbar
        report_text = tk.Text(content_frame, wrap='word', font=("Consolas", 11))
        scrollbar = ttk.Scrollbar(content_frame, orient='vertical', command=report_text.yview)
        report_text.configure(yscrollcommand=scrollbar.set)
        
        report_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Add tags for styling
        report_text.tag_configure("heading", font=("Helvetica", 12, "bold"))
        report_text.tag_configure("subheading", font=("Helvetica", 11, "bold"))
        report_text.tag_configure("normal", font=("Helvetica", 11))
        report_text.tag_configure("data", font=("Consolas", 11))
        report_text.tag_configure("status-pending", font=("Consolas", 11), foreground="orange")
        report_text.tag_configure("status-ordered", font=("Consolas", 11), foreground="blue")
        report_text.tag_configure("status-approved", font=("Consolas", 11), foreground="purple")
        report_text.tag_configure("status-delivered", font=("Consolas", 11), foreground="green")
        report_text.tag_configure("status-installed", font=("Consolas", 11), foreground="green")
        
        # Generate report content
        report_text.insert(tk.END, f"Structure ID: {structure_id}\n", "heading")
        report_text.insert(tk.END, f"Total Components: {len(components)}\n\n", "normal")
        
        # Status summary
        status_counts = {}
        for component in components:
            status_counts[component.status] = status_counts.get(component.status, 0) + 1
        
        report_text.insert(tk.END, "Status Summary:\n", "subheading")
        for status, count in status_counts.items():
            report_text.insert(tk.END, f"  {status}: {count}\n", f"status-{status}")
        
        report_text.insert(tk.END, "\nComponent Details:\n", "subheading")
        
        # Component details
        for i, component in enumerate(components):
            if i > 0:
                report_text.insert(tk.END, "\n" + "-"*50 + "\n", "normal")
            
            # Format dates for display
            order_date = component.order_date.strftime("%Y-%m-%d") if component.order_date else "Not set"
            expected_date = component.expected_delivery_date.strftime("%Y-%m-%d") if component.expected_delivery_date else "Not set"
            delivery_date = component.actual_delivery_date.strftime("%Y-%m-%d") if component.actual_delivery_date else "Not delivered"
            
            report_text.insert(tk.END, f"{component.component_type_name}\n", "subheading")
            report_text.insert(tk.END, f"  Status: {component.status}\n", f"status-{component.status}")
            report_text.insert(tk.END, f"  Order Date: {order_date}\n", "data")
            report_text.insert(tk.END, f"  Expected Delivery: {expected_date}\n", "data")
            report_text.insert(tk.END, f"  Actual Delivery: {delivery_date}\n", "data")
            
            if component.notes:
                report_text.insert(tk.END, f"  Notes: {component.notes}\n", "data")
        
        # Make text readonly
        report_text.configure(state='disabled')
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        # Export button
        ttk.Button(
            button_frame, 
            text="Export as PDF", 
            bootstyle="success",
            command=lambda: Messagebox.show_info("PDF export functionality not implemented yet", "Feature Coming Soon")
        ).pack(side="left", padx=5)
        
        # Print button
        ttk.Button(
            button_frame, 
            text="Print", 
            bootstyle="info",
            command=lambda: Messagebox.show_info("Print functionality not implemented yet", "Feature Coming Soon")
        ).pack(side="left", padx=5)
        
        # Close button
        ttk.Button(
            button_frame, 
            text="Close", 
            bootstyle="secondary",
            command=report_window.destroy
        ).pack(side="right", padx=5)

    def import_structures(self):
        """Import structures from a file"""
        Messagebox.show_info("Structure import functionality coming soon", "Feature Not Implemented")
        
    def export_structures(self):
        """Export structures to a file"""
        Messagebox.show_info("Structure export functionality coming soon", "Feature Not Implemented")

    def rename_structure_dialog(self):
        """Show dialog to rename the selected structure"""
        # Get selected structure from treeview
        selection = self.structure_tree.selection()
        if not selection:
            Messagebox.show_warning("Please select a structure to rename", "No Selection")
            return
        
        # Get current structure ID
        current_id = self.structure_tree.item(selection[0], "values")[0]
        
        # Skip if it's a separator row
        if not current_id or "─── Run" in current_id:
            Messagebox.show_warning("Please select a valid structure", "Invalid Selection")
            return
        
        # Get project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            Messagebox.show_error("Could not find current project", "Project Error")
            return
        
        # Create rename dialog
        rename_window = ttk.Toplevel(self.root)
        rename_window.title("Rename Structure")
        rename_window.geometry("450x400")
        self.center_toplevel(rename_window)
        rename_window.resizable(False, False)
        
        # Center the window
        rename_window.transient(self.root)
        rename_window.grab_set()
        
        # Main container with padding
        main_frame = ttk.Frame(rename_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(
            main_frame, 
            text="Rename Structure", 
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        ).pack(pady=(0, 20))
        
        # Current structure info
        info_frame = ttk.Labelframe(main_frame, text="Current Structure", padding=10)
        info_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(
            info_frame,
            text=f"Structure ID: {current_id}",
            font=("Helvetica", 12, "bold")
        ).pack(anchor="w")
        
        # Get structure details for display
        structure = self.db.get_structure(current_id, project.id)
        if structure:
            ttk.Label(
                info_frame,
                text=f"Type: {structure.structure_type}",
                font=("Helvetica", 10)
            ).pack(anchor="w")
            ttk.Label(
                info_frame,
                text=f"Rim Elevation: {structure.rim_elevation}",
                font=("Helvetica", 10)
            ).pack(anchor="w")
        
        # New ID input
        input_frame = ttk.Labelframe(main_frame, text="New Structure ID", padding=10)
        input_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(input_frame, text="Enter new structure ID:").pack(anchor="w", pady=(0, 5))
        new_id_entry = ttk.Entry(input_frame, font=("Helvetica", 12))
        new_id_entry.pack(fill="x", pady=(0, 10))
        new_id_entry.insert(0, current_id)  # Pre-fill with current ID
        new_id_entry.select_range(0, tk.END)  # Select all text
        new_id_entry.focus()
        
        # Warning message
        warning_frame = ttk.Frame(main_frame)
        warning_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(
            warning_frame,
            text="⚠️ Warning: This will update all references to this structure",
            font=("Helvetica", 10),
            bootstyle="warning"
        ).pack(anchor="w")
        
        ttk.Label(
            warning_frame,
            text="including upstream connections and group memberships.",
            font=("Helvetica", 9),
            bootstyle="secondary"
        ).pack(anchor="w")
        
        def perform_rename():
            new_id = new_id_entry.get().strip()
            
            # Validation
            if not new_id:
                Messagebox.show_error("Please enter a new structure ID", "Validation Error")
                new_id_entry.focus()
                return
            
            if new_id == current_id:
                Messagebox.show_info("No changes needed - new ID is the same as current ID", "No Change")
                rename_window.destroy()
                return
            
            # Additional validation (you can customize these rules)
            if len(new_id) < 2:
                Messagebox.show_error("Structure ID must be at least 2 characters", "Validation Error")
                new_id_entry.focus()
                return
            
            # Check for invalid characters (customize as needed)
            import re
            if not re.match(r'^[A-Za-z0-9_-]+$', new_id):
                Messagebox.show_error(
                    "Structure ID can only contain letters, numbers, underscores, and hyphens", 
                    "Validation Error"
                )
                new_id_entry.focus()
                return
            
            # Confirm the rename operation
            confirm = Messagebox.yesno(
                f"Are you sure you want to rename '{current_id}' to '{new_id}'?\n\n"
                f"This will update all references and cannot be easily undone.",
                "Confirm Rename"
            )
            
            if not confirm:
                return
            
            # Perform the rename
            success = self.db.rename_structure(current_id, new_id, project.id)
            
            if success:
                Messagebox.show_info(
                    f"Structure successfully renamed from '{current_id}' to '{new_id}'",
                    "Rename Successful"
                )
                
                # Close dialog
                rename_window.destroy()
                
                # Refresh the structure list
                self.load_structures()
                
                # Update the form if this structure was selected
                if self.entries['Structure ID:'].get() == current_id:
                    self.entries['Structure ID:'].delete(0, tk.END)
                    self.entries['Structure ID:'].insert(0, new_id)
                
                # Try to select the renamed structure in the tree
                self.select_structure_in_tree(new_id)
                
            else:
                Messagebox.show_error(
                    f"Failed to rename structure. The new ID '{new_id}' may already exist.",
                    "Rename Failed"
                )
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        # Rename button
        ttk.Button(
            button_frame,
            text="Rename Structure",
            bootstyle="primary",
            command=perform_rename
        ).pack(side="left", padx=5)
        
        # Cancel button
        ttk.Button(
            button_frame,
            text="Cancel",
            bootstyle="secondary",
            command=rename_window.destroy
        ).pack(side="right", padx=5)
        
        # Bind Enter key to rename action
        new_id_entry.bind('<Return>', lambda e: perform_rename())    
    
    def manage_groups(self):
        """Show the group management dialog"""
        try:
            # Get project ID
            project = self.db.get_project_by_name(self.current_project, self.current_user.id)
            if not project:
                Messagebox.show_error("Could not find current project", "Project Error")
                return
                
            # Get all groups for this project
            groups = self.db.get_all_groups(project.id)
            
            # Create dialog window
            group_window = ttk.Toplevel(self.root)
            group_window.title("Manage Structure Groups")
            group_window.geometry("700x500")
            self.center_toplevel(group_window)
            
            # Main container with padding
            main_frame = ttk.Frame(group_window, padding=20)
            main_frame.pack(fill="both", expand=True)
            
            # Title
            ttk.Label(
                main_frame, 
                text="Structure Groups", 
                font=("Helvetica", 16, "bold"),
                bootstyle="primary"
            ).pack(anchor="w", pady=(0, 20))
            
            # Groups list frame
            list_frame = ttk.Labelframe(main_frame, text="Available Groups")
            list_frame.pack(fill="both", expand=True, pady=(0, 20))
            
            # Create groups treeview
            columns = ("Name", "Description", "Count")
            group_tree = ttk.Treeview(
                list_frame,
                columns=columns,
                show="headings",
                height=10
            )
            
            # Define column headings
            for col in columns:
                group_tree.heading(col, text=col)
                
            group_tree.column("Name", width=150)
            group_tree.column("Description", width=300)
            group_tree.column("Count", width=80, anchor="center")
            
            # Add a scrollbar
            scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=group_tree.yview)
            group_tree.configure(yscrollcommand=scrollbar.set)
            
            # Pack the treeview and scrollbar
            group_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            scrollbar.pack(side="right", fill="y", pady=10)
            
            # Populate groups
            for group in groups:
                # Get count of structures in this group
                structures = self.db.get_group_structures(group.name, project.id)
                group_tree.insert(
                    "", 
                    "end", 
                    values=(group.name, group.description or "", len(structures))
                )
            
            # Button frame
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill="x")
            
            # Buttons for group operations
            ttk.Button(
                button_frame,
                text="New Group",
                bootstyle="success",
                command=lambda: self.create_new_group_dialog(group_tree, project.id)
            ).pack(side="left", padx=5)
            
            ttk.Button(
                button_frame,
                text="View Structures",
                bootstyle="info",
                command=lambda: self.view_group_structures(group_tree, project.id)
            ).pack(side="left", padx=5)
            
            ttk.Button(
                button_frame,
                text="Delete Group",
                bootstyle="danger",
                command=lambda: self.delete_group_dialog(group_tree, project.id)
            ).pack(side="left", padx=5)
            
            ttk.Button(
                button_frame,
                text="Close",
                bootstyle="secondary",
                command=group_window.destroy
            ).pack(side="right", padx=5)
            
        except Exception as e:
            self.logger.error(f"Group management error: {e}", exc_info=True)
            Messagebox.show_error(f"An error occurred: {str(e)}", "Error")
            
    def create_new_group_dialog(self, tree_view, project_id):
        """Dialog for creating a new group"""
        # Get group details
        group_name = dialogs.Querybox.get_string(
            "Enter group name:",
            "New Group"
        )
        
        if not group_name:
            return
            
        description = dialogs.Querybox.get_string(
            "Enter description (optional):",
            "New Group"
        )
        
        # Create group
        success = self.db.create_group(group_name, project_id, description or "")
        if success:
            Messagebox.show_info(f"Group '{group_name}' created successfully", "Success")
            
            # Add to treeview
            tree_view.insert(
                "",
                "end",
                values=(group_name, description or "", 0)
            )
        else:
            Messagebox.show_error(
                "Failed to create group. Group name may already exist.",
                "Database Error"
            )
            
    def view_group_structures(self, tree_view, project_id):
        """View structures in the selected group - UPDATED with new columns"""
        selection = tree_view.selection()
        if not selection:
            Messagebox.show_warning("Please select a group", "No Selection")
            return
            
        group_name = tree_view.item(selection[0], "values")[0]
        
        # Get structures in this group
        structures = self.db.get_group_structures(group_name, project_id)
        if not structures:
            Messagebox.show_info(f"No structures in group '{group_name}'", "Empty Group")
            return
            
        # Create dialog window
        view_window = ttk.Toplevel(self.root)
        view_window.title(f"Group: {group_name}")
        view_window.geometry("900x500")  # Made wider for new columns
        self.center_toplevel(view_window)
        
        # Main container with padding
        main_frame = ttk.Frame(view_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(
            main_frame, 
            text=f"Structures in Group: {group_name}", 
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        ).pack(anchor="w", pady=(0, 20))
        
        # Structures list - UPDATED with new columns including SLOPE
        columns = ("ID", "Type", "Rim Elevation", "Invert Out", "Depth", "Upstream", "Slope")
        structure_tree = ttk.Treeview(
            main_frame,
            columns=columns,
            show="headings",
            height=15
        )
        
        # Define column headings
        for col in columns:
            structure_tree.heading(col, text=col)
            
        structure_tree.column("ID", width=100)
        structure_tree.column("Type", width=80)
        structure_tree.column("Rim Elevation", width=120, anchor="e")
        structure_tree.column("Invert Out", width=120, anchor="e")
        structure_tree.column("Depth", width=80, anchor="e")
        structure_tree.column("Upstream", width=120, anchor="center")
        structure_tree.column("Slope", width=80, anchor="center")
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=structure_tree.yview)
        structure_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack the treeview and scrollbar
        structure_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create a dictionary for quick lookup of structures (for slope calculation)
        structure_dict = {s.structure_id: s for s in structures}
        
        # Populate structures - UPDATED with depth and slope calculation
        for structure in structures:
            # Calculate depth
            if structure.rim_elevation is not None and structure.invert_out_elevation is not None:
                depth = structure.rim_elevation - structure.invert_out_elevation
                depth_text = f"{depth:.2f}"
            else:
                depth_text = "—"
            
            upstream_id = structure.upstream_structure_id if structure.upstream_structure_id else "—"
            
            # Calculate slope using the same method as main treeview
            slope_text = self.calculate_slope(structure, structure_dict)
            
            structure_tree.insert(
                "",
                "end",
                values=(
                    structure.structure_id,
                    structure.structure_type,
                    f"{structure.rim_elevation:.2f}",
                    f"{structure.invert_out_elevation:.2f}",
                    depth_text,
                    upstream_id,
                    slope_text
                )
            )
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        # Close button
        ttk.Button(
            button_frame,
            text="Close",
            bootstyle="secondary",
            command=view_window.destroy
        ).pack(side="right")
        
    def delete_group_dialog(self, tree_view, project_id):
        """Delete the selected group"""
        selection = tree_view.selection()
        if not selection:
            Messagebox.show_warning("Please select a group to delete", "No Selection")
            return
            
        group_name = tree_view.item(selection[0], "values")[0]
        
        # Confirm deletion
        confirm = Messagebox.yesno(
            f"Are you sure you want to delete group '{group_name}'?\n\nThis will not delete the structures in the group.",
            "Confirm Deletion"
        )
        
        if not confirm:
            return
            
        # Delete group
        success = self.db.delete_group(group_name, project_id)
        if success:
            Messagebox.show_info(f"Group '{group_name}' deleted successfully", "Success")
            # Remove from treeview
            tree_view.delete(selection[0])
        else:
            Messagebox.show_error(f"Failed to delete group '{group_name}'", "Database Error")
        
    def find_structure(self):
        """Show the structure search dialog"""
        search_term = dialogs.Querybox.get_string(
            "Enter structure ID or partial ID to search:", 
            "Find Structure"
        )
        
        if not search_term:
            return
            
        # Get project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            Messagebox.show_error("Could not find current project", "Project Error")
            return
            
        # Get all structures
        structures = self.db.get_all_structures(project.id)
        
        # Filter structures by search term
        matches = []
        for structure in structures:
            if search_term.lower() in structure.structure_id.lower():
                matches.append(structure)
        
        if not matches:
            Messagebox.show_info(f"No structures matching '{search_term}' found", "No Results")
            return
            
        # If only one match, select it in the treeview
        if len(matches) == 1:
            self.select_structure_in_tree(matches[0].structure_id)
            return
            
        # If multiple matches, show results dialog
        results_window = ttk.Toplevel(self.root)
        results_window.title("Search Results")
        results_window.geometry("500x400")
        self.center_toplevel(results_window)
        
        # Main container with padding
        main_frame = ttk.Frame(results_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(
            main_frame, 
            text=f"Search Results: {search_term}", 
            font=("Helvetica", 14, "bold"),
            bootstyle="primary"
        ).pack(anchor="w", pady=(0, 20))
        
        # Results list
        columns = ("ID", "Type")
        results_tree = ttk.Treeview(
            main_frame,
            columns=columns,
            show="headings",
            height=10
        )
        
        # Define column headings
        for col in columns:
            results_tree.heading(col, text=col)
            
        results_tree.column("ID", width=150)
        results_tree.column("Type", width=100)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=results_tree.yview)
        results_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack the treeview and scrollbar
        results_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Populate results
        for structure in matches:
            results_tree.insert(
                "",
                "end",
                values=(structure.structure_id, structure.structure_type)
            )
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        # Select button
        ttk.Button(
            button_frame,
            text="Select",
            bootstyle="primary",
            command=lambda: self.select_from_results(results_tree, results_window)
        ).pack(side="left")
        
        # Close button
        ttk.Button(
            button_frame,
            text="Close",
            bootstyle="secondary",
            command=results_window.destroy
        ).pack(side="right")
        
    def select_from_results(self, results_tree, window):
        """Select a structure from search results"""
        selection = results_tree.selection()
        if not selection:
            Messagebox.show_warning("Please select a structure", "No Selection")
            return
            
        structure_id = results_tree.item(selection[0], "values")[0]
        window.destroy()
        self.select_structure_in_tree(structure_id)
        
    def select_structure_in_tree(self, structure_id):
        """Find and select a structure in the main treeview"""
        for item in self.structure_tree.get_children():
            if self.structure_tree.item(item, "values")[0] == structure_id:
                # Clear previous selection
                self.structure_tree.selection_set("")
                # Select the found item
                self.structure_tree.selection_set(item)
                # Ensure it's visible
                self.structure_tree.see(item)
                # Show details
                self.show_structure_details(None)
                return
        
    def change_theme(self, theme_name):
        """Change the application theme"""
        try:
            style = ttk.Style()
            current_theme = style.theme.name
            
            if current_theme == theme_name:
                return  # Already using this theme
                
            style.theme_use(theme_name)
            
            # Save the theme preference for the user (could be stored in a user_preferences table)
            self.logger.info(f"Theme changed to {theme_name}")
            
            # You could add a small notification or visual confirmation
            theme_toast = ttk.Toplevel(self.root)
            theme_toast.overrideredirect(True)  # No window decorations
            theme_toast.attributes('-topmost', True)  # Stay on top
            
            # Position at the bottom right of the main window
            x = self.root.winfo_x() + self.root.winfo_width() - 200
            y = self.root.winfo_y() + self.root.winfo_height() - 80
            theme_toast.geometry(f"200x60+{x}+{y}")
            
            # Toast content
            toast_frame = ttk.Frame(theme_toast, padding=10)
            toast_frame.pack(fill="both", expand=True)
            
            ttk.Label(
                toast_frame,
                text=f"Theme: {theme_name.capitalize()}",
                font=("Helvetica", 12, "bold")
            ).pack(pady=(0, 5))
            
            # Auto-close after 2 seconds
            theme_toast.after(2000, theme_toast.destroy)
            
        except Exception as e:
            self.logger.error(f"Theme change error: {e}", exc_info=True)
        
    def show_preferences(self):
        """Show the user preferences dialog"""
        pref_window = ttk.Toplevel(self.root)
        pref_window.title("User Preferences")
        pref_window.geometry("600x500")
        self.center_toplevel(pref_window)
        
        # Main container with padding
        main_frame = ttk.Frame(pref_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(
            main_frame, 
            text="User Preferences", 
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        ).pack(anchor="w", pady=(0, 20))
        
        # Create a notebook for preference categories
        pref_notebook = ttk.Notebook(main_frame)
        pref_notebook.pack(fill="both", expand=True)
        
        # General preferences tab
        general_frame = ttk.Frame(pref_notebook, padding=10)
        pref_notebook.add(general_frame, text="General")
        
        # Pipe Types Configuration tab
        pipe_types_frame = ttk.Frame(pref_notebook, padding=10)
        pref_notebook.add(pipe_types_frame, text="Pipe Types")

        # Display preferences tab
        display_frame = ttk.Frame(pref_notebook, padding=10)
        pref_notebook.add(display_frame, text="Display")
        
        # Units preferences tab
        units_frame = ttk.Frame(pref_notebook, padding=10)
        pref_notebook.add(units_frame, text="Units")

        # Configure the pipe types tab
        self.setup_pipe_types_configuration(pipe_types_frame)
        
        # General preferences content
        ttk.Label(general_frame, text="Default Project:").grid(row=0, column=0, sticky="w", padx=5, pady=10)
        default_project = ttk.Combobox(general_frame, state="readonly")
        default_project.grid(row=0, column=1, sticky="ew", padx=5, pady=10)
        
        # Get user's projects for the dropdown
        projects = self.db.get_user_projects(self.current_user.id)
        project_names = [p.name for p in projects['owned']] + [p.name for p in projects['shared']]
        default_project['values'] = project_names
        
        ttk.Label(general_frame, text="Auto-save interval (minutes):").grid(row=1, column=0, sticky="w", padx=5, pady=10)
        autosave_spin = ttk.Spinbox(general_frame, from_=1, to=60, width=5)
        autosave_spin.set(5)  # Default value
        autosave_spin.grid(row=1, column=1, sticky="w", padx=5, pady=10)
        
        # Create and configure a switch for auto-backup
        ttk.Label(general_frame, text="Auto-backup:").grid(row=2, column=0, sticky="w", padx=5, pady=10)
        auto_backup_var = tk.BooleanVar(value=True)
        auto_backup_switch = ttk.Checkbutton(
            general_frame, 
            bootstyle="round-toggle",
            variable=auto_backup_var
        )
        auto_backup_switch.grid(row=2, column=1, sticky="w", padx=5, pady=10)
        
        # Display preferences content
        theme_label = ttk.Label(display_frame, text="Theme:")
        theme_label.grid(row=0, column=0, sticky="w", padx=5, pady=10)
        
        # Theme dropdown
        theme_combo = ttk.Combobox(display_frame, state="readonly")
        theme_combo['values'] = ["darkly", "cosmo", "flatly", "litera", "minty", "lumen", "sandstone", "yeti"]
        theme_combo.current(0)  # Set default
        theme_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=10)
        
        # Font size
        ttk.Label(display_frame, text="Font Size:").grid(row=1, column=0, sticky="w", padx=5, pady=10)
        font_size_combo = ttk.Combobox(display_frame, state="readonly")
        font_size_combo['values'] = ["Small", "Medium", "Large"]
        font_size_combo.current(1)  # Medium by default
        font_size_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=10)
        
        # Display density
        ttk.Label(display_frame, text="Display Density:").grid(row=2, column=0, sticky="w", padx=5, pady=10)
        density_combo = ttk.Combobox(display_frame, state="readonly")
        density_combo['values'] = ["Compact", "Comfortable", "Spacious"]
        density_combo.current(1)  # Comfortable by default
        density_combo.grid(row=2, column=1, sticky="ew", padx=5, pady=10)
        
        # Units preferences content
        ttk.Label(units_frame, text="Length:").grid(row=0, column=0, sticky="w", padx=5, pady=10)
        length_combo = ttk.Combobox(units_frame, state="readonly")
        length_combo['values'] = ["Feet", "Meters"]
        length_combo.current(0)  # Feet by default
        length_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=10)
        
        ttk.Label(units_frame, text="Diameter:").grid(row=1, column=0, sticky="w", padx=5, pady=10)
        diameter_combo = ttk.Combobox(units_frame, state="readonly")
        diameter_combo['values'] = ["Inches", "Millimeters"]
        diameter_combo.current(0)  # Inches by default
        diameter_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=10)
        
        ttk.Label(units_frame, text="Elevation:").grid(row=2, column=0, sticky="w", padx=5, pady=10)
        elevation_combo = ttk.Combobox(units_frame, state="readonly")
        elevation_combo['values'] = ["Feet", "Meters"]
        elevation_combo.current(0)  # Feet by default
        elevation_combo.grid(row=2, column=1, sticky="ew", padx=5, pady=10)
        
        # Preview changes option
        preview_var = tk.BooleanVar(value=True)
        preview_check = ttk.Checkbutton(
            main_frame, 
            text="Preview changes",
            variable=preview_var
        )
        preview_check.pack(anchor="w", pady=(20, 5))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        # Save button
        ttk.Button(
            button_frame,
            text="Save Preferences",
            bootstyle="primary",
            command=lambda: self.save_preferences(
                default_project.get(),
                autosave_spin.get(),
                auto_backup_var.get(),
                theme_combo.get(),
                font_size_combo.get(),
                density_combo.get(),
                length_combo.get(),
                diameter_combo.get(),
                elevation_combo.get(),
                pref_window
            )
        ).pack(side="left")
        
        # Cancel button
        ttk.Button(
            button_frame,
            text="Cancel",
            bootstyle="secondary",
            command=pref_window.destroy
        ).pack(side="right")
        
    def setup_pipe_types_configuration(self, parent_frame):
        """Setup the pipe types configuration panel"""
        # Title
        ttk.Label(
            parent_frame, 
            text="Manage Pipe Types", 
            font=("Helvetica", 14, "bold"),
            bootstyle="primary"
        ).pack(anchor="w", pady=(0, 20))
        
        # Create a frame for the list and buttons
        list_frame = ttk.Frame(parent_frame)
        list_frame.pack(fill="both", expand=True)
        
        # Create treeview for pipe types
        columns = ("Type",)
        pipe_types_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            height=12
        )
        
        pipe_types_tree.heading("Type", text="Pipe Type")
        pipe_types_tree.column("Type", width=300)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=pipe_types_tree.yview)
        pipe_types_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack the treeview and scrollbar
        pipe_types_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Populate the list
        def refresh_pipe_types_list():
            # Clear existing items
            for item in pipe_types_tree.get_children():
                pipe_types_tree.delete(item)
            
            # Get pipe types from database
            pipe_types = self.db.get_all_pipe_types()
            
            # Add to treeview
            for pipe_type in pipe_types:
                pipe_types_tree.insert("", "end", values=(pipe_type,))
        
        refresh_pipe_types_list()
        
        # Button frame
        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        # Add button
        def add_pipe_type():
            type_name = dialogs.dialogs.Querybox.get_string(
                "Enter new pipe type name:", 
                "Add Pipe Type"
            )
            
            if type_name:
                success = self.db.add_pipe_type(type_name)
                if success:
                    Messagebox.show_info(f"Pipe type '{type_name}' added successfully", "Success")
                    refresh_pipe_types_list()
                    # Also refresh the dropdown in the main form
                    self.refresh_pipe_types()
                else:
                    Messagebox.show_error(f"Pipe type '{type_name}' already exists", "Error")
        
        ttk.Button(
            button_frame,
            text="Add Pipe Type",
            bootstyle="success",
            command=add_pipe_type
        ).pack(side="left", padx=5)
        
        # Delete button
        def delete_pipe_type():
            selection = pipe_types_tree.selection()
            if not selection:
                Messagebox.show_warning("Please select a pipe type to delete", "No Selection")
                return
            
            pipe_type = pipe_types_tree.item(selection[0], "values")[0]
            
            # Confirm deletion
            confirm = Messagebox.yesno(
                f"Are you sure you want to delete '{pipe_type}'?",
                "Confirm Deletion"
            )
            
            if confirm:
                success = self.db.delete_pipe_type(pipe_type)
                if success:
                    Messagebox.show_info(f"Pipe type '{pipe_type}' deleted successfully", "Success")
                    refresh_pipe_types_list()
                    # Also refresh the dropdown in the main form
                    self.refresh_pipe_types()
                else:
                    Messagebox.show_error(f"Failed to delete pipe type '{pipe_type}'", "Error")
        
        ttk.Button(
            button_frame,
            text="Delete Selected",
            bootstyle="danger",
            command=delete_pipe_type
        ).pack(side="left", padx=5)
    
    def save_preferences(self, default_project, autosave, auto_backup, 
                    theme, font_size, density, length_unit, 
                    diameter_unit, elevation_unit, window):
        """Save user preferences (placeholder for now)"""
        # In a full implementation, you would save these to a database or config file
        self.logger.info(f"Preferences saved: theme={theme}, units={length_unit}/{diameter_unit}/{elevation_unit}")
        
        # Apply theme immediately
        self.change_theme(theme)
        
        # Close the preferences window
        window.destroy()
        
        Messagebox.show_info("Preferences saved successfully", "Preferences")
        
    def show_project_settings(self):
        """Show the project settings dialog"""
        Messagebox.show_info("Project settings dialog coming soon", "Feature Not Implemented")
        
    def show_documentation(self):
        """Show the application documentation"""
        Messagebox.show_info("Documentation coming soon", "Feature Not Implemented")
        
    def show_about(self):
        """Show the about dialog"""
        about_window = ttk.Toplevel(self.root)
        about_window.title("About Structure Management System")
        about_window.geometry("400x300")
        self.center_toplevel(about_window)
        
        # Add padding around the entire content
        main_frame = ttk.Frame(about_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # App logo or icon could go here
        
        # Title with primary color
        ttk.Label(
            main_frame, 
            text="Structure Management System", 
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        ).pack(pady=(0, 10))
        
        ttk.Label(
            main_frame, 
            text="Version 1.0", 
            font=("Helvetica", 12)
        ).pack(pady=(0, 20))
        
        ttk.Label(
            main_frame, 
            text="A system for managing structures and pipe orders.", 
            justify="center"
        ).pack(pady=(0, 20))
        
        ttk.Label(
            main_frame, 
            text="© 2025 John Braglin / Sullivan Eastern", 
            font=("Helvetica", 10),
            bootstyle="secondary"
        ).pack(pady=(10, 0))
        
        # Close button
        ttk.Button(
            main_frame, 
            text="Close", 
            bootstyle="secondary",
            command=about_window.destroy
        ).pack(pady=(20, 0))

    def show_shortcuts(self):
        """Show keyboard shortcuts dialog"""
        shortcuts_window = ttk.Toplevel(self.root)
        shortcuts_window.title("Keyboard Shortcuts")
        shortcuts_window.geometry("500x400")
        self.center_toplevel(shortcuts_window)
        shortcuts_window.resizable(False, False)
        
        # Center the window
        shortcuts_window.transient(self.root)
        shortcuts_window.grab_set()
        
        # Main frame with padding
        main_frame = ttk.Frame(shortcuts_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(
            main_frame, 
            text="Keyboard Shortcuts", 
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        ).pack(pady=(0, 20))
        
        # Create scrollable frame for shortcuts
        shortcuts_frame = ttk.Frame(main_frame)
        shortcuts_frame.pack(fill="both", expand=True)
        
        # Add shortcuts (you can customize these based on your application)
        shortcuts = [
            ("Ctrl+N", "New Structure"),
            ("Ctrl+S", "Save Current Structure"),
            ("Ctrl+F", "Find Structure"),
            ("Ctrl+D", "Delete Selected Structure"),
            ("F5", "Refresh View"),
            ("Ctrl+R", "Generate Report"),
            ("Ctrl+E", "Export Data"),
            ("Ctrl+I", "Import Data"),
            ("Escape", "Close Dialog"),
            ("Tab", "Navigate Fields"),
            ("Enter", "Confirm Action"),
            ("Delete", "Delete Selected Item")
        ]
        
        # Display shortcuts in a formatted way
        for i, (key, description) in enumerate(shortcuts):
            shortcut_frame = ttk.Frame(shortcuts_frame)
            shortcut_frame.pack(fill="x", pady=2)
            
            # Key combination (left aligned)
            ttk.Label(
                shortcut_frame, 
                text=key, 
                font=("Courier", 10, "bold"),
                bootstyle="info",
                width=15
            ).pack(side="left", padx=(0, 20))
            
            # Description (left aligned)
            ttk.Label(
                shortcut_frame, 
                text=description,
                font=("Helvetica", 10)
            ).pack(side="left", anchor="w")
        
        # Close button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        ttk.Button(
            button_frame,
            text="Close",
            bootstyle="secondary",
            command=shortcuts_window.destroy
        ).pack(side="right")

    def add_structure(self):
        """Add a new structure to the database based on form fields with auto-base component"""
        try:
            # Get the current project ID
            project = self.db.get_project_by_name(self.current_project, self.current_user.id)
            if not project:
                Messagebox.show_error("Could not find current project", "Project Error")
                return
                    
            # Get structure data from form fields
            structure_id = self.entries['Structure ID:'].get()
            structure_type = self.entries['Structure Type:'].get().strip()
            
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
                
                # Get pipe diameter from dropdown
                pipe_diameter_text = self.entries['Pipe Diameter:'].get()
                pipe_diameter = float(pipe_diameter_text) if pipe_diameter_text else None
                
                vert_drop = float(self.entries['Drop (VF):'].get()) if self.entries['Drop (VF):'].get() else None
            except ValueError:
                Messagebox.show_error(
                    "Invalid numeric input in one or more fields. Please check all elevation, length, and diameter values.",
                    "Input Error"
                )
                return
                
            # Get other optional fields
            upstream_structure_id = self.entries['Upstream Structure:'].get() or None
            pipe_type = self.entries['Pipe Type:'].get() or None  # Get from dropdown
            frame_type = self.entries['Frame Type:'].get() or None
            description = self.entries['Description:'].get() or None
            
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
                invert_out_angle=None,  # Can be added to form if needed
                vert_drop=vert_drop,
                upstream_structure_id=upstream_structure_id,
                pipe_length=pipe_length,
                pipe_diameter=pipe_diameter,
                pipe_type=pipe_type,
                frame_type=frame_type,
                description=description
            )
            
            # Add to database
            success = self.db.add_structure(new_structure, project.id)
            
            if success:
                # Automatically add base component to the new structure
                base_added = self.auto_add_base_to_new_structure(structure_id, project.id)
                
                # Success message with base component info
                if base_added:
                    message = f"Structure {structure_id} added successfully with base component"
                else:
                    message = f"Structure {structure_id} added successfully (base component could not be auto-added)"
                
                self.show_status_toast(message)
                
                # Clear form fields
                self.clear_structure_form()
                
                # Refresh structure list
                self.load_structures()
                
                # If we're on the component tracking tab, refresh that too
                if hasattr(self, 'component_structure_tree'):
                    self.load_structures_for_components()
                    
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
            self.show_status_toast(f"Structure {structure_id} deleted successfully")
            # Remove from treeview
            self.structure_tree.delete(selection[0])
        else:
            Messagebox.show_error(f"Failed to delete structure {structure_id}", "Error")

    def clear_structure_form(self):
        """Clear all structure form fields"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def show_structure_details(self, event):
        """Show details for selected structure in treeview (updated to handle separators)"""
        # Get selected item
        selection = self.structure_tree.selection()
        if not selection:
            return
        
        # Get the values from the selected item
        values = self.structure_tree.item(selection[0], "values")
        
        # Check if this is a separator row
        if not values or not values[0] or "─── Run" in values[0]:
            # This is a separator row, don't show details
            return
            
        # Get structure ID from treeview (first column)
        structure_id = values[0]
        
        # Skip if it's an empty spacing row
        if not structure_id.strip():
            return
        
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
            self.entries['Pipe Diameter:'].set(str(int(structure.pipe_diameter)))
        if structure.pipe_type:
            self.entries['Pipe Type:'].set(structure.pipe_type)
        if structure.frame_type:
            self.entries['Frame Type:'].insert(0, structure.frame_type)
        if structure.description:
            self.entries['Description:'].insert(0, structure.description)

    def load_structures(self):
        """Load structures from database into treeview with visual separation between runs"""
        # Clear existing items in the treeview
        for item in self.structure_tree.get_children():
            self.structure_tree.delete(item)
        
        # Get current project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            return
            
        # Get structures for this project
        structures = self.db.get_all_structures(project.id)
        
        if not structures:
            return
        
        # Create a dictionary for quick lookup of structures
        structure_dict = {s.structure_id: s for s in structures}
        
        # Configure tags for visual styling
        self.setup_treeview_tags()
        
        # Group structures into runs (connected sequences)
        runs = self.group_structures_into_runs(structures, structure_dict)
        
        # Add runs to treeview with visual separation
        for run_index, run in enumerate(runs):
            # Add a separator row for each run (including the first one)
            self.add_run_separator(run_index)
            
            # Add structures in this run
            for structure_index, structure in enumerate(run):
                self.add_structure_to_treeview(structure, structure_dict, run_index, structure_index)

    def setup_treeview_tags(self):
        """Configure treeview tags for visual styling"""
        # Alternating colors for different runs
        run_colors = [
            ("#f8f9fa", "#212529"),  # Light gray background, dark text
            ("#e3f2fd", "#1565c0"),  # Light blue background, blue text
            ("#f3e5f5", "#7b1fa2"),  # Light purple background, purple text
            ("#e8f5e8", "#2e7d32"),  # Light green background, green text
            ("#fff3e0", "#ef6c00"),  # Light orange background, orange text
            ("#fce4ec", "#c2185b"),  # Light pink background, pink text
        ]
        
        # Configure run tags
        for i, (bg_color, fg_color) in enumerate(run_colors):
            self.structure_tree.tag_configure(
                f"run_{i % len(run_colors)}", 
                background=bg_color,
                foreground=fg_color
            )
        
        # Configure separator tag
        self.structure_tree.tag_configure(
            "separator", 
            background="#6c757d",
            foreground="#ffffff",
            font=("Helvetica", 9, "bold")
        )
        
        # Configure first structure in run tag (slightly darker)
        for i, (bg_color, fg_color) in enumerate(run_colors):
            # Make first structure slightly more prominent
            darker_bg = self.darken_color(bg_color, 0.1)
            self.structure_tree.tag_configure(
                f"run_{i % len(run_colors)}_first", 
                background=darker_bg,
                foreground=fg_color,
                font=("Helvetica", 10, "bold")
            )

    def darken_color(self, hex_color, factor):
        """Darken a hex color by a given factor (0.0 to 1.0)"""
        # Remove the '#' if present
        hex_color = hex_color.lstrip('#')
        
        # Convert hex to RGB
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Darken each component
        darkened = tuple(int(c * (1 - factor)) for c in rgb)
        
        # Convert back to hex
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

    def group_structures_into_runs(self, structures, structure_dict):
        """Group structures into connected runs (sequences)"""
        runs = []
        processed = set()
        
        # Find all downstream structures (structures with no upstream connections or 
        # structures that aren't referenced as upstream by any other structure)
        upstream_refs = {s.upstream_structure_id for s in structures if s.upstream_structure_id}
        
        # Start with structures that are not referenced as upstream by any other
        downstream_starts = [s for s in structures if s.structure_id not in upstream_refs]
        
        # If no clear downstream structures, start with those that have no upstream
        if not downstream_starts:
            downstream_starts = [s for s in structures if not s.upstream_structure_id]
        
        # Create runs starting from each downstream structure
        for start_structure in downstream_starts:
            if start_structure.structure_id in processed:
                continue
                
            # Build the run following upstream connections
            current_run = []
            current_structure = start_structure
            
            while current_structure and current_structure.structure_id not in processed:
                current_run.append(current_structure)
                processed.add(current_structure.structure_id)
                
                # Move to upstream structure
                if current_structure.upstream_structure_id:
                    current_structure = structure_dict.get(current_structure.upstream_structure_id)
                else:
                    current_structure = None
            
            if current_run:
                runs.append(current_run)
        
        # Handle any remaining structures (orphaned or circular references)
        remaining_structures = [s for s in structures if s.structure_id not in processed]
        for structure in remaining_structures:
            runs.append([structure])
            processed.add(structure.structure_id)
        
        return runs

    def add_run_separator(self, run_index):
        """Add a visual separator between runs"""
        separator_text = f"─── Run {run_index + 1} ───"
        
        self.structure_tree.insert(
            "", 
            "end", 
            values=(separator_text, "", "", "", "", "", "", ""),
            tags=("separator",)
        )

    def add_structure_to_treeview(self, structure, structure_dict, run_index, structure_index):
        """Add a single structure to the treeview with appropriate styling"""
        # Format values for display
        rim_elevation = f"{structure.rim_elevation:.2f}" if structure.rim_elevation is not None else "—"
        invert_out = f"{structure.invert_out_elevation:.2f}" if structure.invert_out_elevation is not None else "—"
        
        # Calculate depth (Rim Elevation - Invert Out Elevation)
        if structure.rim_elevation is not None and structure.invert_out_elevation is not None:
            depth = structure.rim_elevation - structure.invert_out_elevation
            depth_text = f"{depth:.2f}"
        else:
            depth_text = "—"
        
        # Get upstream structure ID
        upstream_id = structure.upstream_structure_id if structure.upstream_structure_id else "—"
        
        # Calculate slope
        slope_text = self.calculate_slope(structure, structure_dict)
        
        # Use the pipe_type field for description
        description = structure.pipe_type or ""
        
        # Determine which tag to use
        color_index = run_index % 6  # Cycle through 6 colors
        if structure_index == 0:  # First structure in run
            tag = f"run_{color_index}_first"
        else:
            tag = f"run_{color_index}"
        
        # Add to treeview with appropriate styling
        self.structure_tree.insert(
            "", 
            "end", 
            values=(
                structure.structure_id, 
                structure.structure_type, 
                rim_elevation,
                invert_out,
                depth_text,
                upstream_id,
                slope_text,
                description
            ),
            tags=(tag,)
        )

    # Alternative method: Add spacing between runs instead of separator rows
    def load_structures_with_spacing(self):
        """Alternative version: Load structures with empty rows between runs for spacing"""
        # Clear existing items in the treeview
        for item in self.structure_tree.get_children():
            self.structure_tree.delete(item)
        
        # Get current project ID
        project = self.db.get_project_by_name(self.current_project, self.current_user.id)
        if not project:
            return
            
        # Get structures for this project
        structures = self.db.get_all_structures(project.id)
        
        if not structures:
            return
        
        # Create a dictionary for quick lookup of structures
        structure_dict = {s.structure_id: s for s in structures}
        
        # Configure tags for visual styling
        self.setup_treeview_tags()
        
        # Group structures into runs
        runs = self.group_structures_into_runs(structures, structure_dict)
        
        # Add runs to treeview with spacing
        for run_index, run in enumerate(runs):
            # Add spacing between runs (except before the first run)
            if run_index > 0:
                # Add empty row for spacing
                self.structure_tree.insert("", "end", values=("", "", "", "", "", "", "", ""))
            
            # Add structures in this run
            for structure_index, structure in enumerate(run):
                self.add_structure_to_treeview(structure, structure_dict, run_index, structure_index)

    # Method to toggle between different visual styles
    def toggle_run_visualization(self):
        """Toggle between different run visualization modes"""
        if not hasattr(self, 'current_visualization_mode'):
            self.current_visualization_mode = 'separated'
        
        if self.current_visualization_mode == 'separated':
            self.current_visualization_mode = 'spaced'
            self.load_structures_with_spacing()
        else:
            self.current_visualization_mode = 'separated'
            self.load_structures()
        
        # Update button text or status
        mode_text = "Separated Runs" if self.current_visualization_mode == 'separated' else "Spaced Runs"
        print(f"Visualization mode: {mode_text}")

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
            structure_type = self.entries['Structure Type:'].get().strip()
            
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
                
                # Get pipe diameter from dropdown
                pipe_diameter_text = self.entries['Pipe Diameter:'].get()
                pipe_diameter = float(pipe_diameter_text) if pipe_diameter_text else None
                
                vert_drop = float(self.entries['Drop (VF):'].get()) if self.entries['Drop (VF):'].get() else None
            except ValueError:
                Messagebox.show_error(
                    "Invalid numeric input in one or more fields. Please check all elevation, length, and diameter values.",
                    "Input Error"
                )
                return
                
            # Get other optional fields
            upstream_structure_id = self.entries['Upstream Structure:'].get() or None
            pipe_type = self.entries['Pipe Type:'].get() or None  # Get from dropdown
            frame_type = self.entries['Frame Type:'].get() or None
            description = self.entries['Description:'].get() or None
            
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
                frame_type=frame_type,
                description=description,
                group_name=existing_structure.group_name  # Preserve existing group
            )
            
            # Update in database
            success = self.db.update_structure(updated_structure, project.id)
            
            if success:
                self.show_status_toast(f"Structure {structure_id} updated successfully")
                
                # Update in treeview
                for item in self.structure_tree.get_children():
                    if self.structure_tree.item(item, "values")[0] == structure_id:
                        self.structure_tree.item(item, values=(structure_id, structure_type, "Active"))
                        break
                        
                # Refresh structure list
                self.load_structures()
                
                # Refresh pipe totals summary to reflect any changes in pipe length
                self.calculate_project_pipe_totals()
            else:
                Messagebox.show_error("Failed to update structure", "Database Error")
                
        except Exception as e:
            Messagebox.show_error(f"An error occurred: {str(e)}", "System Error")

    def sort_structures_by_flow(self, structures):
        """
        Sort structures by flow direction (downstream to upstream).
        Structures with no upstream_structure_id come first (most downstream),
        followed by their upstream connections in order.
        """
        if not structures:
            return []
        
        # Create a dictionary for quick lookup
        structure_dict = {s.structure_id: s for s in structures}
        sorted_list = []
        processed = set()
        
        def add_structure_and_upstream(structure):
            """Recursively add structure and its upstream chain"""
            if structure.structure_id in processed:
                return
            
            # Add current structure
            sorted_list.append(structure)
            processed.add(structure.structure_id)
            
            # Find and add upstream structure if it exists
            if structure.upstream_structure_id and structure.upstream_structure_id in structure_dict:
                upstream_structure = structure_dict[structure.upstream_structure_id]
                add_structure_and_upstream(upstream_structure)
        
        # Start with structures that have no downstream connections
        # (structures that are not referenced as upstream by any other structure)
        downstream_structures = []
        upstream_refs = {s.upstream_structure_id for s in structures if s.upstream_structure_id}
        
        for structure in structures:
            if structure.structure_id not in upstream_refs:
                # This structure is not referenced as upstream by any other structure
                # It's likely a downstream/outlet structure
                downstream_structures.append(structure)
        
        # If no clear downstream structures found, start with structures that have no upstream
        if not downstream_structures:
            downstream_structures = [s for s in structures if not s.upstream_structure_id]
        
        # Process each downstream structure and its upstream chain
        for structure in downstream_structures:
            add_structure_and_upstream(structure)
        
        # Add any remaining structures that weren't processed
        # (handles cases with circular references or orphaned structures)
        for structure in structures:
            if structure.structure_id not in processed:
                sorted_list.append(structure)
                processed.add(structure.structure_id)
        
        return sorted_list

    def calculate_slope(self, structure, structure_dict):
        """
        Calculate slope using the formula:
        (upstream inv out - (Downstream Inv out + Drop vf)) / Pipe length
        
        Returns formatted slope text or "—" if calculation cannot be performed
        """
        # Check if we have an upstream structure
        if not structure.upstream_structure_id:
            return "—"
        
        # Check if upstream structure exists in our data
        if structure.upstream_structure_id not in structure_dict:
            return "—"
        
        upstream_structure = structure_dict[structure.upstream_structure_id]
        
        # Check if we have all required values
        if (structure.invert_out_elevation is None or 
            upstream_structure.invert_out_elevation is None or 
            structure.pipe_length is None or 
            structure.pipe_length <= 0):
            return "—"
        
        # Get drop value (vert_drop), default to 0 if not provided
        drop_vf = structure.vert_drop if structure.vert_drop is not None else 0
        
        try:
            # Calculate slope: (upstream inv out - (Downstream Inv out + Drop vf)) / Pipe length
            downstream_adjusted = structure.invert_out_elevation + drop_vf
            elevation_difference = upstream_structure.invert_out_elevation - downstream_adjusted
            slope = elevation_difference / structure.pipe_length
            
            # Format as percentage with 2 decimal places, rounded to nearest hundredth
            slope_percentage = slope * 100
            # Round to 2 decimal places (nearest hundredth)
            rounded_slope = round(slope_percentage, 2)
            return f"{rounded_slope:.2f}%"
            
        except (TypeError, ZeroDivisionError):
            return "—"

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
            
            if structure.upstream_structure_id:
                report_text.insert(tk.END, f"  Upstream Structure: {structure.upstream_structure_id}\n", "data")
            if structure.pipe_length:
                report_text.insert(tk.END, f"  Pipe Length: {structure.pipe_length}\n", "data")
            if structure.pipe_diameter:
                report_text.insert(tk.END, f"  Pipe Diameter: {structure.pipe_diameter}\n", "data")
            if structure.pipe_type:
                report_text.insert(tk.END, f"  Pipe Type: {structure.pipe_type}\n", "data")
            
        
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