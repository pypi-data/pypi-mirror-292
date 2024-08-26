from .module.core import SimpleWindow
from .module.widgets import *
from .module.dialogs import *
from .module.utils import *

class SimpleWindow(SimpleWindow):
    """Main SimpleWindow class that integrates core, widgets, dialogs, and utils."""

    def __init__(self, title="TkEasyGo Window", width=300, height=200):
        super().__init__(title, width, height)

    # 绑定方法
    add_button = add_button
    add_label = add_label
    add_textbox = add_textbox
    add_checkbox = add_checkbox
    add_radiobutton = add_radiobutton
    add_combobox = add_combobox
    add_progressbar = add_progressbar
    add_slider = add_slider
    add_notebook = add_notebook
    add_label_frame = add_label_frame
    add_spinbox = add_spinbox
    add_canvas = add_canvas
    add_calendar = add_calendar
    add_treeview = add_treeview
    add_tooltip = add_tooltip
    add_context_menu = add_context_menu
    add_text = add_text
    add_listbox = add_listbox
    add_scrollbar = add_scrollbar
    add_message = add_message
    add_paned_window = add_paned_window
    add_separator = add_separator
    _add_widget=add_widget
    open_file_dialog = open_file_dialog
    open_color_dialog = open_color_dialog
    show_messagebox = show_messagebox
    bind_event = bind_event
    bind_events = bind_events
    disable_widget = disable_widget
    enable_widget = enable_widget
    remove_widget = remove_widget
    

    # 添加更多方法...


