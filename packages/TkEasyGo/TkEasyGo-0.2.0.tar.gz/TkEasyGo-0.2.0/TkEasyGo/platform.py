import platform
class PlatformUtils:
    """Utility class for platform-specific operations."""

    @staticmethod
    def is_windows():
        """Check if the platform is Windows."""
        return platform.system() == "Windows"

    @staticmethod
    def is_mac():
        """Check if the platform is macOS."""
        return platform.system() == "Darwin"

    @staticmethod
    def is_linux():
        """Check if the platform is Linux."""
        return platform.system() == "Linux"

    @staticmethod
    def adjust_for_platform(widget):
        """Adjust widget properties based on the platform."""
        if PlatformUtils.is_windows():
            widget.configure(bg='lightblue')
        elif PlatformUtils.is_mac():
            widget.configure(bg='lightgreen')
        elif PlatformUtils.is_linux():
            widget.configure(bg='lightyellow')