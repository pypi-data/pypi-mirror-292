# TkEasyGo/dialogs.py

from tkinter import filedialog, colorchooser, messagebox

def open_file_dialog(self, filetypes=(("All files", "*.*"),)):
    return filedialog.askopenfilename(filetypes=filetypes)

def open_color_dialog(self):
    return colorchooser.askcolor()[1]

def show_messagebox(self, title, message):
    messagebox.showinfo(title, message)
