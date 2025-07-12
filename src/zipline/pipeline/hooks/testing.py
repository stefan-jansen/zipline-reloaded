from collections import namedtuple

from .iface import PipelineHooks, PIPELINE_HOOKS_CONTEXT_MANAGERS


from zipline.utils.compat import contextmanager, wraps


Call = namedtuple("Call", "method_name args kwargs")


class ContextCall(namedtuple("ContextCall", "state call")):
    @property
    def method_name(self):
        return self.call.method_name

    @property
    def args(self):
        return self.call.args

    @property
    def kwargs(self):
        return self.call.kwargs


def testing_hooks_method(method_name):
    """Factory function for making testing methods."""
    if method_name in PIPELINE_HOOKS_CONTEXT_MANAGERS:
        # Generate a method that enters the context of all sub-hooks.
        @wraps(getattr(PipelineHooks, method_name))
        @contextmanager
        def ctx(self, *args, **kwargs):
            call = Call(method_name, args, kwargs)
            self.trace.append(ContextCall("enter", call))
            yield
            self.trace.append(ContextCall("exit", call))

        return ctx

    else:
        # Generate a method that calls methods of all sub-hooks.
        @wraps(getattr(PipelineHooks, method_name))
        def method(self, *args, **kwargs):
            self.trace.append(Call(method_name, args, kwargs))

        return method


class TestingHooks(PipelineHooks):
    """A hooks implementation that keeps a trace of hook method calls."""

    def __init__(self):
        self.trace = []

    def clear(self):
        self.trace = []

    @contextmanager
    def running_pipeline(self, *args, **kwargs):
        call = Call("running_pipeline", args, kwargs)
        self.trace.append(ContextCall("enter", call))
        yield
        self.trace.append(ContextCall("exit", call))

    @contextmanager
    def computing_chunk(self, *args, **kwargs):
        call = Call("computing_chunk", args, kwargs)
        self.trace.append(ContextCall("enter", call))
        yield
        self.trace.append(ContextCall("exit", call))

    @contextmanager
    def loading_terms(self, *args, **kwargs):
        call = Call("loading_terms", args, kwargs)
        self.trace.append(ContextCall("enter", call))
        yield
        self.trace.append(ContextCall("exit", call))

    @contextmanager
    def computing_term(self, *args, **kwargs):
        call = Call("computing_term", args, kwargs)
        self.trace.append(ContextCall("enter", call))
        yield
        self.trace.append(ContextCall("exit", call))
