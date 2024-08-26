class GridLayout:
    """Class to handle grid layout configuration."""

    def __init__(self, parent):
        self.parent = parent
        self.grid_config = {'padx': 10, 'pady': 10, 'sticky': "ew"}

    def set_grid_config(self, **options):
        """Set the default grid configuration."""
        self.grid_config.update(options)

    def add_widget(self, widget, row, column, rowspan=1, columnspan=1):
        """Add a widget to the grid with the current configuration."""
        widget.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, **self.grid_config)