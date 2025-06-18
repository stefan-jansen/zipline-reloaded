"""
Compatibility layer for python-interface package.

This module provides a drop-in replacement for python-interface that works
with Python 3.13 and later versions.
"""

import sys
from typing import Any, Callable, TypeVar, Type
import functools
import warnings
import threading
import weakref

__all__ = [
    "Interface",
    "implements",
    "default",
    "create_implementation",
    "implements_decorator",
]

T = TypeVar("T")

# Thread-local storage to prevent issues in multi-threaded environments
_local = threading.local()
# Global lock for thread-safe operations
_global_lock = threading.RLock()
# Cache for created base classes to avoid recreation
_base_class_cache = weakref.WeakValueDictionary()


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

        # Safely iterate over class dict to avoid issues during class creation
        try:
            for name, method in cls.__dict__.items():
                if callable(method) and not name.startswith("_"):
                    cls._interface_methods.add(name)
                    cls._signatures.add(name)
                elif isinstance(method, property) and not name.startswith("_"):
                    cls._interface_methods.add(name)
                    cls._signatures.add(name)
        except (RuntimeError, AttributeError):
            # Handle case where dict changes during iteration
            pass


def _copy_default_methods(target_class, interfaces):
    """
    Safely copy default methods from interfaces to target class.

    Parameters
    ----------
    target_class : type
        The class to copy methods to.
    interfaces : tuple
        The interfaces to copy methods from.
    """
    with _global_lock:
        for interface in interfaces:
            try:
                for name, method in interface.__dict__.items():
                    if hasattr(method, "_is_default_implementation") and not hasattr(
                        target_class, name
                    ):
                        try:
                            setattr(target_class, name, method)
                        except (AttributeError, TypeError):
                            # Some classes don't allow attribute assignment
                            pass
            except (AttributeError, RuntimeError):
                # Handle edge cases during class creation
                pass


def create_implementation(interface: Type[Interface]) -> Type:
    """
    Create a class that implements the given interface.

    This is used for the pattern: Domain = create_implementation(IDomain)

    Parameters
    ----------
    interface : Type[Interface]
        The interface to implement.

    Returns
    -------
    Type
        A new class that implements the interface.
    """

    class ImplementationClass:
        """Auto-generated class that implements the interface."""

        def __init__(self, *args, **kwargs):
            # Allow initialization with arguments
            super().__init__()

    # Copy all default methods from the interface
    _copy_default_methods(ImplementationClass, (interface,))

    # Mark this class as implementing the interface
    ImplementationClass._implements = {interface}

    return ImplementationClass


def implements(*interfaces: Type[Interface]):
    """
    Create a base class for implementing interfaces.

    This is a compatibility replacement for python-interface.implements
    that works with Python 3.13+.

    Parameters
    ----------
    *interfaces : Type[Interface]
        Interface classes that the decorated class implements.

    Returns
    -------
    Type
        A base class that implements the interfaces.
    """

    # Create a cache key for this combination of interfaces
    cache_key = tuple(sorted(id(iface) for iface in interfaces))

    with _global_lock:
        # Check if we already have a base class for this combination
        if cache_key in _base_class_cache:
            return _base_class_cache[cache_key]

        # Create a base class for inheritance
        class ImplementsBase:
            """Base class for classes that implement interfaces."""

            def __init_subclass__(cls, **kwargs):
                super().__init_subclass__(**kwargs)
                # Store which interfaces this class implements
                if not hasattr(cls, "_implements"):
                    cls._implements = set()
                cls._implements.update(interfaces)

                # Copy default methods from all interfaces to the implementing class
                _copy_default_methods(cls, interfaces)

        # Copy default methods from all interfaces to the base class itself
        _copy_default_methods(ImplementsBase, interfaces)

        # Cache the base class
        _base_class_cache[cache_key] = ImplementsBase

        return ImplementsBase


def implements_decorator(*interfaces: Type[Interface]):
    """
    Decorator to declare that a class implements one or more interfaces.

    This is a compatibility replacement for python-interface.implements
    when used as a decorator.

    Parameters
    ----------
    *interfaces : Type[Interface]
        Interface classes that the decorated class implements.

    Returns
    -------
    Callable[[Type[T]], Type[T]]
        Class decorator function.
    """

    def decorator(cls: Type[T]) -> Type[T]:
        # Store which interfaces this class implements
        if not hasattr(cls, "_implements"):
            cls._implements = set()
        cls._implements.update(interfaces)

        # Copy default methods from interfaces
        _copy_default_methods(cls, interfaces)

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
        try:
            func._is_default_implementation = True
        except AttributeError:
            # Some objects don't allow attribute assignment
            # Create a wrapper function that carries the marker
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            wrapper._is_default_implementation = True
            return wrapper
        return func


# For Python 3.13+ compatibility, we may need to handle inspect module changes
if sys.version_info >= (3, 13):
    import inspect

    # Monkey patch any problematic inspect functionality if needed
    # This would be where we'd add specific fixes for Python 3.13 inspect changes
    pass
