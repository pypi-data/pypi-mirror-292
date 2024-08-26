# TkEasyGo/utils.py

def bind_event(self, widget_name, event_name, handler):
    widget = self.widgets.get(widget_name)
    if widget:
        widget.bind(event_name, handler)

def bind_events(self, widget_name, events):
    widget = self.widgets.get(widget_name)
    if widget:
        for event_name, handler in events.items():
            widget.bind(event_name, handler)

def disable_widget(self, widget_name):
    widget = self.widgets.get(widget_name)
    if widget:
        widget.state(["disabled"])

def enable_widget(self, widget_name):
    widget = self.widgets.get(widget_name)
    if widget:
        widget.state(["!disabled"])

def remove_widget(self, widget_name):
    widget = self.widgets.pop(widget_name, None)
    if widget:
        widget.grid_forget()
        widget.destroy()
