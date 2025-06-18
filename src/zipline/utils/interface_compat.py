"""
Compatibility layer for python-interface package.

This module provides a drop-in replacement for python-interface that works
with Python 3.13 and later versions.
"""

import sys
from typing import Any, Callable, TypeVar, Type
import functools
import warnings

__all__ = ["Interface", "implements", "default"]

T = TypeVar("T")


class DefaultProperty(property):
    """A property that can be marked as a default implementation."""

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        super().__init__(fget, fset, fdel, doc)
        self._is_default_implementation = True


class Interface:
    """
    Base class for defining interfaces.

    This is a compatibility replacement for python-interface.Interface
    that works with Python 3.13+.
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Mark this as an interface
        cls._is_interface = True
        # Store interface methods for validation
        cls._interface_methods = set()
        cls._signatures = set()  # For compatibility with original python-interface
        for name, method in cls.__dict__.items():
            if callable(method) and not name.startswith("_"):
                cls._interface_methods.add(name)
                cls._signatures.add(name)


def implements(*interfaces: Type[Interface]):
    """
    Decorator to declare that a class implements one or more interfaces.

    This is a compatibility replacement for python-interface.implements
    that works with Python 3.13+.

    Can be used as a decorator or as a class factory (for backward compatibility).

    Parameters
    ----------
    *interfaces : Type[Interface]
        Interface classes that the decorated class implements.

    Returns
    -------
    Callable[[Type[T]], Type[T]] or Type
        Class decorator function or a new class that implements the interface.
    """
    # Handle the special case where implements is called with a single interface
    # to create a class (like Domain = implements(IDomain))
    if (
        len(interfaces) == 1
        and isinstance(interfaces[0], type)
        and issubclass(interfaces[0], Interface)
    ):
        interface = interfaces[0]

        # Create a new class that implements the interface
        class ImplementationClass:
            """Auto-generated class that implements the interface."""

            pass

        # Copy all default methods from the interface
        for name, method in interface.__dict__.items():
            if hasattr(method, "_is_default_implementation"):
                setattr(ImplementationClass, name, method)

        # Mark this class as implementing the interface
        ImplementationClass._implements = {interface}

        return ImplementationClass

    # Normal decorator usage
    def decorator(cls: Type[T]) -> Type[T]:
        # Store which interfaces this class implements
        if not hasattr(cls, "_implements"):
            cls._implements = set()
        cls._implements.update(interfaces)
        return cls

    return decorator


def default(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to mark a method as a default implementation in an interface.

    This is a compatibility replacement for python-interface.default
    that works with Python 3.13+.

    Parameters
    ----------
    func : Callable[..., Any]
        The method to mark as a default implementation.

    Returns
    -------
    Callable[..., Any]
        The decorated method with default implementation marker.
    """
    # Handle properties and other descriptors
    if isinstance(func, property):
        # Create a new DefaultProperty with the same getter/setter/deleter
        return DefaultProperty(func.fget, func.fset, func.fdel, func.__doc__)
    else:
        # Handle regular functions and methods
        func._is_default_implementation = True
        return func


# For Python 3.13+ compatibility, we may need to handle inspect module changes
if sys.version_info >= (3, 13):
    import inspect

    # Monkey patch any problematic inspect functionality if needed
    # This would be where we'd add specific fixes for Python 3.13 inspect changes
    pass
