# TkEasyGo/core.py

import tkinter as tk
import ttkbootstrap as tb

class SimpleWindow:
    """A simple GUI window using Tkinter and ttkbootstrap with various helper methods."""
  
    def __init__(self, title="TkEasyGo Window", width=300, height=200):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.style = tb.Style()  # Use ttkbootstrap's style
        self.configure_styles()
        self.widgets = {}
        self.current_row = 0
        self.current_column = 0
        self.frames = {}
        self.maximized = False
        self.grid_config = {'padx': 10, 'pady': 10, 'sticky': "ew"}  # Default grid configuration

    def configure_styles(self):
        """Configure the styles for various ttkbootstrap widgets."""
        self.style.configure('TButton', padding=6, relief="flat", background="#4CAF50", font=("Arial", 12))
        self.style.configure('TLabel', background="#f4f4f4", font=("Arial", 12))
        # 其他样式配置...

    def update_style(self, style_name, options):
        """Update the style configuration for a given widget style."""
        self.style.configure(style_name, **options)

    def set_grid_config(self, **options):
        """Set the default grid configuration for all widgets."""
        self.grid_config.update(options)

    def run(self):
        """Run the Tkinter main loop."""
        self.root.mainloop()

    def maximize(self):
        """Maximize the window."""
        self.root.attributes("-fullscreen", True)
        self.maximized = True

    def minimize(self):
        """Minimize the window."""
        self.root.iconify()

    def restore(self):
        """Restore the window to its normal size."""
        self.root.attributes("-fullscreen", False)
        self.maximized = False

    def log(self, message):
        """Log a message (simple print for now, could be expanded)."""
        print(f"[LOG]: {message}")
