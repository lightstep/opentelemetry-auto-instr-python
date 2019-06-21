from __future__ import absolute_import

import functools
from importlib import import_module

from ..internal.packages import (
    marker_passes,
    parse_marker,

    requirement_passes,
    parse_requirement,
)


class require_modules(object):
    """Context manager to check the availability of required modules."""
    def __init__(self, modules):
        self._missing_modules = []
        for module in modules:
            try:
                import_module(module)
            except ImportError:
                self._missing_modules.append(module)

    def __enter__(self):
        return self._missing_modules

    def __exit__(self, exc_type, exc_value, traceback):
        return False


class require_package:
    __slots__ = ('req', )

    def __init__(self, req):
        self.req = parse_requirement(req)

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if requirement_passes(self.req):
                return func(*args, **kwargs)
        return wrapper

    def __enter__(self):
        if requirement_passes(self.req):
            yield

    def __exit__(self, *args, **kwargs):
        pass


class require_marker:
    __slots__ = ('m', )

    def __init__(self, m):
        self.m = parse_marker(m)

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if marker_passes(self.m):
                return func(*args, **kwargs)
        return wrapper

    def __enter__(self):
        if marker_passes(self.m):
            yield

    def __exit__(self, *args, **kwargs):
        pass


def func_name(f):
    """Return a human readable version of the function's name."""
    if hasattr(f, '__module__'):
        return '%s.%s' % (f.__module__, getattr(f, '__name__', f.__class__.__name__))
    return getattr(f, '__name__', f.__class__.__name__)


def module_name(instance):
    """Return the instance module name."""
    return instance.__class__.__module__.split('.')[0]
