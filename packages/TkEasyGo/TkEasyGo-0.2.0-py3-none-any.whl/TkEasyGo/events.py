class EventHandler:
    """Class to handle various events in the GUI."""

    def __init__(self, widget):
        self.widget = widget

    def bind_event(self, event_name, handler):
        """Bind a single event to the widget."""
        self.widget.bind(event_name, handler)

    def bind_multiple(self, events):
        """Bind multiple events to the widget."""
        for event_name, handler in events.items():
            self.bind_event(event_name, handler)
