import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar  # Ensure you have installed tkcalendar using 'pip install tkcalendar'

def add_button(self, text, command, row=None, column=None, rowspan=1, columnspan=1, style=None, frame=None):
    frame = frame or self.root
    button = ttk.Button(frame, text=text, command=command, style='TButton')
    if style:
        button.config(**style)
    self.widgets['button'] = self._add_widget(button, row, column, rowspan, columnspan)
    return button

def add_label(self, text, row=None, column=None, rowspan=1, columnspan=1, style=None, frame=None):
    frame = frame or self.root
    label = ttk.Label(frame, text=text, style='TLabel')
    if style:
        label.config(**style)
    self.widgets['label'] = self._add_widget(label, row, column, rowspan, columnspan)
    return label

def add_textbox(self, default_text="", width=20, row=None, column=None, rowspan=1, columnspan=1, style=None, frame=None):
    frame = frame or self.root
    textbox = ttk.Entry(frame, width=width, style='TEntry')
    textbox.insert(0, default_text)
    if style:
        textbox.config(**style)
    self.widgets['textbox'] = self._add_widget(textbox, row, column, rowspan, columnspan)
    return textbox

def add_checkbox(self, text, variable, row=None, column=None, style=None, frame=None):
    frame = frame or self.root
    checkbox = ttk.Checkbutton(frame, text=text, variable=variable.var, style='TCheckbutton')
    if style:
        checkbox.config(**style)
    self.widgets['checkbox'] = self._add_widget(checkbox, row, column)
    return checkbox

def add_radiobutton(self, text, value, variable, row=None, column=None, style=None, frame=None):
    frame = frame or self.root
    radiobutton = ttk.Radiobutton(frame, text=text, value=value, variable=variable.var, style='TRadiobutton')
    if style:
        radiobutton.config(**style)
    self.widgets['radiobutton'] = self._add_widget(radiobutton, row, column)
    return radiobutton

def add_combobox(self, values, row=None, column=None, style=None, frame=None):
    frame = frame or self.root
    combobox = ttk.Combobox(frame, values=values, style='TCombobox')
    if style:
        combobox.config(**style)
    self.widgets['combobox'] = self._add_widget(combobox, row, column)
    return combobox

def add_progressbar(self, maximum=100, value=0, row=None, column=None, columnspan=1, style=None, frame=None):
    frame = frame or self.root
    progressbar = ttk.Progressbar(frame, maximum=maximum, value=value, style='TProgressbar')
    if style:
        progressbar.config(**style)
    self.widgets['progressbar'] = self._add_widget(progressbar, row, column, columnspan=columnspan)
    return progressbar

def add_slider(self, from_=0, to=100, orient=tk.HORIZONTAL, value=0, row=None, column=None, columnspan=1, style=None, frame=None):
    frame = frame or self.root
    slider = tk.Scale(frame, from_=from_, to=to, orient=orient, length=200, sliderlength=30)
    slider.set(value)
    if style:
        slider.config(**style)
    self.widgets['slider'] = self._add_widget(slider, row, column, columnspan=columnspan)
    return slider

def add_notebook(self, tabs, row=None, column=None, rowspan=1, columnspan=1, style=None):
    notebook = ttk.Notebook(self.root, style='TNotebook')
    if style:
        notebook.config(**style)
    for tab_name, content in tabs.items():
        frame = tk.Frame(notebook)
        content(self, frame)
        notebook.add(frame, text=tab_name)
    self.widgets['notebook'] = self._add_widget(notebook, row, column, rowspan, columnspan)
    return notebook

def add_label_frame(self, text, row=None, column=None, rowspan=1, columnspan=1, style=None):
    frame = ttk.LabelFrame(self.root, text=text, style='TLabelFrame')
    if style:
        frame.config(**style)
    self.widgets['label_frame'] = self._add_widget(frame, row, column, rowspan, columnspan)
    return frame

def add_spinbox(self, from_, to, increment=1, row=None, column=None, style=None, frame=None):
    frame = frame or self.root
    spinbox = ttk.Spinbox(frame, from_=from_, to=to, increment=increment, style='TSpinbox')
    if style:
        spinbox.config(**style)
    self.widgets['spinbox'] = self._add_widget(spinbox, row, column)
    return spinbox

def add_canvas(self, width, height, row=None, column=None, columnspan=1):
    canvas = tk.Canvas(self.root, width=width, height=height)
    self.widgets['canvas'] = self._add_widget(canvas, row, column, columnspan=columnspan)
    return canvas

def add_calendar(self, row=None, column=None):
    frame = tk.Frame(self.root)
    frame.grid(row=row if row is not None else self.current_row,
               column=column if column is not None else self.current_column,
               **self.grid_config)
    
    calendar = Calendar(frame, selectmode='day')
    calendar.pack(padx=10, pady=10, expand=True, fill='both')
    
    self.widgets['calendar'] = calendar
    return calendar

def add_treeview(self, columns, row=None, column=None, columnspan=1, style=None, frame=None):
        """Add a treeview to the window."""
        frame = frame or self.root
        treeview = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns:
            treeview.heading(col, text=col)
        if style:
            treeview.config(style=style)
        self.widgets['treeview'] = self._add_widget(treeview, row, column, columnspan=columnspan)
        return treeview


def add_tooltip(self, widget_name, text):
    widget = self.widgets.get(widget_name)
    if widget:
        tooltip = tk.Label(widget, text=text, background="yellow")
        widget.bind("<Enter>", lambda e: tooltip.place(relx=0.5, rely=1.1, anchor="center"))
        widget.bind("<Leave>", lambda e: tooltip.place_forget())

def add_context_menu(self, widget_name, menu_items):
    widget = self.widgets.get(widget_name)
    if widget:
        menu = tk.Menu(widget, tearoff=0)
        for item_name, command in menu_items.items():
            menu.add_command(label=item_name, command=command)
        widget.bind("<Button-3>", lambda e: menu.tk_popup(e.x_root, e.y_root))

def add_text(self, text, row=None, column=None, columnspan=1, style=None):
    text_widget = tk.Label(self.root, text=text)
    if style:
        text_widget.config(**style)
    self.widgets['text'] = self._add_widget(text_widget, row, column, columnspan=columnspan)
    return text_widget

def add_listbox(self, items, row=None, column=None, columnspan=1, style=None, frame=None):
    frame = frame or self.root
    listbox = tk.Listbox(frame)
    for item in items:
        listbox.insert(tk.END, item)
    if style:
        listbox.config(**style)
    self.widgets['listbox'] = self._add_widget(listbox, row, column, columnspan=columnspan)
    return listbox

def add_scrollbar(self, widget_name, orient=tk.VERTICAL, row=None, column=None, rowspan=1, columnspan=1, frame=None):
        """Add a scrollbar to a widget."""
        frame = frame or self.root
        scrollbar = ttk.Scrollbar(frame, orient=orient)
        widget = self.widgets.get(widget_name)
        if widget:
            widget.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=widget.yview)
        self.widgets['scrollbar'] = self._add_widget(scrollbar, row, column, rowspan=rowspan, columnspan=columnspan)
        return scrollbar

def add_message(self, text, row=None, column=None, columnspan=1, style=None):
    message = tk.Message(self.root, text=text)
    if style:
        message.config(**style)
    self.widgets['message'] = self._add_widget(message, row, column, columnspan=columnspan)
    return message

def add_paned_window(self, orient=tk.HORIZONTAL, row=None, column=None, rowspan=1, columnspan=1):
        """Add a paned window to the window."""
        paned_window = ttk.PanedWindow(self.root, orient=orient)
        self.widgets['paned_window'] = self._add_widget(paned_window, row, column, rowspan=rowspan, columnspan=columnspan)
        return paned_window
def add_separator(self, orient=tk.HORIZONTAL, row=None, column=None, columnspan=1):
    separator = ttk.Separator(self.root, orient=orient)
    self.widgets['separator'] = self._add_widget(separator, row, column, columnspan=columnspan)
    return separator
def add_widget(self, widget, row=None, column=None, rowspan=1, columnspan=1):
    """Helper function to add a widget to the window with grid layout."""
    widget.grid(row=row if row is not None else self.current_row,
                column=column if column is not None else self.current_column,
                rowspan=rowspan,
                columnspan=columnspan,
                **self.grid_config)
    # Update the current row/column positions for next widget if row/column is not specified
    if row is None:
        self.current_row += 1
    if column is None:
        self.current_column += 1
    return widget
