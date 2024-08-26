"""
core.py

This module serves as the main entry point for the TkEasyGo package.
It provides access to the core classes and functions.

Classes:
- SimpleVariable: A simple wrapper around Tkinter's StringVar with additional utility methods.
- SimpleWindow: A simple GUI window using Tkinter and ttkbootstrap with various helper methods.
"""

from .simple_variable import SimpleVariable
from .simple_window import SimpleWindow
from .builder import GUIBuilder

__all__ = [
    'SimpleVariable',
    'SimpleWindow',
    'GUIBuilder'
]
