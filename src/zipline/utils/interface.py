"""
Interface compatibility module for zipline.

This module provides a unified interface for working with python-interface
across different Python versions, with fallback compatibility for Python 3.13+.
"""

import sys
import warnings

try:
    # Try to import the original python-interface package
    from interface import Interface, implements, default

    # Test if it works with current Python version
    # Create a simple test to see if the package works
    class _TestInterface(Interface):
        def test_method(self):
            pass

    @implements(_TestInterface)
    class _TestImplementation:
        def test_method(self):
            return "test"

    # Try to instantiate to test if it works
    _test_instance = _TestImplementation()

    # If we get here, python-interface is working
    _using_original = True

except (ImportError, TypeError, AttributeError) as e:
    # python-interface is not available or not working
    # Fall back to our compatibility layer
    if sys.version_info >= (3, 13):
        # Expected for Python 3.13+
        pass
    else:
        # Unexpected for older Python versions
        warnings.warn(
            f"python-interface package is not available or not compatible with "
            f"Python {sys.version_info.major}.{sys.version_info.minor}. "
            f"Using compatibility layer. Original error: {e}",
            UserWarning,
            stacklevel=2,
        )

    from zipline.utils.interface_compat import Interface, implements, default

    _using_original = False

# Export the symbols
__all__ = ["Interface", "implements", "default", "is_using_original_interface"]


def is_using_original_interface() -> bool:
    """
    Return True if using the original python-interface package,
    False if using the compatibility layer.

    Returns
    -------
    bool
        True if using original python-interface, False if using compatibility layer.
    """
    return _using_original
