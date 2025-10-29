# Plan to Remove python-interface Dependency

## Executive Summary

The `python-interface` library adds complexity without clear benefits over Python's built-in `abc` module. Since the library is unmaintained and incompatible with Python 3.13, removing it would simplify the codebase and resolve the Python 3.13 compatibility issues.

## Current Usage Analysis

### Interfaces in the Codebase

1. **FXRateReader** (`data/fx/base.py`)
   - 3 implementations: ExplodingFXRateReader, HDF5FXRateReader, InMemoryFXRateReader
   - Has default methods: `get_rate_scalar()`, `get_rates_columnar()`

2. **PipelineLoader** (`pipeline/loaders/base.py`)
   - 5+ implementations: DataFrameLoader, EquityPricingLoader, PrecomputedLoader, etc.
   - Has default property: `currency_aware`

3. **IDomain** (`pipeline/domain.py`)
   - Uses special pattern: `Domain = create_implementation(IDomain)`
   - 2 subclasses: GenericDomain, EquityCalendarDomain
   - Has default method: `roll_forward()`

4. **PipelineHooks** (`pipeline/hooks/iface.py`)
   - 4 implementations: NoHooks, ProgressHooks, TestingHooks, DelegatingHooks
   - All methods are context managers

## Conversion Strategy

### Phase 1: Replace with ABC

Convert each interface to use Python's `abc` module:

```python
# Before (python-interface)
from zipline.utils.interface import Interface, implements, default

class FXRateReader(Interface):
    def get_rates(self, rate_names, dts, bases, quotes):
        pass

    @default
    def get_rate_scalar(self, base, quote, dt):
        # default implementation

class HDF5FXRateReader(implements(FXRateReader)):
    def get_rates(self, rate_names, dts, bases, quotes):
        # implementation

# After (abc)
from abc import ABC, abstractmethod

class FXRateReader(ABC):
    @abstractmethod
    def get_rates(self, rate_names, dts, bases, quotes):
        pass

    def get_rate_scalar(self, base, quote, dt):
        # default implementation (no decorator needed)

class HDF5FXRateReader(FXRateReader):
    def get_rates(self, rate_names, dts, bases, quotes):
        # implementation
```

### Phase 2: Handle Special Cases

1. **IDomain Pattern**:
   ```python
   # Before
   Domain = create_implementation(IDomain)

   # After - create concrete base class
   class Domain(IDomain):
       """Base implementation of IDomain interface."""
       pass
   ```

2. **Default Methods**:
   - ABC allows concrete methods in abstract classes
   - Simply remove `@default` decorator

3. **Multiple Interfaces**:
   ```python
   # If needed (rare in this codebase)
   class MyClass(Interface1, Interface2):
       pass
   ```

## Implementation Steps

1. **Create abc_migration branch**
2. **Convert one interface at a time**:
   - Start with simplest (PipelineHooks)
   - Move to FXRateReader
   - Then PipelineLoader
   - Finally IDomain (most complex)
3. **Update imports**:
   - Replace `from zipline.utils.interface import ...`
   - With `from abc import ABC, abstractmethod`
4. **Remove interface modules**:
   - Delete `interface.py` and `interface_compat.py`
   - Remove python-interface from pyproject.toml
5. **Test thoroughly**:
   - Run full test suite
   - Verify Python 3.13 compatibility

## Benefits

1. **Simplification**: Remove 300+ lines of compatibility code
2. **Maintainability**: Use standard Python features
3. **Python 3.13 Support**: Eliminate the root cause of failures
4. **Performance**: Slight improvement from removing abstraction layer
5. **Dependencies**: One less external dependency

## Risks and Mitigations

1. **Risk**: Missing interface validations
   - **Mitigation**: ABC provides similar validation at instantiation time

2. **Risk**: Different error messages
   - **Mitigation**: ABC errors are clear and well-understood by Python developers

3. **Risk**: Breaking changes for extensions
   - **Mitigation**: The change is mostly internal; external API remains the same

## Effort Estimate

- **Development**: 4-6 hours
- **Testing**: 2-3 hours
- **Documentation**: 1 hour
- **Total**: ~1 day of work

## Recommendation

**Proceed with removal**. The benefits far outweigh the risks, and this change would:
- Permanently fix Python 3.13 compatibility
- Simplify the codebase
- Remove an unmaintained dependency
- Use standard Python features that developers understand

The conversion is straightforward since `abc` provides all the features currently used from python-interface.
