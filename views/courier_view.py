import tkinter as tk
from tkinter import ttk, messagebox
from auth_controller import AuthController
from courier_controller import CourierController
from views.auth_view import LoginView
from styles import Styles

class CourierDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.auth = AuthController()
        self.courier_ctrl = CourierController()
        self.styles = Styles()
        
        self.configure(bg=self.styles.bg_color)
        self.create_widgets()
        self.load_packages()
    
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self, bg=self.styles.bg_color)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        user = self.auth.get_current_user()
        tk.Label(
            header_frame, 
            text=f"Courier Dashboard - {user.full_name}", 
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
        
        # Status Frame
        status_frame = tk.Frame(self, bg=self.styles.bg_color)
        status_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(
            status_frame, 
            text="Current Status:", 
            bg=self.styles.bg_color,
            font=self.styles.label_font
        ).pack(side='left')
        
        self.status_var = tk.StringVar(value=user.status)
        status_options = ['available', 'assigned', 'on_break']
        self.status_menu = ttk.OptionMenu(
            status_frame, 
            self.status_var, 
            user.status, 
            *status_options,
            command=self.update_status
        )
        self.status_menu.pack(side='left', padx=10)
        
        # Packages Frame
        packages_frame = tk.Frame(self, bg=self.styles.bg_color)
        packages_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Treeview for packages
        columns = ('id', 'tracking', 'sender', 'receiver', 'status', 'pickup', 'delivery')
        self.packages_tree = ttk.Treeview(
            packages_frame, 
            columns=columns, 
            show='headings',
            selectmode='browse'
        )
        
        # Define headings
        self.packages_tree.heading('id', text='ID')
        self.packages_tree.heading('tracking', text='Tracking #')
        self.packages_tree.heading('sender', text='Sender')
        self.packages_tree.heading('receiver', text='Receiver')
        self.packages_tree.heading('status', text='Status')
        self.packages_tree.heading('pickup', text='Pickup Address')
        self.packages_tree.heading('delivery', text='Delivery Address')
        
        # Set column widths
        self.packages_tree.column('id', width=50)
        self.packages_tree.column('tracking', width=120)
        self.packages_tree.column('sender', width=150)
        self.packages_tree.column('receiver', width=150)
        self.packages_tree.column('status', width=100)
        self.packages_tree.column('pickup', width=200)
        self.packages_tree.column('delivery', width=200)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(packages_frame, orient='vertical', command=self.packages_tree.yview)
        self.packages_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.packages_tree.pack(fill='both', expand=True)
        
        # Action Buttons
        btn_frame = tk.Frame(self, bg=self.styles.bg_color)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        self.update_btn = ttk.Button(
            btn_frame, 
            text="Update Status", 
            command=self.update_package_status,
            style='TButton'
        )
        self.update_btn.pack(side='left', padx=5)
        
        self.view_btn = ttk.Button(
            btn_frame, 
            text="View Details", 
            command=self.view_package_details,
            style='TButton'
        )
        self.view_btn.pack(side='left', padx=5)
    
    def load_packages(self):
        user = self.auth.get_current_user()
        packages = self.courier_ctrl.get_courier_packages(user.courier_id)
        
        # Clear existing data
        for item in self.packages_tree.get_children():
            self.packages_tree.delete(item)
        
        # Insert new data
        for pkg in packages:
            self.packages_tree.insert('', 'end', values=(
                pkg['id'],
                pkg['tracking_number'],
                pkg['sender_name'],
                pkg['receiver_name'],
                pkg['status'],
                pkg['pickup_address'],
                pkg['delivery_address']
            ))
    
    def update_status(self, *args):
        new_status = self.status_var.get()
        user = self.auth.get_current_user()
        
        conn = self.auth.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE couriers SET status=? WHERE id=?",
                (new_status, user.courier_id)
            )
            conn.commit()
            user.status = new_status
            messagebox.showinfo("Success", "Status updated successfully")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", str(e))
    
    def update_package_status(self):
        selected = self.packages_tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a package first")
            return
        
        package_data = self.packages_tree.item(selected, 'values')
        package_id = package_data[0]
        
        dialog = tk.Toplevel(self)
        dialog.title("Update Package Status")
        dialog.geometry("300x200")
        
        tk.Label(dialog, text="Select New Status:").pack(pady=10)
        
        status_var = tk.StringVar(value=package_data[4])
        status_options = ['pending', 'assigned', 'in_transit', 'out_for_delivery', 'delivered', 'failed']
        ttk.OptionMenu(dialog, status_var, package_data[4], *status_options).pack(pady=5)
        
        tk.Label(dialog, text="Location:").pack()
        location_entry = ttk.Entry(dialog)
        location_entry.pack(pady=5)
        
        tk.Label(dialog, text="Notes:").pack()
        notes_entry = ttk.Entry(dialog)
        notes_entry.pack(pady=5)
        
        def update_status():
            status = status_var.get()
            location = location_entry.get()
            notes = notes_entry.get()
            
            success, message = self.courier_ctrl.update_package_status(
                package_id, status, location, notes
            )
            
            if success:
                messagebox.showinfo("Success", message)
                self.load_packages()
                dialog.destroy()
            else:
                messagebox.showerror("Error", message)
        
        ttk.Button(dialog, text="Update", command=update_status).pack(pady=10)
    
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
        
        tk.Label(info_frame, text="Sender:", font='bold').grid(row=1, column=0, sticky='e')
        tk.Label(info_frame, text=package_data[2]).grid(row=1, column=1, sticky='w')
        
        tk.Label(info_frame, text="Receiver:", font='bold').grid(row=2, column=0, sticky='e')
        tk.Label(info_frame, text=package_data[3]).grid(row=2, column=1, sticky='w')
        
        tk.Label(info_frame, text="Status:", font='bold').grid(row=3, column=0, sticky='e')
        tk.Label(info_frame, text=package.status).grid(row=3, column=1, sticky='w')
        
        tk.Label(info_frame, text="Pickup Address:", font='bold').grid(row=4, column=0, sticky='e')
        tk.Label(info_frame, text=package.pickup_address, wraplength=300).grid(row=4, column=1, sticky='w')
        
        tk.Label(info_frame, text="Delivery Address:", font='bold').grid(row=5, column=0, sticky='e')
        tk.Label(info_frame, text=package.delivery_address, wraplength=300).grid(row=5, column=1, sticky='w')
        
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
    
    def logout(self):
        self.auth.logout()
        self.controller.show_frame(LoginView)