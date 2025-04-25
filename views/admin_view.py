import tkinter as tk
from tkinter import ttk, messagebox
from auth_controller import AuthController
from courier_controller import CourierController
from views.auth_view import LoginView
from styles import Styles

class AdminDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.auth = AuthController()
        self.courier_ctrl = CourierController()
        self.styles = Styles()
        
        self.configure(bg=self.styles.bg_color)
        self.create_widgets()
    
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self, bg=self.styles.bg_color)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(
            header_frame, 
            text="Admin Dashboard", 
            font=self.styles.header_font,
            bg=self.styles.bg_color,
            fg=self.styles.header_fg
        ).pack(side='left')
        
        # Logout Button
        logout_btn = ttk.Button(
            header_frame, 
            text="Logout", 
            command=self.logout,
            style='TButton'
        )
        logout_btn.pack(side='right')
        
        # Main Content
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_users_tab()
        self.create_couriers_tab()
        self.create_packages_tab()
    
    def create_users_tab(self):
        users_tab = ttk.Frame(self.notebook)
        self.notebook.add(users_tab, text="Users")
        
        # Treeview for users
        columns = ('id', 'username', 'role', 'full_name', 'email', 'phone', 'created_at')
        self.users_tree = ttk.Treeview(
            users_tab, 
            columns=columns, 
            show='headings',
            selectmode='browse'
        )
        
        # Define headings
        self.users_tree.heading('id', text='ID')
        self.users_tree.heading('username', text='Username')
        self.users_tree.heading('role', text='Role')
        self.users_tree.heading('full_name', text='Full Name')
        self.users_tree.heading('email', text='Email')
        self.users_tree.heading('phone', text='Phone')
        self.users_tree.heading('created_at', text='Created At')
        
        # Set column widths
        self.users_tree.column('id', width=50)
        self.users_tree.column('username', width=100)
        self.users_tree.column('role', width=80)
        self.users_tree.column('full_name', width=150)
        self.users_tree.column('email', width=150)
        self.users_tree.column('phone', width=100)
        self.users_tree.column('created_at', width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(users_tab, orient='vertical', command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.users_tree.pack(fill='both', expand=True)
        
        # Load data
        self.load_users()
    
    def load_users(self):
        conn = self.auth.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        
        # Clear existing data
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        # Insert new data
        for user in users:
            self.users_tree.insert('', 'end', values=user)
    
    def create_couriers_tab(self):
        couriers_tab = ttk.Frame(self.notebook)
        self.notebook.add(couriers_tab, text="Couriers")
        
        # Add Courier Button
        add_btn = ttk.Button(
            couriers_tab, 
            text="Add Courier", 
            command=self.show_add_courier_dialog,
            style='TButton'
        )
        add_btn.pack(pady=5, anchor='ne', padx=10)
        
        # Treeview for couriers
        columns = ('id', 'name', 'vehicle', 'license', 'status')
        self.couriers_tree = ttk.Treeview(
            couriers_tab, 
            columns=columns, 
            show='headings',
            selectmode='browse'
        )
        
        # Define headings
        self.couriers_tree.heading('id', text='ID')
        self.couriers_tree.heading('name', text='Name')
        self.couriers_tree.heading('vehicle', text='Vehicle Type')
        self.couriers_tree.heading('license', text='License Plate')
        self.couriers_tree.heading('status', text='Status')
        
        # Set column widths
        self.couriers_tree.column('id', width=50)
        self.couriers_tree.column('name', width=150)
        self.couriers_tree.column('vehicle', width=100)
        self.couriers_tree.column('license', width=100)
        self.couriers_tree.column('status', width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(couriers_tab, orient='vertical', command=self.couriers_tree.yview)
        self.couriers_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.couriers_tree.pack(fill='both', expand=True)
        
        # Load data
        self.load_couriers()
    
    def load_couriers(self):
        conn = self.auth.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.id, u.full_name, c.vehicle_type, c.license_plate, c.status 
            FROM couriers c
            JOIN users u ON c.user_id = u.id
            ORDER BY c.id
        """)
        couriers = cursor.fetchall()
        
        # Clear existing data
        for item in self.couriers_tree.get_children():
            self.couriers_tree.delete(item)
        
        # Insert new data
        for courier in couriers:
            self.couriers_tree.insert('', 'end', values=courier)
    
    def show_add_courier_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add New Courier")
        dialog.geometry("400x300")
        
        tk.Label(dialog, text="Username:").pack(pady=(10, 0))
        username_entry = ttk.Entry(dialog)
        username_entry.pack(pady=5)
        
        tk.Label(dialog, text="Password:").pack()
        password_entry = ttk.Entry(dialog, show="*")
        password_entry.pack(pady=5)
        
        tk.Label(dialog, text="Full Name:").pack()
        full_name_entry = ttk.Entry(dialog)
        full_name_entry.pack(pady=5)
        
        tk.Label(dialog, text="Vehicle Type:").pack()
        vehicle_entry = ttk.Entry(dialog)
        vehicle_entry.pack(pady=5)
        
        tk.Label(dialog, text="License Plate:").pack()
        license_entry = ttk.Entry(dialog)
        license_entry.pack(pady=5)
        
        def add_courier():
            username = username_entry.get()
            password = password_entry.get()
            full_name = full_name_entry.get()
            vehicle = vehicle_entry.get()
            license_plate = license_entry.get()
            
            if not all([username, password, full_name, vehicle, license_plate]):
                messagebox.showerror("Error", "All fields are required")
                return
            
            conn = self.auth.db.get_connection()
            cursor = conn.cursor()
            
            try:
                # Insert user
                hashed_password = self.auth.hash_password(password)
                cursor.execute(
                    "INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
                    (username, hashed_password, 'courier', full_name)
                )
                user_id = cursor.lastrowid
                
                # Insert courier
                cursor.execute(
                    "INSERT INTO couriers (user_id, vehicle_type, license_plate) VALUES (?, ?, ?)",
                    (user_id, vehicle, license_plate)
                )
                
                conn.commit()
                messagebox.showinfo("Success", "Courier added successfully")
                self.load_couriers()
                dialog.destroy()
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error", str(e))
        
        ttk.Button(dialog, text="Add Courier", command=add_courier).pack(pady=10)
    
    def create_packages_tab(self):
        packages_tab = ttk.Frame(self.notebook)
        self.notebook.add(packages_tab, text="Packages")
        
        # Treeview for packages
        columns = ('id', 'tracking', 'sender', 'receiver', 'courier', 'status', 'created', 'estimated')
        self.packages_tree = ttk.Treeview(
            packages_tab, 
            columns=columns, 
            show='headings',
            selectmode='browse'
        )
        
        # Define headings
        self.packages_tree.heading('id', text='ID')
        self.packages_tree.heading('tracking', text='Tracking #')
        self.packages_tree.heading('sender', text='Sender')
        self.packages_tree.heading('receiver', text='Receiver')
        self.packages_tree.heading('courier', text='Courier')
        self.packages_tree.heading('status', text='Status')
        self.packages_tree.heading('created', text='Created At')
        self.packages_tree.heading('estimated', text='Est. Delivery')
        
        # Set column widths
        self.packages_tree.column('id', width=50)
        self.packages_tree.column('tracking', width=120)
        self.packages_tree.column('sender', width=150)
        self.packages_tree.column('receiver', width=150)
        self.packages_tree.column('courier', width=150)
        self.packages_tree.column('status', width=100)
        self.packages_tree.column('created', width=120)
        self.packages_tree.column('estimated', width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(packages_tab, orient='vertical', command=self.packages_tree.yview)
        self.packages_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.packages_tree.pack(fill='both', expand=True)
        
        # Load data
        self.load_packages()
    
    def load_packages(self):
        conn = self.auth.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.id, p.tracking_number, 
                   s.full_name as sender, r.full_name as receiver,
                   c.full_name as courier, p.status, p.created_at, p.estimated_delivery
            FROM packages p
            JOIN customers s ON p.sender_id = s.id
            JOIN customers r ON p.receiver_id = r.id
            JOIN users sender ON s.user_id = sender.id
            JOIN users receiver ON r.user_id = receiver.id
            LEFT JOIN couriers courier ON p.courier_id = courier.id
            LEFT JOIN users c ON courier.user_id = c.id
            ORDER BY p.created_at DESC
        """)
        packages = cursor.fetchall()
        
        # Clear existing data
        for item in self.packages_tree.get_children():
            self.packages_tree.delete(item)
        
        # Insert new data
        for pkg in packages:
            self.packages_tree.insert('', 'end', values=pkg)
    
    def logout(self):
        self.auth.logout()
        self.controller.show_frame(LoginView)