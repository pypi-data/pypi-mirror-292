import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import StringVar
class GUIBuilder:
    def __init__(self, root):
        self.root = root
        self.root.title("GUI Builder")
        
        # Frames for controls, editor, and control list
        self.controls_frame = ttk.Frame(root)
        self.controls_frame.pack(side="left", fill="y")
        
        self.editor_frame = ttk.Frame(root)
        self.editor_frame.pack(side="left", fill="both", expand=True)
        
        self.property_frame = ttk.Frame(root)
        self.property_frame.pack(side="right", fill="y")
        
        # Create Controls, Editor, and Property Editor
        self.create_controls()
        self.create_editor()
        self.create_property_editor()

        # List to store controls and their details
        self.controls = []
        self.current_control = None
        self.highlight = None

    def create_controls(self):
        self.control_types = {
            "Button": tk.Button,
            "Label": tk.Label,
            "Entry": tk.Entry,
            "Checkbutton": tk.Checkbutton,
            "Radiobutton": tk.Radiobutton,
            "Listbox": tk.Listbox,
            "Combobox": ttk.Combobox,
            "Spinbox": tk.Spinbox,
            "Text": tk.Text,
            "Scale": tk.Scale,
            "Scrollbar": tk.Scrollbar,
            "Progressbar": ttk.Progressbar,
        }
        
        # Control type listbox
        self.control_list = tk.Listbox(self.controls_frame)
        for control in self.control_types:
            self.control_list.insert(tk.END, control)
        self.control_list.pack(padx=10, pady=10)
        self.control_list.bind("<Double-1>", self.add_control)
    
    def create_editor(self):
        self.canvas = tk.Canvas(self.editor_frame, bg="white")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.move_control)
        self.canvas.bind("<ButtonRelease-1>", self.release_control)
    
    def create_property_editor(self):
        self.property_label = ttk.Label(self.property_frame, text="Control Properties")
        self.property_label.pack(padx=10, pady=10)
        
        # 使用一个容器框架来存放属性小部件
        self.property_container = ttk.Frame(self.property_frame)
        self.property_container.pack(fill="both", expand=True)
        
        self.property_widgets = {}

    def clear_property_editor(self):
        if self.property_container:
            self.property_container.destroy()
        self.property_container = ttk.Frame(self.property_frame)
        self.property_container.pack(fill="both", expand=True)
        self.property_widgets.clear()

    def load_properties(self):
        if self.current_control:
            self.clear_property_editor()
            control = self.current_control['control']
            properties = {}

            if isinstance(control, (tk.Button, tk.Label, tk.Checkbutton, tk.Radiobutton)):
                properties["text"] = {"label": "Text:", "value": control.cget('text')}
            if isinstance(control, (tk.Widget,)):
                properties["bg"] = {"label": "Background:", "value": control.cget('bg') if 'bg' in control.keys() else ''}
            if isinstance(control, (tk.Entry, tk.Listbox, tk.Text)):
                properties["width"] = {"label": "Width:", "value": control.cget('width') if 'width' in control.keys() else ''}
            if isinstance(control, (tk.Text, tk.Listbox, tk.Entry)):
                properties["height"] = {"label": "Height:", "value": control.cget('height') if 'height' in control.keys() else ''}
            if isinstance(control, (tk.Entry, tk.Text, tk.Label, tk.Button)):
                properties["font"] = {"label": "Font:", "value": control.cget('font') if 'font' in control.keys() else ''}
                
            for key, prop in properties.items():
                label = ttk.Label(self.property_container, text=prop["label"])
                label.pack(anchor="w", padx=10)
                if key == "bg":
                    bg_var = StringVar()
                    bg_var.set(prop["value"])
                    combobox = ttk.Combobox(self.property_container, textvariable=bg_var)
                    combobox['values'] = ('white', 'black', 'red', 'green', 'blue', 'yellow', 'gray', 'cyan', 'magenta')
                    combobox.pack(padx=10, fill="x")
                    self.property_widgets[key] = bg_var
                elif key == "font":
                    font_var = StringVar()
                    font_var.set(prop["value"])
                    combobox = ttk.Combobox(self.property_container, textvariable=font_var)
                    combobox['values'] = ('Arial', 'Helvetica', 'Times New Roman', 'Courier', 'Comic Sans MS', 'Verdana', 'Impact')
                    combobox.pack(padx=10, fill="x")
                    self.property_widgets[key] = font_var
                else:
                    entry = ttk.Entry(self.property_container)
                    entry.insert(0, prop["value"])
                    entry.pack(padx=10, fill="x")
                    self.property_widgets[key] = entry

            self.update_button = ttk.Button(self.property_container, text="Update", command=self.update_properties)
            self.update_button.pack(pady=10)

        
    def update_properties(self):
        if self.current_control:
            control = self.current_control['control']
            
            if "text" in self.property_widgets:
                control.config(text=self.property_widgets["text"].get())
            if "bg" in self.property_widgets:
                control.config(bg=self.property_widgets["bg"].get())
            if "width" in self.property_widgets:
                control.config(width=self.property_widgets["width"].get())
            if "height" in self.property_widgets:
                control.config(height=self.property_widgets["height"].get())
            if "font" in self.property_widgets:
                control.config(font=self.property_widgets["font"].get())


    def add_control(self, event):
        selection = self.control_list.curselection()
        if not selection:
            return
        control_type = self.control_list.get(selection[0])
        if control_type:
            control_class = self.control_types[control_type]
            x, y = 10, 10
            
            # Only pass "text" if the control supports it
            if control_class in [tk.Button, tk.Label, tk.Checkbutton, tk.Radiobutton]:
                control = control_class(self.canvas, text=control_type)
            else:
                control = control_class(self.canvas)
                
            window = self.canvas.create_window(x, y, window=control, anchor="nw")
            name = self.get_unique_name(control_type.lower())
            self.controls.append({'name': name, 'type': control_type, 'window': window, 'control': control, 'position': (x, y)})
            self.add_control_to_list(name)
    
    def move_control(self, event):
        if not self.current_control:
            return
        x, y = event.x, event.y
        self.canvas.coords(self.current_control['window'], x, y)
        self.current_control['position'] = (x, y)
    
    def on_canvas_click(self, event):
        clicked_item = self.canvas.find_closest(event.x, event.y)
        if clicked_item:
            self.current_control = next((ctrl for ctrl in self.controls if ctrl['window'] == clicked_item[0]), None)
            if self.current_control:
                self.load_properties()
                self.highlight_control()
                self.highlight_control_in_list()

    def highlight_control(self):
        if self.highlight:
            self.canvas.delete(self.highlight)

        x0, y0, x1, y1 = self.canvas.bbox(self.current_control['window'])
        self.highlight = self.canvas.create_rectangle(x0 - 2, y0 - 2, x1 + 2, y1 + 2, outline="blue", width=2)

    def highlight_control_in_list(self):
        if self.current_control:
            index = self.added_controls_list.get(0, tk.END).index(self.current_control['name'])
            self.added_controls_list.selection_clear(0, tk.END)
            self.added_controls_list.selection_set(index)

    def release_control(self, event):
        self.current_control = None
    
    def get_unique_name(self, base_name):
        existing_names = [ctrl['name'] for ctrl in self.controls]
        counter = 1
        unique_name = f"{base_name}{counter}"
        while unique_name in existing_names:
            counter += 1
            unique_name = f"{base_name}{counter}"
        return unique_name

    def add_control_to_list(self, name):
        if not hasattr(self, 'added_controls_list'):
            self.added_controls_list = tk.Listbox(self.property_frame)
            self.added_controls_list.pack(padx=10, pady=10)
            self.added_controls_list.bind("<<ListboxSelect>>", self.on_control_select)

        self.added_controls_list.insert(tk.END, name)
    
    def refresh_control_list(self):
        self.added_controls_list.delete(0, tk.END)
        for ctrl in self.controls:
            self.added_controls_list.insert(tk.END, ctrl['name'])

    def on_control_select(self, event):
        selection = self.added_controls_list.curselection()
        if selection:
            selected_name = self.added_controls_list.get(selection[0])
            self.current_control = next(ctrl for ctrl in self.controls if ctrl['name'] == selected_name)
            self.load_properties()
            self.highlight_control()

    def delete_control(self):
        if self.current_control:
            self.canvas.delete(self.current_control['window'])
            self.controls.remove(self.current_control)
            self.refresh_control_list()
            self.clear_property_editor()
            self.current_control = None
            self.highlight = None

    def generate_code(self):
        code = "import tkinter as tk\n"
        code += "from tkinter import ttk\n\n"  # Import ttk for ttk controls
        code += "root = tk.Tk()\n\n"
        
        for control in self.controls:
            control_type = control['type']
            x, y = control['position']
            name = control['name']
            
            # 获取控件的属性值
            text = control['control'].cget('text') if 'text' in control['control'].keys() else ''
            bg = control['control'].cget('bg') if 'bg' in control['control'].keys() else ''
            width = control['control'].cget('width') if 'width' in control['control'].keys() else ''
            height = control['control'].cget('height') if 'height' in control['control'].keys() else ''
            font = control['control'].cget('font') if 'font' in control['control'].keys() else ''
            
            # 根据控件类型选择前缀
            if control_type in ["Combobox", "Progressbar"]:  # 使用ttk的控件
                prefix = "ttk."
            else:
                prefix = "tk."
            
            # 构建控件的创建行
            code_line = f"{name} = {prefix}{control_type}(root"
            
            if text:
                code_line += f", text='{text}'"
            if bg:
                code_line += f", bg='{bg}'"
            if width:
                code_line += f", width={width}"
            if height:
                code_line += f", height={height}"
            if font:
                code_line += f", font='{font}'"
            
            # 关闭括号并换行
            code_line += ")\n"
            
            # 添加控件的布局信息
            code_line += f"{name}.place(x={x}, y={y})\n"
            
            # 添加到代码中
            code += code_line + "\n"
        
        code += "root.mainloop()\n"
        return code



    def save_code(self):
        code = self.generate_code()
        with open("generated_code.py", "w") as f:
            f.write(code)
        messagebox.showinfo("Info", "Code saved as generated_code.py")

    def show_save_button(self):
        save_button = tk.Button(self.root, text="Save Code", command=self.save_code)
        save_button.pack(padx=10, pady=10)

    def run():
        root = tk.Tk()
        app = GUIBuilder(root)
        app.show_save_button()
        root.mainloop()
