import tkinter as tk
from tkinter import ttk
from database import Database
from styles import Styles
from views.customer_view import CustomerDashboard
from views.auth_view import LoginView

class CourierApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Initialize database
        db = Database()
        db.initialize_database()
        
        # Window configuration
        self.title("Courier Tracking System")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # Apply styles
        self.styles = Styles()
        self.style = ttk.Style()
        self.style.configure('TButton', font=self.styles.button_font)
        
        # Container frame
        container = tk.Frame(self)
        container.pack(fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        
        # Create all frames
        from views.auth_view import LoginView, RegisterView
        from views.admin_view import AdminDashboard
        from views.courier_view import CourierDashboard
        from views.customer_view import CustomerDashboard
        
        frame = LoginView(container, self, CustomerDashboard)
        for F in (LoginView, RegisterView, AdminDashboard, CourierDashboard, CustomerDashboard):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        
        # Show login frame first
        self.show_frame(LoginView)
    
    def show_frame(self, cont):
        """Show a frame for the given class"""
        frame = self.frames[cont]
        frame.tkraise()

if __name__ == "__main__":
    app = CourierApp()
    app.mainloop()