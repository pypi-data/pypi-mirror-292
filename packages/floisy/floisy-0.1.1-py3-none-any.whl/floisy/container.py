import inspect
from typing import Callable, Any, Dict
from functools import lru_cache
import types

class Container:
    def __init__(self):
        self.bindings = {}
        self.instances = {}
        self.context_vars = None
        self.preserve_context = False

    def bind_value(self, abstract: str, value: Any):
        """Bind a value directly."""
        self.bindings[abstract] = lambda: value

    def bind_callable(self, abstract: str, callable_func: Callable):
        """Bind a callable directly."""
        if not callable(callable_func):
            raise Exception(f"'{type(callable_func)}' is not callable")
        self.bindings[abstract] = callable_func

    def singleton(self, abstract: str, concrete: Callable):
        """Bind a singleton instance."""
        if not callable(concrete):
            raise Exception(f"'{type(concrete)}' is not callable")
        if abstract not in self.instances:
            self.instances[abstract] = concrete()
        self.bindings[abstract] = lambda: self.instances[abstract]

    def make(self, abstract: str):
        """Resolve a type from the container."""
        if abstract in self.bindings:
            return self.bindings[abstract]()
        raise Exception(f"No binding found for {abstract}")

    @lru_cache(maxsize=128)
    def get_injectable_params(self, func: Callable) -> Dict[str, str]:
        """Get the injectable parameters for a function."""
        signature = inspect.signature(func)
        return {
            name: param.annotation if param.annotation != inspect._empty else Any
            for name, param in signature.parameters.items()
            if name in self.bindings
        }

    def in_context(self, vars_dict: Dict[str, Any], preserve=False):
        """Set the context for the next call."""
        self.context_vars = vars_dict
        self.preserve_context = preserve
        return self

    def reset_context(self):
        """Reset the context."""
        self.context_vars = None
        self.preserve_context = False

    def call(self, callable_obj: Callable, *args, **kwargs):
        """
        Call a function or instantiate a class, automatically injecting dependencies
        and executing within the current context.
        """
        injectable_params = self.get_injectable_params(callable_obj)
        injected_args = {
            name: self.make(name)
            for name in injectable_params
            if name not in kwargs
        }
        injected_args.update(kwargs)
        vars_dict = self.context_vars or {}

        # if callable_obj is bound method, then we need to add self as a parameter
        if inspect.ismethod(callable_obj):
            injected_args['self'] = callable_obj.__self__

        if inspect.isclass(callable_obj):
            # For classes, we create an instance
            result = callable_obj(*args, **injected_args)
        else:
            # For functions, we create a new function with an updated closure
            new_func = types.FunctionType(
                callable_obj.__code__,
                {**callable_obj.__globals__, **vars_dict},
                callable_obj.__name__,
                callable_obj.__defaults__,
                callable_obj.__closure__
            )
            result = new_func(*args, **injected_args)

        if not self.preserve_context:
            self.reset_context()
        return result

    def __enter__(self):
        """Support for use as a context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Reset context when exiting the context manager."""
        self.reset_context()