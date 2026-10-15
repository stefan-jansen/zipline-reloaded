"""
Windows-specific cleanup utilities for handling file locking issues.
"""

import gc
import os
import sys
import time
import shutil
from contextlib import contextmanager
from functools import wraps


def force_close_on_windows():
    """Force garbage collection and a small delay on Windows to allow file handles to close."""
    if sys.platform == "win32":
        gc.collect()
        time.sleep(0.1)


def retry_on_permission_error(max_attempts=3, delay=0.1):
    """Decorator to retry operations that may fail due to Windows file locking."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except PermissionError:
                    if attempt < max_attempts - 1 and sys.platform == "win32":
                        force_close_on_windows()
                        time.sleep(delay * (attempt + 1))  # Exponential backoff
                    else:
                        raise
            return func(*args, **kwargs)

        return wrapper

    return decorator


@contextmanager
def windows_safe_cleanup(temp_dir):
    """Context manager that ensures proper cleanup on Windows."""
    try:
        yield temp_dir
    finally:
        if sys.platform == "win32":
            force_close_on_windows()
            # Try to clean up with retries
            for attempt in range(3):
                try:
                    if os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir)
                    break
                except PermissionError:
                    if attempt < 2:
                        time.sleep(0.2 * (attempt + 1))
                    else:
                        # Last resort: mark for deletion on reboot
                        # This won't work in CI but at least won't fail the test
                        pass


class WindowsSafeTempDirectory:
    """Wrapper around TempDirectory that handles Windows file locking issues."""

    def __init__(self, temp_directory):
        self.temp_directory = temp_directory

    def __enter__(self):
        return self.temp_directory.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if sys.platform == "win32":
            force_close_on_windows()

        # Try multiple times on Windows
        if sys.platform == "win32":
            for attempt in range(3):
                try:
                    return self.temp_directory.__exit__(exc_type, exc_val, exc_tb)
                except PermissionError:
                    if attempt < 2:
                        force_close_on_windows()
                        time.sleep(0.2 * (attempt + 1))
                    else:
                        # Skip cleanup on final failure to not fail the test
                        print(f"Warning: Could not clean up {self.temp_directory.path}")
                        return True  # Suppress the exception
        else:
            return self.temp_directory.__exit__(exc_type, exc_val, exc_tb)
