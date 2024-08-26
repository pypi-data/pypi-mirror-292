import tkinter as tk

class SimpleVariable:
    """
    A simple wrapper around Tkinter's StringVar with additional utility methods for easier use.

    This class simplifies the use of Tkinter's StringVar, adding utility methods that make it more
    convenient to work with variable tracing, and other data types such as integers, floats, or booleans.
    
    Attributes:
        var (tk.StringVar): The underlying Tkinter StringVar instance.
    """

    def __init__(self, initial_value=None):
        """
        Initialize the SimpleVariable instance.

        Args:
            initial_value (str, optional): The initial value for the StringVar. If not provided, defaults to None.
        """
        self.var = tk.StringVar(value=initial_value)

    def get(self):
        """
        Get the current value of the variable.

        Returns:
            str: The current value stored in the StringVar.
        """
        return self.var.get()

    def set(self, value):
        """
        Set the value of the variable.

        Args:
            value (str): The value to set in the StringVar.
        """
        self.var.set(value)

    def trace(self, callback):
        """
        Attach a callback to be triggered whenever the variable's value changes.

        The callback will be passed the new value of the variable as its argument.

        Args:
            callback (function): The function to call when the variable changes.
        """
        self.var.trace_add("write", lambda *args: callback(self.var.get()))

    def bind_to_widget(self, widget, attribute="text"):
        """
        Bind the variable to a widget's attribute (e.g., text, value) for automatic updates.

        Args:
            widget (tk.Widget): The widget to bind the variable to.
            attribute (str): The widget attribute to bind to (default is "text").
        """
        if hasattr(widget, attribute):
            widget.config(textvariable=self.var)
        else:
            raise AttributeError(f"The widget does not have the attribute '{attribute}'.")

    def get_as_int(self):
        """
        Get the variable's value as an integer.

        Returns:
            int: The integer value of the variable.
        """
        try:
            return int(self.get())
        except ValueError:
            raise ValueError("The current value cannot be converted to an integer.")

    def get_as_float(self):
        """
        Get the variable's value as a float.

        Returns:
            float: The float value of the variable.
        """
        try:
            return float(self.get())
        except ValueError:
            raise ValueError("The current value cannot be converted to a float.")

    def get_as_bool(self):
        """
        Get the variable's value as a boolean.

        The conversion follows standard Python truthiness rules.

        Returns:
            bool: The boolean value of the variable.
        """
        return bool(self.get())

    def increment(self, step=1):
        """
        Increment the variable's value by a given step.

        This method assumes the current value is an integer.

        Args:
            step (int): The amount to increment by (default is 1).

        Raises:
            ValueError: If the current value cannot be converted to an integer.
        """
        try:
            current_value = self.get_as_int()
            self.set(str(current_value + step))
        except ValueError:
            raise ValueError("The current value is not an integer and cannot be incremented.")

    def decrement(self, step=1):
        """
        Decrement the variable's value by a given step.

        This method assumes the current value is an integer.

        Args:
            step (int): The amount to decrement by (default is 1).

        Raises:
            ValueError: If the current value cannot be converted to an integer.
        """
        self.increment(-step)

    def reset(self, value=None):
        """
        Reset the variable to a specified value, or to its initial value if none is provided.

        Args:
            value (str, optional): The value to reset to. If not provided, the initial value will be used.
        """
        self.set(value)

    def clear(self):
        """
        Clear the value of the variable, setting it to an empty string.
        """
        self.set("")
