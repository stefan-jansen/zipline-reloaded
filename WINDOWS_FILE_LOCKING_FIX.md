# Windows File Locking Fix Summary

## Problem
Bundle tests on Windows were failing with `PermissionError: [WinError 32] The process cannot access the file because it is being used by another process`. This was happening because SQLite database connections and file handles were not being properly closed.

## Root Causes
1. `AssetFinder` class was creating SQLAlchemy engines from string paths but had no `close()` method to dispose of them
2. `SQLiteAdjustmentReader` already had a `close()` method but it wasn't being called in tests
3. Tests were creating SQLAlchemy engines directly without disposing of them
4. The `BundleData` namedtuple didn't provide any resource cleanup mechanism

## Changes Made

### 1. Added close() method to AssetFinder (src/zipline/assets/assets.py)
- Track whether the engine was created from a string path
- Add `close()` method that disposes the engine if it was created from a string

### 2. Created BundleData wrapper class (src/zipline/data/bundles/core.py)
- Changed `BundleData` from a namedtuple to a class that inherits from a namedtuple
- Added `close()` method to close AssetFinder and SQLiteAdjustmentReader
- Added context manager support (`__enter__` and `__exit__`) for automatic cleanup

### 3. Updated test_ingest to use context manager (tests/data/bundles/test_core.py)
- Changed the test to use `with self.load(...) as bundle:` pattern
- This ensures resources are automatically closed when the test completes

### 4. Fixed test_ingest_assets_versions engine disposal (tests/data/bundles/test_core.py)
- Wrapped engine usage in try/finally block
- Added `eng.dispose()` in finally block to ensure connections are closed

## Testing
These changes ensure that:
- All SQLite connections are properly closed after use
- File handles are released on Windows
- Tests can run without file locking errors
- The fix is backward compatible (existing code continues to work)

## Best Practices Going Forward
1. Always use BundleData as a context manager when possible: `with load(...) as bundle:`
2. Always dispose SQLAlchemy engines created for testing: `eng.dispose()`
3. Consider adding `__enter__` and `__exit__` methods to classes that manage resources
