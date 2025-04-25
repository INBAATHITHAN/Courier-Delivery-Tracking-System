import tkinter as tk
from tkinter import ttk, messagebox
from auth_controller import AuthController
from views.admin_view import AdminDashboard
from views.courier_view import CourierDashboard
from styles import Styles

CustomerDashboard = None
class LoginView(tk.Frame):
    def __init__(self, parent, controller, customer_dashboard_class):
        self.customer_dashboard_class = customer_dashboard_class
        super().__init__(parent)
        self.controller = controller
        self.auth = AuthController()
        self.styles = Styles()
        
        self.configure(bg=self.styles.bg_color)
        
        # Header
        header = tk.Label(
            self, 
            text="Courier Tracking System", 
            font=self.styles.header_font,
            bg=self.styles.bg_color,
            fg=self.styles.header_fg
        )
        header.pack(pady=20)
        
        # Login Frame
        login_frame = tk.Frame(self, bg=self.styles.bg_color)
        login_frame.pack(pady=20)
        
        # Username
        tk.Label(
            login_frame, 
            text="Username:", 
            bg=self.styles.bg_color,
            font=self.styles.label_font
        ).grid(row=0, column=0, padx=5, pady=5, sticky='e')
        
        self.username_entry = ttk.Entry(login_frame, font=self.styles.entry_font)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Password
        tk.Label(
            login_frame, 
            text="Password:", 
            bg=self.styles.bg_color,
            font=self.styles.label_font
        ).grid(row=1, column=0, padx=5, pady=5, sticky='e')
        
        self.password_entry = ttk.Entry(login_frame, show="*", font=self.styles.entry_font)
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Login Button
        login_btn = ttk.Button(
            login_frame, 
            text="Login", 
            command=self.login,
            style='TButton'
        )
        login_btn.grid(row=2, column=1, pady=10, sticky='e')
        
        # Register Link
        register_label = tk.Label(
            login_frame, 
            text="Don't have an account? Register here", 
            fg="blue", 
            cursor="hand2",
            bg=self.styles.bg_color,
            font=self.styles.link_font
        )
        register_label.grid(row=3, column=0, columnspan=2, pady=10)
        register_label.bind("<Button-1>", lambda e: controller.show_frame(RegisterView))
    
    def login_successful(self):
        global CustomerDashboard
        if CustomerDashboard is None:  # Load ONLY when needed
            from views.customer_view import CustomerDashboard
        # Now use CustomerDashboard normally
        self.controller.show_frame(CustomerDashboard)


    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        if self.auth.login(username, password):
            user = self.auth.get_current_user()
            if user.role == 'admin':
                self.controller.show_frame(AdminDashboard)
            elif user.role == 'courier':
                self.controller.show_frame(CourierDashboard)
            else:
                self.controller.show_frame(self.customer_dashboard_class)
        else:
            messagebox.showerror("Error", "Invalid username or password")

class RegisterView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.auth = AuthController()
        self.styles = Styles()
        
        self.configure(bg=self.styles.bg_color)
        
        # Header
        header = tk.Label(
            self, 
            text="Customer Registration", 
            font=self.styles.header_font,
            bg=self.styles.bg_color,
            fg=self.styles.header_fg
        )
        header.pack(pady=20)
        
        # Registration Frame
        reg_frame = tk.Frame(self, bg=self.styles.bg_color)
        reg_frame.pack(pady=10)
        
        # Form fields
        fields = [
            ("Username:", "username"),
            ("Password:", "password", True),
            ("Full Name:", "full_name"),
            ("Email:", "email"),
            ("Phone:", "phone"),
            ("Address:", "address"),
            ("City:", "city"),
            ("State:", "state"),
            ("ZIP Code:", "zip_code")
        ]
        
        self.entries = {}
        
        for i, field in enumerate(fields):
            label_text = field[0]
            field_name = field[1]
            is_password = field[2] if len(field) > 2 else False
            
            tk.Label(
                reg_frame, 
                text=label_text, 
                bg=self.styles.bg_color,
                font=self.styles.label_font
            ).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            
            entry = ttk.Entry(
                reg_frame, 
                show="*" if is_password else None,
                font=self.styles.entry_font
            )
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[field_name] = entry
        
        # Register Button
        register_btn = ttk.Button(
            reg_frame, 
            text="Register", 
            command=self.register,
            style='TButton'
        )
        register_btn.grid(row=len(fields), column=1, pady=10, sticky='e')
        
        # Back to Login Link
        login_label = tk.Label(
            reg_frame, 
            text="Already have an account? Login here", 
            fg="blue", 
            cursor="hand2",
            bg=self.styles.bg_color,
            font=self.styles.link_font
        )
        login_label.grid(row=len(fields)+1, column=0, columnspan=2, pady=10)
        login_label.bind("<Button-1>", lambda e: controller.show_frame(LoginView))
    
    def register(self):
        data = {field: self.entries[field].get() for field in self.entries}
        
        # Validate required fields
        required = ['username', 'password', 'full_name', 'address', 'city', 'state', 'zip_code']
        for field in required:
            if not data.get(field):
                messagebox.showerror("Error", f"Please enter {field.replace('_', ' ')}")
                return
        
        success, message = self.auth.register_customer(
            data['username'],
            data['password'],
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
            self.controller.show_frame(LoginView)
        else:
            messagebox.showerror("Error", message)