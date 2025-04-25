# styles.py

import tkinter.font as tkfont

class Styles:
    def __init__(self):
        # Colors
        self.bg_color = "#F5F5F5"       # Light gray background
        self.header_fg = "#2E86C1"      # Blue header text
        self.label_fg = "#333333"       # Dark text
        self.entry_bg = "#FFFFFF"       # White entry field

        # Fonts
        self.header_font = ("Helvetica", 20, "bold")
        self.label_font = ("Helvetica", 12)
        self.entry_font = ("Helvetica", 12)
        self.button_font = ("Helvetica", 11, "bold")

    def apply_ttk_theme(self, style):
        """Applies custom styles to ttk widgets."""
        style.theme_use('default')
        
        style.configure('TButton',
                        font=self.button_font,
                        background="#2E86C1",
                        foreground="#FFFFFF",
                        padding=6)
        
        style.map('TButton',
                  background=[('active', '#1B4F72')])

        style.configure('TLabel',
                        background=self.bg_color,
                        font=self.label_font)

        style.configure('TEntry',
                        font=self.entry_font,
                        fieldbackground=self.entry_bg)

