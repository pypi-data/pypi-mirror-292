
class ThemeManager:
    """Class to manage and apply themes."""

    def __init__(self, style):
        self.style = style

    def apply_theme(self, theme_name):
        """Apply a theme based on the given theme name."""
        if theme_name == 'dark':
            self.style.configure('TButton', background='black', foreground='white')
            self.style.configure('TLabel', background='black', foreground='white')
        elif theme_name == 'light':
            self.style.configure('TButton', background='white', foreground='black')
            self.style.configure('TLabel', background='white', foreground='black')
        else:
            raise ValueError(f"Unknown theme: {theme_name}")
