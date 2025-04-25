import tkinter as tk
from tkinter import ttk
from courier_controller import CourierController
from styles import Styles

class TrackingView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.courier_ctrl = CourierController()
        self.styles = Styles()
        
        self.configure(bg=self.styles.bg_color)
        self.create_widgets()
    
    def create_widgets(self):
        # Header
        header = tk.Label(
            self, 
            text="Package Tracking", 
            font=self.styles.header_font,
            bg=self.styles.bg_color,
            fg=self.styles.header_fg
        )
        header.pack(pady=20)
        
        # Tracking Form
        track_frame = tk.Frame(self, bg=self.styles.bg_color)
        track_frame.pack(pady=10)
        
        tk.Label(
            track_frame, 
            text="Enter Tracking Number:", 
            bg=self.styles.bg_color,
            font=self.styles.label_font
        ).grid(row=0, column=0, padx=5, pady=5)
        
        self.tracking_entry = ttk.Entry(track_frame, font=self.styles.entry_font)
        self.tracking_entry.grid(row=0, column=1, padx=5, pady=5)
        
        track_btn = ttk.Button(
            track_frame, 
            text="Track", 
            command=self.track_package,
            style='TButton'
        )
        track_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Results Frame
        self.results_frame = tk.Frame(self, bg=self.styles.bg_color)
        self.results_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    def track_package(self):
        tracking_number = self.tracking_entry.get()
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        if not tracking_number:
            tk.Label(
                self.results_frame,
                text="Please enter a tracking number.",
                bg=self.styles.bg_color,
                fg="red",
                font=self.styles.label_font
            ).pack()
            return

        tracking_info = self.courier_ctrl.get_tracking_details(tracking_number)

        if tracking_info:
            tk.Label(
                self.results_frame,
                text=f"Status: {tracking_info['status']}",
                bg=self.styles.bg_color,
                font=self.styles.label_font
            ).pack(anchor='w')

            tk.Label(
                self.results_frame,
                text=f"Estimated Delivery: {tracking_info['estimated_delivery']}",
                bg=self.styles.bg_color,
                font=self.styles.label_font
            ).pack(anchor='w')

            tk.Label(
                self.results_frame,
                text=f"Current Location: {tracking_info['current_location']}",
                bg=self.styles.bg_color,
                font=self.styles.label_font
            ).pack(anchor='w')
        else:
            tk.Label(
                self.results_frame,
                text="No tracking information found for this number.",
                bg=self.styles.bg_color,
                fg="red",
                font=self.styles.label_font
            ).pack()
