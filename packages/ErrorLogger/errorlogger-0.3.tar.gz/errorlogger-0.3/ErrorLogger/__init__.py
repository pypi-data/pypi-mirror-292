# Import the main components of the ErrorLogger library
from .logger import ErrorLogger, capture_exception

# Specify what should be available when someone imports the package
__all__ = ['ErrorLogger', 'capture_exception']
