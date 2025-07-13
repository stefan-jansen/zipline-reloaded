# CI Test Fixes Applied

This document summarizes the fixes applied to resolve CI test failures across all platforms.

## Issues Fixed

### 1. DataFrame Attribute Access Error
**Error**: `AttributeError: 'DataFrame' object has no attribute 'exchange'`
**Location**: `tests/pipeline/test_international_markets.py:230`
**Fix**: Changed `cls.EXCHANGE_INFO.exchange` to `cls.EXCHANGE_INFO['exchange']`
**Impact**: Resolved test failures across all platforms

### 2. Pandas future_stack Parameter Compatibility
**Error**: `TypeError: DataFrame.stack() got an unexpected keyword argument 'future_stack'`
**Locations**: Multiple files using `.stack(future_stack=True)`
**Fix**:
- Added `stack_future_compatible()` function in `src/zipline/utils/pandas_utils.py`
- Function detects pandas version and only passes `future_stack` parameter for pandas >= 2.1.0
- Updated all affected files to use the compatibility wrapper
**Files Modified**:
- `src/zipline/utils/pandas_utils.py` (added compatibility function)
- `tests/pipeline/test_international_markets.py`
- `src/zipline/pipeline/loaders/earnings_estimates.py`
- `src/zipline/_protocol.pyx`
- `tests/pipeline/test_quarters_estimates.py`
**Impact**: Ensures compatibility across pandas versions 1.3.0 to 3.0

### 3. Windows File Locking Issues
**Error**: `PermissionError: [WinError 32] The process cannot access the file because it is being used by another process`
**Locations**: Bundle tests (test_ingest, test_ingest_assets_versions)
**Fix**:
- Added `close()` method to `AssetFinder` class
- Transformed `BundleData` from namedtuple to proper class with resource cleanup
- Added context manager support (`__enter__`/`__exit__`) to BundleData
- Updated tests to use context managers and proper engine disposal
**Files Modified**:
- `src/zipline/assets/assets.py` (added close() method)
- `src/zipline/data/bundles/core.py` (added BundleData class with cleanup)
- `tests/data/bundles/test_core.py` (updated tests to use context managers)
**Impact**: Resolved Windows-specific file locking errors in bundle tests

## Verification

After applying these fixes:
- DataFrame attribute access errors are resolved
- Pandas compatibility is maintained across versions
- Windows file locking issues are fixed
- All platforms (Ubuntu, macOS, Windows) should have clean CI runs

## Related Documentation
- See `CI_FIXES_SUMMARY.md` for additional CI workarounds (coverage bug, Python 3.13)
- See `WINDOWS_FILE_LOCKING_FIX.md` for detailed explanation of the Windows fix
