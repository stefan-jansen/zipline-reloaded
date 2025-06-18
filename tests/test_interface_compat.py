"""
Test interface compatibility layer for Python 3.13+.

This test ensures that our interface compatibility layer works correctly
and provides the same functionality as the original python-interface package.
"""

import pytest
from zipline.utils.interface import (
    Interface,
    implements,
    default,
    create_implementation,
)


class TestInterfaceCompatibility:
    """Test the interface compatibility layer."""

    def test_basic_interface_creation(self):
        """Test that we can create basic interfaces."""

        class IBasic(Interface):
            def method1(self):
                pass

            def method2(self, arg):
                pass

        # Should not raise any errors
        assert hasattr(IBasic, "_is_interface")
        assert hasattr(IBasic, "_interface_methods")

    def test_implements_decorator(self):
        """Test the implements functionality."""

        class ITest(Interface):
            def required_method(self):
                pass

            @default
            def default_method(self):
                return "default_value"

        class TestClass(implements(ITest)):
            def required_method(self):
                return "implemented"

        obj = TestClass()
        assert obj.required_method() == "implemented"
        assert obj.default_method() == "default_value"

    def test_default_property(self):
        """Test that @default properties work correctly."""

        class IWithProperty(Interface):
            @default
            @property
            def default_prop(self):
                return "default_property_value"

        class TestClass(implements(IWithProperty)):
            pass

        obj = TestClass()
        assert obj.default_prop == "default_property_value"

    def test_create_implementation(self):
        """Test the create_implementation function."""

        class IDomain(Interface):
            @default
            def default_method(self):
                return "domain_default"

        DomainClass = create_implementation(IDomain)
        obj = DomainClass()
        assert obj.default_method() == "domain_default"

    def test_multiple_interfaces(self):
        """Test implementing multiple interfaces."""

        class IInterface1(Interface):
            @default
            def method1(self):
                return "interface1"

        class IInterface2(Interface):
            @default
            def method2(self):
                return "interface2"

        class TestClass(implements(IInterface1, IInterface2)):
            pass

        obj = TestClass()
        assert obj.method1() == "interface1"
        assert obj.method2() == "interface2"

    def test_inheritance_with_interfaces(self):
        """Test that inheritance works correctly with interfaces."""

        class IBase(Interface):
            @default
            def base_method(self):
                return "base"

        class BaseClass(implements(IBase)):
            pass

        class DerivedClass(BaseClass):
            def own_method(self):
                return "derived"

        obj = DerivedClass()
        assert obj.base_method() == "base"
        assert obj.own_method() == "derived"

    def test_thread_safety(self):
        """Test that interface creation is thread-safe."""
        import threading
        import time

        results = []
        errors = []

        def create_interface_class(thread_id):
            try:

                class IThreadTest(Interface):
                    @default
                    def thread_method(self):
                        return f"thread_{thread_id}"

                class ThreadTestClass(implements(IThreadTest)):
                    pass

                obj = ThreadTestClass()
                # Add a small delay to ensure concurrent execution
                time.sleep(0.01)
                results.append(obj.thread_method())
            except Exception as e:
                errors.append(e)

        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_interface_class, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Should have no errors and 5 results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5

        # Each result should be unique (different thread IDs)
        assert len(set(results)) == 5
