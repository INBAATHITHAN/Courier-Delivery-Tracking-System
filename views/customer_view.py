import tkinter as tk
from tkinter import ttk, messagebox
from auth_controller import AuthController
from courier_controller import CourierController
from customer_controller import CustomerController
from views.auth_view import LoginView
from styles import Styles

LoginView = None

class CustomerDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.auth = AuthController()
        self.courier_ctrl = CourierController()
        self.customer_ctrl = CustomerController()
        self.styles = Styles()
        
        self.configure(bg=self.styles.bg_color)
        self.create_widgets()
        self.load_packages()
        self.load_profile()
    
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self, bg=self.styles.bg_color)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        user = self.auth.get_current_user()
        tk.Label(
            header_frame, 
            text=f"Welcome, {user.full_name}", 
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
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_packages_tab()
        self.create_profile_tab()
        self.create_tracking_tab()
    
    def create_packages_tab(self):
        packages_tab = ttk.Frame(self.notebook)
        self.notebook.add(packages_tab, text="My Packages")
        
        # New Package Button
        new_pkg_btn = ttk.Button(
            packages_tab, 
            text="New Package", 
            command=self.show_new_package_dialog,
            style='TButton'
        )
        new_pkg_btn.pack(pady=5, anchor='ne', padx=10)
        
        # Treeview for packages
        columns = ('id', 'tracking', 'receiver', 'status', 'created', 'estimated')
        self.packages_tree = ttk.Treeview(
            packages_tab, 
            columns=columns, 
            show='headings',
            selectmode='browse'
        )
        
        # Define headings
        self.packages_tree.heading('id', text='ID')
        self.packages_tree.heading('tracking', text='Tracking #')
        self.packages_tree.heading('receiver', text='Receiver')
        self.packages_tree.heading('status', text='Status')
        self.packages_tree.heading('created', text='Created At')
        self.packages_tree.heading('estimated', text='Est. Delivery')
        
        # Set column widths
        self.packages_tree.column('id', width=50)
        self.packages_tree.column('tracking', width=120)
        self.packages_tree.column('receiver', width=150)
        self.packages_tree.column('status', width=100)
        self.packages_tree.column('created', width=120)
        self.packages_tree.column('estimated', width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(packages_tab, orient='vertical', command=self.packages_tree.yview)
        self.packages_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.packages_tree.pack(fill='both', expand=True)
        
        # View Button
        view_btn = ttk.Button(
            packages_tab, 
            text="View Details", 
            command=self.view_package_details,
            style='TButton'
        )
        view_btn.pack(pady=10)
    
    def load_packages(self):
        user = self.auth.get_current_user()
        customer = self.customer_ctrl.get_customer_by_id(user.customer_id)
        packages = self.customer_ctrl.get_customer_packages(customer.customer_id)
        
        # Clear existing data
        for item in self.packages_tree.get_children():
            self.packages_tree.delete(item)
        
        # Insert new data
        for pkg in packages:
            self.packages_tree.insert('', 'end', values=(
                pkg['id'],
                pkg['tracking_number'],
                pkg['receiver_name'],
                pkg['status'],
                pkg['created_at'],
                pkg['estimated_delivery']
            ))
    
    def show_new_package_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Create New Package")
        dialog.geometry("500x400")
        
        user = self.auth.get_current_user()
        
        # Form fields
        fields = [
            ("Receiver Name:", "receiver_name"),
            ("Receiver Address:", "receiver_address"),
            ("Receiver City:", "receiver_city"),
            ("Receiver State:", "receiver_state"),
            ("Receiver ZIP Code:", "receiver_zip"),
            ("Description:", "description"),
            ("Weight (kg):", "weight"),
            ("Dimensions (LxWxH):", "dimensions")
        ]
        
        self.entries = {}
        
        for i, field in enumerate(fields):
            label_text = field[0]
            field_name = field[1]
            
            tk.Label(dialog, text=label_text).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            
            entry = ttk.Entry(dialog)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[field_name] = entry
        
        def create_package():
            data = {field: self.entries[field].get() for field in self.entries}
            
            # Validate required fields
            required = ['receiver_name', 'receiver_address', 'receiver_city', 'receiver_state', 'receiver_zip']
            for field in required:
                if not data.get(field):
                    messagebox.showerror("Error", f"Please enter {field.replace('_', ' ')}")
                    return
            
            try:
                # First create receiver customer (simplified for demo)
                conn = self.auth.db.get_connection()
                cursor = conn.cursor()
                
                cursor.execute(
                    "INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
                    (f"temp_{data['receiver_name'].lower().replace(' ', '_')}", 'temp123', 'customer', data['receiver_name'])
                )
                user_id = cursor.lastrowid
                
                cursor.execute(
                    "INSERT INTO customers (user_id, address, city, state, zip_code) VALUES (?, ?, ?, ?, ?)",
                    (user_id, data['receiver_address'], data['receiver_city'], data['receiver_state'], data['receiver_zip'])
                )
                receiver_id = cursor.lastrowid
                
                # Now create package
                sender_id = user.customer_id
                success, result = self.courier_ctrl.create_package(
                    sender_id,
                    receiver_id,
                    data['description'],
                    float(data['weight']) if data['weight'] else 0.5,
                    data['dimensions'],
                    "My Address",  # Simplified pickup address
                    f"{data['receiver_address']}, {data['receiver_city']}, {data['receiver_state']} {data['receiver_zip']}"
                )
                
                if success:
                    conn.commit()
                    messagebox.showinfo("Success", f"Package created! Tracking #: {self.courier_ctrl.get_package_by_id(result).tracking_number}")
                    self.load_packages()
                    dialog.destroy()
                else:
                    conn.rollback()
                    messagebox.showerror("Error", result)
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error", str(e))
        
        ttk.Button(dialog, text="Create Package", command=create_package).grid(row=len(fields), column=1, pady=10)
    
    def view_package_details(self):
        selected = self.packages_tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a package first")
            return
        
        package_data = self.packages_tree.item(selected, 'values')
        package_id = package_data[0]
        
        package = self.courier_ctrl.get_package_by_id(package_id)
        history = self.courier_ctrl.get_tracking_history(package_id)
        
        dialog = tk.Toplevel(self)
        dialog.title("Package Details")
        dialog.geometry("600x400")
        
        # Package Info Frame
        info_frame = tk.Frame(dialog)
        info_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(info_frame, text="Tracking Number:", font='bold').grid(row=0, column=0, sticky='e')
        tk.Label(info_frame, text=package.tracking_number).grid(row=0, column=1, sticky='w')
        
        tk.Label(info_frame, text="Receiver:", font='bold').grid(row=1, column=0, sticky='e')
        tk.Label(info_frame, text=package_data[2]).grid(row=1, column=1, sticky='w')
        
        tk.Label(info_frame, text="Status:", font='bold').grid(row=2, column=0, sticky='e')
        tk.Label(info_frame, text=package.status).grid(row=2, column=1, sticky='w')
        
        tk.Label(info_frame, text="Delivery Address:", font='bold').grid(row=3, column=0, sticky='e')
        tk.Label(info_frame, text=package.delivery_address, wraplength=300).grid(row=3, column=1, sticky='w')
        
        tk.Label(info_frame, text="Estimated Delivery:", font='bold').grid(row=4, column=0, sticky='e')
        tk.Label(info_frame, text=package.estimated_delivery).grid(row=4, column=1, sticky='w')
        
        # Tracking History
        history_frame = tk.Frame(dialog)
        history_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(history_frame, text="Tracking History:", font='bold').pack(anchor='w')
        
        history_text = tk.Text(history_frame, wrap='word', height=10)
        scrollbar = ttk.Scrollbar(history_frame, orient='vertical', command=history_text.yview)
        history_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        history_text.pack(fill='both', expand=True)
        
        for record in history:
            history_text.insert('end', 
                f"{record.timestamp}: {record.status}\n"
                f"Location: {record.location or 'N/A'}\n"
                f"Notes: {record.notes or 'None'}\n\n"
            )
        
        history_text.config(state='disabled')
    
    def create_profile_tab(self):
        profile_tab = ttk.Frame(self.notebook)
        self.notebook.add(profile_tab, text="My Profile")
        
        # Profile Form
        self.profile_frame = tk.Frame(profile_tab, bg=self.styles.bg_color)
        self.profile_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Will be populated by load_profile()
    
    def load_profile(self):
        # Clear existing widgets
        for widget in self.profile_frame.winfo_children():
            widget.destroy()
        
        user = self.auth.get_current_user()
        customer = self.customer_ctrl.get_customer_by_id(user.customer_id)
        
        # Form fields
        fields = [
            ("Username:", "username", customer.username, True),
            ("Full Name:", "full_name", customer.full_name),
            ("Email:", "email", customer.email),
            ("Phone:", "phone", customer.phone),
            ("Address:", "address", customer.address),
            ("City:", "city", customer.city),
            ("State:", "state", customer.state),
            ("ZIP Code:", "zip_code", customer.zip_code)
        ]
        
        self.profile_entries = {}
        
        for i, field in enumerate(fields):
            label_text = field[0]
            field_name = field[1]
            field_value = field[2]
            readonly = field[3] if len(field) > 3 else False
            
            tk.Label(
                self.profile_frame, 
                text=label_text, 
                bg=self.styles.bg_color,
                font=self.styles.label_font
            ).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            
            if readonly:
                entry = ttk.Entry(
                    self.profile_frame, 
                    font=self.styles.entry_font,
                    state='readonly'
                )
                entry.insert(0, field_value)
            else:
                entry = ttk.Entry(
                    self.profile_frame, 
                    font=self.styles.entry_font
                )
                entry.insert(0, field_value)
            
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.profile_entries[field_name] = entry
        
        # Update Button
        update_btn = ttk.Button(
            self.profile_frame, 
            text="Update Profile", 
            command=self.update_profile,
            style='TButton'
        )
        update_btn.grid(row=len(fields), column=1, pady=10, sticky='e')
    
    def update_profile(self):
        data = {
            'full_name': self.profile_entries['full_name'].get(),
            'email': self.profile_entries['email'].get(),
            'phone': self.profile_entries['phone'].get(),
            'address': self.profile_entries['address'].get(),
            'city': self.profile_entries['city'].get(),
            'state': self.profile_entries['state'].get(),
            'zip_code': self.profile_entries['zip_code'].get()
        }
        
        user = self.auth.get_current_user()
        success, message = self.customer_ctrl.update_customer_profile(
            user.customer_id,
            data['full_name'],
            data['email'],
            data['phone'],
            data['address'],
            data['city'],
            data['state'],
            data['zip_code']
        )
        
        if success:
            messagebox.showinfo("Success", message)
            self.load_profile()  # Refresh profile view
        else:
            messagebox.showerror("Error", message)
    
    def create_tracking_tab(self):
        tracking_tab = ttk.Frame(self.notebook)
        self.notebook.add(tracking_tab, text="Track Package")
        
        # Tracking Form
        track_frame = tk.Frame(tracking_tab, bg=self.styles.bg_color)
        track_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(
            track_frame, 
            text="Enter Tracking Number:", 
            bg=self.styles.bg_color,
            font=self.styles.label_font
        ).pack(side='left')
        
        self.tracking_entry = ttk.Entry(track_frame, font=self.styles.entry_font)
        self.tracking_entry.pack(side='left', padx=5)
        
        track_btn = ttk.Button(
            track_frame, 
            text="Track", 
            command=self.track_package,
            style='TButton'
        )
        track_btn.pack(side='left')
        
        # Results Frame
        self.track_results = tk.Frame(tracking_tab, bg=self.styles.bg_color)
        self.track_results.pack(fill='both', expand=True, padx=10, pady=10)
    
    def track_package(self):
        tracking_number = self.tracking_entry.get()
        if not tracking_number:
            messagebox.showwarning("Warning", "Please enter a tracking number")
            return
        
        package = self.courier_ctrl.get_package_by_tracking_number(tracking_number)
        if not package:
            messagebox.showerror("Error", "Package not found")
            return
        
        history = self.courier_ctrl.get_tracking_history(package.id)
        
        # Clear previous results
        for widget in self.track_results.winfo_children():
            widget.destroy()
        
        # Package Info
        info_frame = tk.Frame(self.track_results, bg=self.styles.bg_color)
        info_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(
            info_frame, 
            text=f"Tracking Number: {package.tracking_number}", 
            font=('Arial', 12, 'bold'),
            bg=self.styles.bg_color
        ).pack(anchor='w')
        
        tk.Label(
            info_frame, 
            text=f"Status: {package.status.upper()}", 
            font=('Arial', 12),
            bg=self.styles.bg_color
        ).pack(anchor='w')
        
        tk.Label(
            info_frame, 
            text=f"Estimated Delivery: {package.estimated_delivery}", 
            font=('Arial', 12),
            bg=self.styles.bg_color
        ).pack(anchor='w')
        
        # Tracking History
        history_frame = tk.Frame(self.track_results, bg=self.styles.bg_color)
        history_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(
            history_frame, 
            text="Tracking History:", 
            font=('Arial', 12, 'bold'),
            bg=self.styles.bg_color
        ).pack(anchor='w')
        
        history_text = tk.Text(
            history_frame, 
            wrap='word', 
            height=10,
            font=('Arial', 11)
        )
        scrollbar = ttk.Scrollbar(history_frame, orient='vertical', command=history_text.yview)
        history_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        history_text.pack(fill='both', expand=True)
        
        for record in history:
            history_text.insert('end', 
                f"{record.timestamp}: {record.status}\n"
                f"Location: {record.location or 'N/A'}\n"
                f"Notes: {record.notes or 'None'}\n\n"
            )
        
        history_text.config(state='disabled')
    
    def some_method_that_needs_loginview(self):
        global LoginView
        if LoginView is None:  # Load ONLY when needed
            from views.auth_view import LoginView
        # Now use LoginView normally
        self.controller.show_frame(LoginView)

    def logout(self):
        self.auth.logout()
        self.controller.show_frame(LoginView)